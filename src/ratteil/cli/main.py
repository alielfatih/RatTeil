"""
Main CLI entry point for RatTeil application.

This module provides the main entry point and subcommand handling.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from ratteil.config.settings import get_settings
from ratteil.config.exceptions import RatTeilError
from ratteil.utils.logging import get_logger


logger = get_logger("ratteil.cli")


def create_main_parser() -> argparse.ArgumentParser:
    """
    Create the main parser with subcommands.
    
    Returns:
        Configured ArgumentParser with subcommands
    """
    parser = argparse.ArgumentParser(
        prog="ratteil",
        description="RatTeil - Quran Recitation Streaming Tool",
        epilog="""
RatTeil streams Quran recitations to YouTube and Facebook.
Use subcommands for specific operations or run without arguments for interactive mode.

Examples:
  ratteil stream -p youtube -r alafasy -s 1-5
  ratteil download -r alafasy --surahs 10
  ratteil list reciters
  ratteil auth youtube
  ratteil config show
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "-d", "--dev",
        action="store_true",
        help="Enable development mode"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        description="Use these commands to perform specific operations"
    )
    
    # Stream subcommand
    stream_parser = subparsers.add_parser(
        "stream",
        help="Stream Quran recitations",
        description="Stream Quran recitations to YouTube or Facebook"
    )
    stream_parser.add_argument(
        "-p", "--platform",
        metavar="PLATFORM",
        help="Platform(s) to stream to (youtube, facebook)",
        dest="sites",
        choices=["youtube", "yt", "fb", "facebook"],
        nargs="*",
        required=True
    )
    stream_parser.add_argument(
        "-R", "--reciter",
        metavar="CODE",
        help="Reciter code(s) to use (e.g., alafasy, husary)",
        dest="reciter",
        nargs="*"
    )
    stream_parser.add_argument(
        "-s", "--surah",
        metavar="INDEX",
        type=int,
        choices=list(range(1, 115)),
        help="Specific surah to stream (1-114)"
    )
    stream_parser.add_argument(
        "-n", "--surahs",
        metavar="COUNT",
        type=int,
        help="Number of surahs per stream (default: 30)",
        default=30
    )
    stream_parser.add_argument(
        "-q", "--qaris",
        metavar="COUNT",
        type=int,
        help="Number of reciters per stream (default: 5)",
        default=5
    )
    stream_parser.add_argument(
        "--max-length",
        metavar="MINUTES",
        type=float,
        help="Maximum stream length in minutes (default: 75.0)",
        default=75.0
    )
    stream_parser.add_argument(
        "--min-length",
        metavar="MINUTES",
        type=float,
        help="Minimum stream length in minutes (default: 120.0)",
        default=120.0
    )
    stream_parser.add_argument(
        "--no-download",
        action="store_true",
        help="Use existing files, don't download new ones"
    )
    stream_parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip minimum stream length validation"
    )
    stream_parser.add_argument(
        "-t", "--title",
        metavar="TITLE",
        help="Custom stream title"
    )
    stream_parser.add_argument(
        "-D", "--description",
        metavar="DESC",
        help="Custom stream description"
    )
    
    # Download subcommand
    download_parser = subparsers.add_parser(
        "download",
        help="Download Quran audio",
        description="Download Quran audio from various reciters"
    )
    download_parser.add_argument(
        "-R", "--reciter",
        metavar="CODE",
        help="Reciter code(s) to download from (e.g., alafasy, husary)",
        dest="reciter",
        nargs="*",
        required=True
    )
    download_parser.add_argument(
        "-s", "--surah",
        metavar="INDEX",
        type=int,
        choices=list(range(1, 115)),
        help="Specific surah to download (1-114)"
    )
    download_parser.add_argument(
        "-n", "--surahs",
        metavar="COUNT",
        type=int,
        help="Number of surahs to download (default: 10)",
        default=10
    )
    download_parser.add_argument(
        "-o", "--output",
        metavar="DIR",
        help="Output directory for downloads",
        default=None
    )
    download_parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Download all available surahs"
    )
    
    # List subcommand
    list_parser = subparsers.add_parser(
        "list",
        help="List available resources",
        description="List available reciters, surahs, or other resources"
    )
    list_parser.add_argument(
        "resource",
        metavar="RESOURCE",
        help="Resource type to list",
        choices=["reciters", "surahs", "all"],
        nargs="?",
        default="reciters"
    )
    list_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed information"
    )
    
    # Auth subcommand
    auth_parser = subparsers.add_parser(
        "auth",
        help="Manage authentication",
        description="Authenticate with YouTube or Facebook"
    )
    auth_parser.add_argument(
        "provider",
        metavar="PROVIDER",
        help="Authentication provider",
        choices=["youtube", "facebook", "all"],
        nargs="?",
        default="all"
    )
    auth_parser.add_argument(
        "--revoke",
        action="store_true",
        help="Revoke existing token"
    )
    auth_parser.add_argument(
        "--check",
        action="store_true",
        help="Check authentication status"
    )
    
    # Prepare subcommand
    prepare_parser = subparsers.add_parser(
        "prepare",
        help="Prepare stream files",
        description="Prepare audio files for streaming without actually streaming"
    )
    prepare_parser.add_argument(
        "-R", "--reciter",
        metavar="CODE",
        help="Reciter code(s) to use (e.g., alafasy, husary)",
        dest="reciter",
        nargs="*"
    )
    prepare_parser.add_argument(
        "-s", "--surah",
        metavar="INDEX",
        type=int,
        choices=list(range(1, 115)),
        help="Specific surah to prepare (1-114)"
    )
    prepare_parser.add_argument(
        "-n", "--surahs",
        metavar="COUNT",
        type=int,
        help="Number of surahs to prepare (default: 30)",
        default=30
    )
    prepare_parser.add_argument(
        "--max-length",
        metavar="MINUTES",
        type=float,
        help="Maximum stream length in minutes (default: 75.0)",
        default=75.0
    )
    
    # Validate subcommand
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate stream configuration",
        description="Validate stream configuration and audio files"
    )
    validate_parser.add_argument(
        "-R", "--reciter",
        metavar="CODE",
        help="Reciter code(s) to validate",
        dest="reciter",
        nargs="*"
    )
    validate_parser.add_argument(
        "-m", "--min-length",
        metavar="MINUTES",
        type=float,
        help="Minimum stream length to validate (default: 120.0)",
        default=120.0
    )
    
    # Config subcommand
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration",
        description="View or modify application configuration"
    )
    config_parser.add_argument(
        "action",
        metavar="ACTION",
        help="Configuration action",
        choices=["show", "set", "get"],
        nargs="?",
        default="show"
    )
    config_parser.add_argument(
        "key",
        metavar="KEY",
        help="Configuration key to set or get",
        nargs="?"
    )
    config_parser.add_argument(
        "value",
        metavar="VALUE",
        help="Value to set",
        nargs="?"
    )
    
    # Copyright subcommand
    copyright_parser = subparsers.add_parser(
        "copyright",
        help="Show copyright information",
        description="Display the application license"
    )
    
    return parser


def handle_stream_command(args: argparse.Namespace) -> int:
    """
    Handle the stream command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    from ratteil.cli.commands import pre_launcher
    from ratteil.data.data_manager import QuranDataManager
    from ratteil.config.settings import get_settings
    
    settings = get_settings()
    if args.verbose:
        settings.debug = True
    
    # Set up paths
    resources_path = settings.data_dir
    package_path = Path(__file__).resolve().parent.parent
    
    # Try to use API method first
    try:
        data_manager = QuranDataManager(
            language=settings.data_language,
            offline=settings.data_offline
        )
        
        # Convert API reciters to old format for compatibility
        recitersDB = {}
        recitersCodesDB = []
        
        for reciter in data_manager.get_reciters():
            code = reciter.code
            recitersCodesDB.append(code)
            recitersDB[code] = {
                "id": reciter.id,
                "name": reciter.name,
                "letter": reciter.letter or "",
                "moshaf": reciter.moshafs or []
            }
        
        logger.debug(f"Using API data: {len(recitersCodesDB)} reciters loaded")
        
    except Exception as api_error:
        logger.warning(f"API method failed, falling back to static data: {api_error}")
        # Fallback to old static method
        from ratteil.reciters import reciters_code as recitersCodesDB, reciters as recitersDB
    
    # Convert args to options-like object
    class Options:
        pass
    options = Options()
    options.sites = args.sites or []
    options.reciter = args.reciter or []
    options.surah = args.surah
    options.surahs_number = args.surahs
    options.reciters_number = args.qaris
    options.max_len = args.max_length
    options.minimum_stream_length = args.min_length
    options.no_download = args.no_download
    options.no_validation = args.skip_validation
    options.dev = args.dev
    
    try:
        pre_launcher(
            options,
            recitersDB,
            recitersCodesDB,
            resources_path,
            package_path
        )
        return 0
    except Exception as e:
        logger.error(f"Stream command failed: {e}")
        return 1


def handle_download_command(args: argparse.Namespace) -> int:
    """
    Handle the download command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    from ratteil.services.download_service import DownloadService
    from ratteil.services.randomizer_service import RandomizerService
    from ratteil.data.data_manager import QuranDataManager
    from ratteil.config.settings import get_settings
    from pathlib import Path
    
    settings = get_settings()
    if args.verbose:
        settings.debug = True
    
    resources_path = settings.data_dir
    download_path = resources_path / "audios"
    download_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Try to use API method first
        try:
            data_manager = QuranDataManager(
                language=settings.data_language,
                offline=settings.data_offline
            )
            
            # Convert API reciters to old format for compatibility
            recitersDB = {}
            recitersCodesDB = []
            
            for reciter in data_manager.get_reciters():
                code = reciter.code
                recitersCodesDB.append(code)
                recitersDB[code] = {
                    "id": reciter.id,
                    "name": reciter.name,
                    "letter": reciter.letter or "",
                    "moshaf": reciter.moshafs or []
                }
            
            logger.debug(f"Using API data: {len(recitersCodesDB)} reciters loaded")
            
        except Exception as api_error:
            logger.warning(f"API method failed, falling back to static data: {api_error}")
            # Fallback to old static method
            from ratteil.reciters import reciters_code as recitersCodesDB, reciters as recitersDB
        
        # Generate surahs list
        if args.all:
            # Download all surahs from selected reciters
            for reciter_code in args.reciter:
                reciter = recitersDB.get(reciter_code, {})
                moshafs = reciter.get("moshaf", [])
                if moshafs:
                    selected_moshaf = moshafs[0]
                    surah_list_str = selected_moshaf.get("surah_list", "")
                    surah_indices = surah_list_str.split(",") if surah_list_str else []
                    
                    for surah_idx in surah_indices:
                        surah_idx = int(surah_idx)
                        from ratteil.models.surah import SurahInfo
                        surah = SurahInfo(surah_idx, reciter_code, 1, recitersDB)
                        url = f"{surah.url}{surah_idx:03d}.mp3"
                        output_path = download_path / surah.dl_name
                        
                        import subprocess
                        subprocess.run(["wget", url, "-O", str(output_path)], check=True)
                        logger.info(f"Downloaded: {surah.dl_name}")
        else:
            # Download specific number of surahs
            _, selected_surahs_list = RandomizerService.generate_random_reciters_list(
                1, args.reciter, recitersDB
            )
            stream_surahs_list = RandomizerService.generate_random_surahs_list(
                args.surahs, args.surah, selected_surahs_list
            )
            
            download_service = DownloadService()
            download_service.download_audios(
                settings.max_stream_length,
                stream_surahs_list,
                recitersDB,
                resources_path
            )
        
        logger.info(f"Downloaded {len(list(download_path.glob('*.mp3')))} audio files")
        return 0
    except Exception as e:
        logger.error(f"Download command failed: {e}")
        return 1


def handle_list_command(args: argparse.Namespace) -> int:
    """
    Handle the list command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    from ratteil.data.data_manager import QuranDataManager
    from ratteil.config.settings import get_settings
    
    settings = get_settings()
    resources_path = settings.data_dir
    package_path = Path(__file__).resolve().parent.parent
    
    try:
        # Use new data manager with API support
        data_manager = QuranDataManager(
            language=settings.data_language,
            offline=settings.data_offline
        )
        
        if args.resource in ["reciters", "all"]:
            print("\nAvailable Reciters (API):")
            reciters = data_manager.get_reciters()
            for reciter in reciters:
                print(f"  code: {reciter.code}\tname: {reciter.name}")
        
        if args.resource in ["surahs", "all"]:
            print("\nAvailable Surahs (API):")
            surahs = data_manager.get_surahs()
            for surah in surahs:
                print(f"  {surah.id:3d}. {surah.name}")
        
        if args.resource == "languages":
            print("\nAvailable Languages (API):")
            languages = data_manager.get_languages()
            for lang in languages:
                print(f"  {lang.code}: {lang.name} ({lang.native_name})")
        
        return 0
    except Exception as e:
        logger.warning(f"API method failed: {e}")
        # Fallback to old method if API fails
        try:
            from ratteil.cli.commands import handle_reciters_list
            from ratteil.reciters import reciters_code as recitersCodesDB, reciters as recitersDB
            
            if args.resource in ["reciters", "all"]:
                print("\nAvailable Reciters (Static):")
                handle_reciters_list(
                    recitersDB,
                    recitersCodesDB,
                    resources_path,
                    package_path,
                    use_api=False  # Use static data
                )
            
            if args.resource in ["surahs", "all"]:
                from ratteil.surahs import surah_list
                print("\nAvailable Surahs (Static):")
                for i in range(1, 115):
                    surah_key = f"surah_{i}"
                    surah_name = surah_list.get(surah_key, {}).get("name", f"Surah {i}")
                    print(f"  {i:3d}. {surah_name}")
            
            return 0
        except Exception as fallback_e:
            logger.error(f"Fallback list command also failed: {fallback_e}")
            return 1


def handle_auth_command(args: argparse.Namespace) -> int:
    """
    Handle the auth command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    from ratteil.auth.google_auth import GoogleAuthService, YouTubeAuthService
    from ratteil.auth.facebook_auth import FacebookAuthService
    from ratteil.config.settings import get_settings
    
    settings = get_settings()
    
    try:
        if args.check:
            # Check authentication status
            if args.provider in ["youtube", "all"]:
                youtube_auth = YouTubeAuthService(settings)
                print(f"YouTube: {'Authenticated' if youtube_auth.is_authenticated() else 'Not authenticated'}")
            
            if args.provider in ["facebook", "all"]:
                fb_auth = FacebookAuthService(settings)
                print(f"Facebook: {'Authenticated' if fb_auth.is_authenticated() else 'Not authenticated'}")
            
            return 0
        
        if args.revoke:
            # Revoke tokens
            if args.provider in ["youtube", "all"]:
                youtube_auth = YouTubeAuthService(settings)
                youtube_auth.revoke_token()
                print("YouTube token revoked")
            
            if args.provider in ["facebook", "all"]:
                fb_auth = FacebookAuthService(settings)
                fb_auth.revoke_token()
                print("Facebook token revoked")
            
            return 0
        
        # Authenticate
        if args.provider in ["youtube", "all"]:
            youtube_auth = YouTubeAuthService(settings)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                token = loop.run_until_complete(youtube_auth.authenticate())
                print(f"YouTube authentication successful! Token expires: {token.expires_at}")
            finally:
                loop.close()
        
        if args.provider in ["facebook", "all"]:
            fb_auth = FacebookAuthService(settings)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                token = loop.run_until_complete(fb_auth.authenticate())
                print(f"Facebook authentication successful!")
            finally:
                loop.close()
        
        return 0
    except Exception as e:
        logger.error(f"Auth command failed: {e}")
        return 1


def handle_prepare_command(args: argparse.Namespace) -> int:
    """
    Handle the prepare command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    from ratteil.services.stream_service import StreamService
    from ratteil.services.randomizer_service import RandomizerService
    from ratteil.data.data_manager import QuranDataManager
    from ratteil.config.settings import get_settings
    from pathlib import Path
    
    settings = get_settings()
    if args.verbose:
        settings.debug = True
    
    resources_path = settings.data_dir
    package_path = Path(__file__).resolve().parent.parent
    
    try:
        # Try to use API method first
        try:
            data_manager = QuranDataManager(
                language=settings.data_language,
                offline=settings.data_offline
            )
            
            # Convert API reciters to old format for compatibility
            recitersDB = {}
            recitersCodesDB = []
            
            for reciter in data_manager.get_reciters():
                code = reciter.code
                recitersCodesDB.append(code)
                recitersDB[code] = {
                    "id": reciter.id,
                    "name": reciter.name,
                    "letter": reciter.letter or "",
                    "moshaf": reciter.moshafs or []
                }
            
            logger.debug(f"Using API data: {len(recitersCodesDB)} reciters loaded")
            
        except Exception as api_error:
            logger.warning(f"API method failed, falling back to static data: {api_error}")
            # Fallback to old static method
            from ratteil.reciters import reciters_code as recitersCodesDB, reciters as recitersDB
        
        stream_service = StreamService(
            recitersDB,
            resources_path,
            package_path,
            settings
        )
        
        temp_reciters_list = args.reciter or recitersCodesDB
        
        _, selected_surahs_list = RandomizerService.generate_random_reciters_list(
            args.qaris or 5, temp_reciters_list, recitersDB
        )
        stream_surahs_list = RandomizerService.generate_random_surahs_list(
            args.surahs, args.surah, selected_surahs_list
        )
        
        # Prepare stream files
        stream_files = [str(resources_path / "audios" / s.split("/")[-1]) 
                       for s in stream_surahs_list]
        stream_service.prepare_stream_files(stream_files)
        
        logger.info(f"Prepared {len(stream_service.streams)} stream segments")
        return 0
    except Exception as e:
        logger.error(f"Prepare command failed: {e}")
        return 1


def handle_validate_command(args: argparse.Namespace) -> int:
    """
    Handle the validate command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    from ratteil.utils.validation import stream_validation
    from ratteil.services.stream_service import StreamService
    from ratteil.data.data_manager import QuranDataManager
    from ratteil.config.settings import get_settings
    from pathlib import Path
    import glob as g
    
    settings = get_settings()
    if args.verbose:
        settings.debug = True
    
    resources_path = settings.data_dir
    package_path = Path(__file__).resolve().parent.parent
    
    try:
        # Try to use API method first
        try:
            data_manager = QuranDataManager(
                language=settings.data_language,
                offline=settings.data_offline
            )
            
            # Convert API reciters to old format for compatibility
            recitersDB = {}
            recitersCodesDB = []
            
            for reciter in data_manager.get_reciters():
                code = reciter.code
                recitersCodesDB.append(code)
                recitersDB[code] = {
                    "id": reciter.id,
                    "name": reciter.name,
                    "letter": reciter.letter or "",
                    "moshaf": reciter.moshafs or []
                }
            
            logger.debug(f"Using API data: {len(recitersCodesDB)} reciters loaded")
            
        except Exception as api_error:
            logger.warning(f"API method failed, falling back to static data: {api_error}")
            # Fallback to old static method
            from ratteil.reciters import reciters_code as recitersCodesDB, reciters as recitersDB
        
        stream_service = StreamService(
            recitersDB,
            resources_path,
            package_path,
            settings
        )
        
        temp_reciters_list = args.reciter or recitersCodesDB
        
        stream_files = g.glob(str(resources_path / "audios/*"))
        stream_validation(
            stream_service,
            settings.max_stream_length,
            stream_files,
            args.min_length,
            temp_reciters_list,
            0,
            None,
            recitersDB,
            resources_path
        )
        
        logger.info("Stream validation completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Validate command failed: {e}")
        return 1


def handle_config_command(args: argparse.Namespace) -> int:
    """
    Handle the config command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    import os
    from ratteil.config.settings import get_settings, reload_settings
    
    try:
        if args.action == "show":
            settings = get_settings()
            print("RatTeil Configuration:")
            print("=" * 50)
            for key, value in settings.to_dict().items():
                print(f"  {key}: {value}")
        
        elif args.action == "get":
            if not args.key:
                print("Please specify a configuration key")
                return 1
            settings = get_settings()
            settings_dict = settings.to_dict()
            if args.key in settings_dict:
                print(f"{args.key}: {settings_dict[args.key]}")
            else:
                print(f"Unknown configuration key: {args.key}")
                return 1
        
        elif args.action == "set":
            if not args.key or not args.value:
                print("Please specify both key and value")
                return 1
            
            # Handle special config keys
            if args.key == "language":
                # Set data language
                from ratteil.data.data_manager import QuranDataManager
                import os
                
                # Save to .env file
                env_path = Path.home() / ".ratteil" / ".env"
                env_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Update or add RATTEIL_LANGUAGE
                env_lines = []
                found = False
                if env_path.exists():
                    with open(env_path, "r", encoding="utf-8") as f:
                        env_lines = f.readlines()
                
                with open(env_path, "w", encoding="utf-8") as f:
                    for line in env_lines:
                        if line.startswith("RATTEIL_LANGUAGE="):
                            f.write(f"RATTEIL_LANGUAGE={args.value}\n")
                            found = True
                        else:
                            f.write(line)
                    if not found:
                        f.write(f"RATTEIL_LANGUAGE={args.value}\n")
                
                # Also set environment variable for current session
                os.environ["RATTEIL_LANGUAGE"] = args.value
                
                # Reload settings
                from ratteil.config.settings import reload_settings
                reload_settings()
                
                print(f"Language set to: {args.value}")
                print("This will be used for new data fetching sessions.")
                print("To apply immediately, restart RatTeil or use 'ratteil data refresh'")
                
            elif args.key == "data_mode":
                # Set offline/online mode
                from ratteil.data.data_manager import QuranDataManager
                import os
                
                # Save to .env file
                env_path = Path.home() / ".ratteil" / ".env"
                env_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Update or add RATTEIL_DATA_MODE
                env_lines = []
                found = False
                if env_path.exists():
                    with open(env_path, "r", encoding="utf-8") as f:
                        env_lines = f.readlines()
                
                with open(env_path, "w", encoding="utf-8") as f:
                    for line in env_lines:
                        if line.startswith("RATTEIL_DATA_MODE="):
                            f.write(f"RATTEIL_DATA_MODE={args.value}\n")
                            found = True
                        else:
                            f.write(line)
                    if not found:
                        f.write(f"RATTEIL_DATA_MODE={args.value}\n")
                
                # Also set environment variable for current session
                os.environ["RATTEIL_DATA_MODE"] = args.value
                
                print(f"Data mode set to: {args.value}")
                print("Use 'online' for API fetching or 'offline' for cached data")
                
            else:
                # Set any configuration key
                env_path = Path.home() / ".ratteil" / ".env"
                env_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Update or add the configuration key
                env_lines = []
                found = False
                if env_path.exists():
                    with open(env_path, "r", encoding="utf-8") as f:
                        env_lines = f.readlines()
                
                with open(env_path, "w", encoding="utf-8") as f:
                    for line in env_lines:
                        if line.startswith(f"RATTEIL_{args.key.upper()}="):
                            f.write(f"RATTEIL_{args.key.upper()}={args.value}\n")
                            found = True
                        else:
                            f.write(line)
                    if not found:
                        f.write(f"RATTEIL_{args.key.upper()}={args.value}\n")
                
                # Also set environment variable for current session
                os.environ[f"RATTEIL_{args.key.upper()}"] = args.value
                
                # Reload settings
                reload_settings()
                
                print(f"Configuration set: {args.key} = {args.value}")
                print(f"Saved to: {env_path}")
                print("This will be used for new RatTeil sessions.")
        
        return 0
    except Exception as e:
        logger.error(f"Config command failed: {e}")
        return 1


def handle_copyright_command(args: argparse.Namespace) -> int:
    """
    Handle the copyright command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code
    """
    from ratteil.cli.commands import handle_copyright
    from pathlib import Path
    
    package_path = Path(__file__).resolve().parent.parent
    handle_copyright(package_path)
    return 0


def main():
    """
    Main entry point for CLI.
    """
    parser = create_main_parser()
    args = parser.parse_args()
    
    # Handle verbose flag
    if args.verbose:
        from ratteil.config.settings import reload_settings
        settings = reload_settings()
        settings.debug = True
    
    # Route to appropriate handler
    handlers = {
        "stream": handle_stream_command,
        "download": handle_download_command,
        "list": handle_list_command,
        "auth": handle_auth_command,
        "prepare": handle_prepare_command,
        "validate": handle_validate_command,
        "config": handle_config_command,
        "copyright": handle_copyright_command,
    }
    
    if args.command in handlers:
        return handlers[args.command](args)
    
    # No command or unknown command - show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
