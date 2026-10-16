"""CLI commands for RatTeil application."""

import sys
from pathlib import Path
from typing import List, Optional, Tuple

from ratteil.config import get_settings, reset_settings
from ratteil.utils.logging import setup_logging, get_logger
from ratteil.repositories.surah_repository import LocalSurahRepository
from ratteil.repositories.reciter_repository import LocalReciterRepository
from ratteil.services.randomizer_service import RandomizerService
from ratteil.services.download_service import DownloadService
from ratteil.services.stream_service import StreamService
from ratteil.services.youtube_service import YouTubeService, AuthMode
from ratteil.services.audio_service import AudioService


logger = get_logger(__name__)


def parse_surah_list(surah_input: str) -> List[int]:
    """Parse a surah input string to a list of surah IDs.
    
    Args:
        surah_input: String like "1,2,3" or "1-10" or "1,2-5,10"
        
    Returns:
        List of surah IDs
    """
    surahs = []
    
    for part in surah_input.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            start = int(start.strip())
            end = int(end.strip())
            surahs.extend(range(start, end + 1))
        else:
            surahs.append(int(part))
    
    return list(set(surahs))  # Remove duplicates


def parse_reciter_list(reciter_input: str) -> List[str]:
    """Parse a reciter input string to a list of reciter IDs.
    
    Args:
        reciter_input: Comma-separated string of reciter IDs
        
    Returns:
        List of reciter IDs
    """
    return [r.strip() for r in reciter_input.split(',') if r.strip()]


def run_ratteil(args) -> int:
    """Run the RatTeil application based on parsed arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Configure settings
    if args.config:
        # Custom config file can be handled by Pydantic
        pass
    
    settings = get_settings()
    
    # Set up logging
    if args.debug:
        setup_logging(log_level='DEBUG')
    else:
        setup_logging()
    
    logger.info(f"Starting RatTeil v{settings.APP_VERSION}")
    
    # Handle YouTube auth mode from args
    youtube_auth_mode = getattr(args, 'youtube_auth', 'device_flow')
    
    # Handle commands
    if args.command == 'download':
        return handle_download(args)
    elif args.command == 'stream':
        return handle_stream(args, youtube_auth_mode)
    elif args.command == 'list':
        return handle_list(args)
    elif args.command == 'prepare':
        return handle_prepare(args)
    elif args.command == 'validate':
        return handle_validate(args)
    elif args.command == 'youtube-auth-test':
        return handle_youtube_auth_test(args)
    else:
        # Default behavior (backward compatibility)
        return handle_default(args, youtube_auth_mode)


def handle_download(args) -> int:
    """Handle download command."""
    logger.info("Starting download operation")
    
    download_service = DownloadService()
    surah_repo = LocalSurahRepository()
    reciter_repo = LocalReciterRepository()
    
    # Determine which surahs to download
    if args.all:
        surahs = surah_repo.get_all()
    elif args.surahs:
        surah_ids = parse_surah_list(args.surahs)
        surahs = [surah_repo.get_by_id(sid) for sid in surah_ids]
        surahs = [s for s in surahs if s is not None]
    else:
        logger.error("No surahs specified for download")
        return 1
    
    # Determine which reciters to use
    if args.reciters:
        reciter_ids = parse_reciter_list(args.reciters)
        reciters = [reciter_repo.get_by_id(rid) for rid in reciter_ids]
        reciters = [r for r in reciters if r is not None]
    else:
        # Use all reciters
        reciters = reciter_repo.get_all()
    
    if not reciters:
        logger.error("No reciters available")
        return 1
    
    # Download for each reciter
    for reciter in reciters:
        logger.info(f"Downloading for reciter: {reciter.name}")
        download_service.download_batch(
            surahs,
            reciter,
            output_dir=Path(args.output_dir) if args.output_dir else None,
        )
    
    logger.info("Download completed")
    return 0


def handle_stream(args, youtube_auth_mode: str = 'device_flow') -> int:
    """Handle stream command."""
    logger.info("Starting stream operation")
    
    randomizer = RandomizerService()
    stream_service = StreamService()
    
    # Determine surahs
    if args.surahs:
        surah_ids = parse_surah_list(args.surahs)
        surah_repo = LocalSurahRepository()
        surahs = [surah_repo.get_by_id(sid) for sid in surah_ids]
        surahs = [s for s in surahs if s is not None]
    elif args.random or (args.surahs_count or args.reciters_count):
        count = args.surahs_count or get_settings().MAX_SURAHS
        surahs = randomizer.generate_random_surahs_list(count)
    else:
        # Default: use all surahs
        surah_repo = LocalSurahRepository()
        surahs = surah_repo.get_all()
    
    # Determine reciters
    if args.reciters:
        reciter_ids = parse_reciter_list(args.reciters)
        reciter_repo = LocalReciterRepository()
        reciters = [reciter_repo.get_by_id(rid) for rid in reciter_ids]
        reciters = [r for r in reciters if r is not None]
    elif args.random or (args.surahs_count or args.reciters_count):
        count = args.reciters_count or get_settings().MAX_RECITERS
        reciters = randomizer.generate_random_reciters_list(count)
    else:
        # Default: use all reciters
        reciter_repo = LocalReciterRepository()
        reciters = reciter_repo.get_all()
    
    if not surahs or not reciters:
        logger.error("No surahs or reciters available for streaming")
        return 1
    
    # Generate stream details
    stream_details = stream_service.generate_stream_details(
        surahs,
        reciters,
        title=args.title,
        description=args.description,
    )
    
    # Validate
    try:
        stream_service.stream_validation(stream_details)
    except Exception as e:
        logger.error(f"Stream validation failed: {e}")
        return 1
    
    # Prepare files
    if not args.no_merge:
        prepared_files = stream_service.prepare_stream_files(stream_details)
        logger.info(f"Prepared {len(prepared_files)} files for streaming")
    
    # Stream
    if args.youtube:
        return handle_youtube_stream(stream_details, youtube_auth_mode)
    else:
        # Local streaming (simulated)
        def on_progress(stream_file, current, total):
            logger.info(
                f"Streaming {current}/{total}: "
                f"Surah {stream_file.surah_id} by {stream_file.reciter_id}"
            )
        
        stream_service.stream(stream_details, on_progress=on_progress)
        logger.info("Stream completed")
    
    return 0


def handle_youtube_stream(stream_details, youtube_auth_mode: str = 'device_flow') -> int:
    """Handle YouTube streaming."""
    logger.info("Starting YouTube stream")
    
    youtube_service = YouTubeService(auth_mode=youtube_auth_mode)
    
    try:
        stream_id, broadcast_id, rtmp_url = youtube_service.create_and_start_stream(
            stream_details
        )
        logger.info(f"YouTube stream created: {rtmp_url}")
        logger.info(f"Broadcast ID: {broadcast_id}")
        logger.info(f"Stream ID: {stream_id}")
        
        # Here you would use FFmpeg to stream to the RTMP URL
        logger.info("Ready to stream to YouTube (RTMP endpoint configured)")
        
        return 0
    except Exception as e:
        logger.error(f"Failed to create YouTube stream: {e}")
        return 1


def handle_list(args) -> int:
    """Handle list command."""
    if args.reciters:
        reciter_repo = LocalReciterRepository()
        reciters = reciter_repo.get_all()
        print("\nAvailable Reciters:")
        print("-" * 50)
        for reciter in reciters:
            print(f"  {reciter.id:20} - {reciter.name}")
            for moshaf in reciter.moshafs:
                print(f"    {moshaf.name:20} - {moshaf.url}")
        print(f"\nTotal: {len(reciters)} reciters")
    
    elif args.surahs:
        surah_repo = LocalSurahRepository()
        surahs = surah_repo.get_all()
        print("\nAvailable Surahs:")
        print("-" * 50)
        for surah in surahs:
            print(f"  {surah.id:3} - {surah.name:25} ({surah.arabic_name}) - {surah.verses_count} verses")
        print(f"\nTotal: {len(surahs)} surahs")
    
    elif args.reciters_with_multiple_moshafs:
        reciter_repo = LocalReciterRepository()
        reciters = reciter_repo.get_with_multiple_moshafs()
        print("\nReciters with Multiple Moshafs:")
        print("-" * 50)
        for reciter in reciters:
            print(f"  {reciter.id:20} - {reciter.name} ({len(reciter.moshafs)} moshafs)")
        print(f"\nTotal: {len(reciters)} reciters")
    
    else:
        # List both
        args.reciters = True
        handle_list(args)
        print("\n")
        args.reciters = False
        args.surahs = True
        handle_list(args)
    
    return 0


def handle_prepare(args) -> int:
    """Handle prepare command."""
    logger.info("Preparing stream files")
    
    randomizer = RandomizerService()
    stream_service = StreamService()
    
    # Determine surahs
    if args.surahs:
        surah_ids = parse_surah_list(args.surahs)
        surah_repo = LocalSurahRepository()
        surahs = [surah_repo.get_by_id(sid) for sid in surah_ids]
        surahs = [s for s in surahs if s is not None]
    else:
        surah_repo = LocalSurahRepository()
        surahs = surah_repo.get_all()
    
    # Determine reciters
    if args.reciters:
        reciter_ids = parse_reciter_list(args.reciters)
        reciter_repo = LocalReciterRepository()
        reciters = [reciter_repo.get_by_id(rid) for rid in reciter_ids]
        reciters = [r for r in reciters if r is not None]
    else:
        reciter_repo = LocalReciterRepository()
        reciters = reciter_repo.get_all()
    
    # Generate stream details
    stream_details = stream_service.generate_stream_details(
        surahs,
        reciters,
    )
    
    # Prepare files
    output_dir = Path(args.output_dir) if args.output_dir else None
    prepared_files = stream_service.prepare_stream_files(
        stream_details,
        output_dir=output_dir,
    )
    
    logger.info(f"Prepared {len(prepared_files)} files in {output_dir or get_settings().STREAM_DIR}")
    
    # Save stream details
    stream_service.save_stream_details(stream_details)
    logger.info(f"Stream details saved")
    
    return 0


def handle_validate(args) -> int:
    """Handle validate command."""
    logger.info("Validating stream configuration")
    
    stream_service = StreamService()
    randomizer = RandomizerService()
    
    # Determine surahs
    if args.surahs:
        surah_ids = parse_surah_list(args.surahs)
        surah_repo = LocalSurahRepository()
        surahs = [surah_repo.get_by_id(sid) for sid in surah_ids]
        surahs = [s for s in surahs if s is not None]
    else:
        surah_repo = LocalSurahRepository()
        surahs = surah_repo.get_all()
    
    # Determine reciters
    if args.reciters:
        reciter_ids = parse_reciter_list(args.reciters)
        reciter_repo = LocalReciterRepository()
        reciters = [reciter_repo.get_by_id(rid) for rid in reciter_ids]
        reciters = [r for r in reciters if r is not None]
    else:
        reciter_repo = LocalReciterRepository()
        reciters = reciter_repo.get_all()
    
    # Generate stream details
    stream_details = stream_service.generate_stream_details(
        surahs,
        reciters,
    )
    
    # Validate
    try:
        stream_service.stream_validation(stream_details)
        logger.info("Stream configuration is valid")
        print("\nValidation Results:")
        print(f"  Surahs: {len(stream_details.stream_files)}")
        print(f"  Total Duration: {stream_details.total_duration:.2f}s")
        print(f"  Status: Valid")
        return 0
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


def handle_youtube_auth_test(args) -> int:
    """Handle YouTube authentication test command."""
    logger.info("Testing YouTube authentication")
    
    auth_mode = getattr(args, 'mode', 'device_flow')
    youtube_service = YouTubeService(auth_mode=auth_mode)
    
    print(f"\nTesting authentication mode: {auth_mode}")
    print("-" * 50)
    
    try:
        success = youtube_service.test_authentication()
        if success:
            print("✅ Authentication successful!")
            logger.info("YouTube authentication test passed")
            return 0
        else:
            print("❌ Authentication failed!")
            logger.error("YouTube authentication test failed")
            return 1
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        logger.error(f"YouTube authentication test failed: {e}")
        return 1


def handle_default(args, youtube_auth_mode: str = 'device_flow') -> int:
    """Handle default behavior (backward compatibility)."""
    logger.info("Running in default mode")
    
    # This mimics the original behavior
    randomizer = RandomizerService()
    stream_service = StreamService()
    
    # Generate random selection
    surahs = randomizer.generate_random_surahs_list()
    reciters = randomizer.generate_random_reciters_list()
    
    logger.info(f"Selected {len(surahs)} surahs and {len(reciters)} reciters")
    
    # Generate stream details
    stream_details = stream_service.generate_stream_details(
        surahs,
        reciters,
    )
    
    # Validate
    try:
        stream_service.stream_validation(stream_details)
    except Exception as e:
        logger.error(f"Stream validation failed: {e}")
        return 1
    
    # Prepare files
    prepared_files = stream_service.prepare_stream_files(stream_details)
    logger.info(f"Prepared {len(prepared_files)} files")
    
    # Stream
    def on_progress(stream_file, current, total):
        logger.info(
            f"Streaming {current}/{total}: "
            f"Surah {stream_file.surah_id} by {stream_file.reciter_id}"
        )
    
    stream_service.stream(stream_details, on_progress=on_progress)
    
    return 0
