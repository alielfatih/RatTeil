"""Argument parser for RatTeil CLI."""

import argparse
from typing import Optional, List

from ratteil.config import get_settings


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for RatTeil CLI.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='ratteil',
        description='RatTeil - Quran recitation streaming tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  ratteil --surahs 5 --reciters 3           Stream random 5 surahs by 3 reciters
  ratteil --surahs 1,2,3 --reciters alafasy Stream specific surahs by Alafasy
  ratteil --list-reciters                   List all available reciters
  ratteil --list-surahs                     List all available surahs
  ratteil --download --surahs 1-10         Download surahs 1-10
  ratteil --stream --youtube                Stream to YouTube
  
YouTube Authentication (for --youtube):
  - Service Account: Set YOUTUBE_CLIENT_SECRETS=path/to/service-account.json
  - Device Flow: Set YOUTUBE_CLIENT_SECRETS=path/to/client-secrets.json
  - API Key: Set YOUTUBE_API_KEY=your_api_key
        ''',
    )
    
    # Main arguments
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {get_settings().APP_VERSION}',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging',
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file',
    )
    
    # YouTube authentication mode
    parser.add_argument(
        '--youtube-auth',
        type=str,
        choices=['service_account', 'device_flow', 'api_key'],
        default='device_flow',
        help='YouTube authentication mode for headless operation',
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        title='Commands',
        required=False,
    )
    
    # Download command
    download_parser = subparsers.add_parser(
        'download',
        help='Download audio files',
    )
    download_parser.add_argument(
        '--surahs',
        type=str,
        help='Surahs to download (e.g., "1,2,3" or "1-10")',
    )
    download_parser.add_argument(
        '--reciters',
        type=str,
        help='Reciters to download from (comma-separated IDs)',
    )
    download_parser.add_argument(
        '--all',
        action='store_true',
        help='Download all surahs',
    )
    download_parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for downloads',
    )
    
    # Stream command
    stream_parser = subparsers.add_parser(
        'stream',
        help='Stream audio files',
    )
    stream_parser.add_argument(
        '--surahs',
        type=str,
        help='Surahs to stream (e.g., "1,2,3" or "1-10")',
    )
    stream_parser.add_argument(
        '--reciters',
        type=str,
        help='Reciters to stream from (comma-separated IDs)',
    )
    stream_parser.add_argument(
        '--random',
        action='store_true',
        help='Use random selection of surahs and reciters',
    )
    stream_parser.add_argument(
        '--surahs-count',
        type=int,
        help='Number of random surahs to select',
    )
    stream_parser.add_argument(
        '--reciters-count',
        type=int,
        help='Number of random reciters to select',
    )
    stream_parser.add_argument(
        '--youtube',
        action='store_true',
        help='Stream to YouTube Live',
    )
    stream_parser.add_argument(
        '--title',
        type=str,
        help='Stream title',
    )
    stream_parser.add_argument(
        '--description',
        type=str,
        help='Stream description',
    )
    stream_parser.add_argument(
        '--no-merge',
        action='store_true',
        help='Do not merge audio files before streaming',
    )
    
    # List commands
    list_parser = subparsers.add_parser(
        'list',
        help='List available items',
    )
    list_parser.add_argument(
        '--reciters',
        action='store_true',
        help='List all available reciters',
    )
    list_parser.add_argument(
        '--surahs',
        action='store_true',
        help='List all available surahs',
    )
    list_parser.add_argument(
        '--reciters-with-multiple-moshafs',
        action='store_true',
        help='List reciters with multiple moshafs',
    )
    
    # Prepare command
    prepare_parser = subparsers.add_parser(
        'prepare',
        help='Prepare stream files without streaming',
    )
    prepare_parser.add_argument(
        '--surahs',
        type=str,
        help='Surahs to prepare',
    )
    prepare_parser.add_argument(
        '--reciters',
        type=str,
        help='Reciters to use',
    )
    prepare_parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for prepared files',
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate stream configuration',
    )
    validate_parser.add_argument(
        '--surahs',
        type=str,
        help='Surahs to validate',
    )
    validate_parser.add_argument(
        '--reciters',
        type=str,
        help='Reciters to validate',
    )
    
    # YouTube auth test command
    yt_auth_parser = subparsers.add_parser(
        'youtube-auth-test',
        help='Test YouTube authentication',
    )
    yt_auth_parser.add_argument(
        '--mode',
        type=str,
        choices=['service_account', 'device_flow', 'api_key'],
        default='device_flow',
        help='Authentication mode to test',
    )
    
    return parser


def parse_args(args: Optional[List[str]] = None):
    """Parse command line arguments.
    
    Args:
        args: Optional list of arguments (defaults to sys.argv)
        
    Returns:
        Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args(args)
