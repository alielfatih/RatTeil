# RatTeil - Quran Recitation Streaming Tool

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

RatTeil is a Python application for downloading, managing, and streaming Quran recitations from various reciters. It provides functionality to:

- Download Quran audio from multiple reciters
- Generate random playlists of surahs and reciters
- Stream to local or YouTube Live
- Merge audio files for continuous playback

## Features

- **Clean Architecture**: Proper separation of concerns with repositories, services, and models
- **Type Safety**: Full type hints throughout the codebase
- **Async Support**: Async/await support for I/O operations
- **Configuration Management**: Environment-based configuration with Pydantic
- **Dependency Injection**: Easy to test and extend
- **CLI Interface**: Comprehensive command-line interface

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- pip (Python package manager)

### Install from PyPI

```bash
pip install ratteil
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/example/ratteil.git
cd ratteil

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For development
pip install -r requirements-dev.txt
```

### Install FFmpeg

FFmpeg is required for audio processing:

- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **Mac**: `brew install ffmpeg`
- **Windows**: Download from [FFmpeg official site](https://ffmpeg.org/)

## Configuration

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
# Edit .env with your settings
```

### Required Configuration

- `RATTEIL_AC`: Access key for your API
- `RATTEIL_SE`: Secret key for your API

### Optional Configuration

- `DEBUG`: Enable debug logging
- `DATA_DIR`: Directory for data files
- `AUDIO_DIR`: Directory for downloaded audio
- `STREAM_DIR`: Directory for stream files
- `YOUTUBE_API_KEY`: YouTube API key for streaming
- `MAX_RECITERS`: Maximum number of reciters to use
- `MAX_SURAHS`: Maximum number of surahs to use

## Usage

### Basic Usage

```bash
# Run with default settings (random selection)
ratteil

# List available reciters
ratteil --list-reciters

# List available surahs
ratteil --list-surahs

# Stream specific surahs by specific reciters
ratteil --surahs 1,2,3 --reciters alafasy,husary

# Stream random surahs by random reciters
ratteil --random --surahs-count 5 --reciters-count 3
```

### Download Audio

```bash
# Download all surahs by a specific reciter
ratteil download --reciters alafasy --all

# Download specific surahs
ratteil download --surahs 1-10 --reciters alafasy,husary

# Download to custom directory
ratteil download --surahs 1,2,3 --reciters alafasy --output-dir ./my_audio
```

### Stream to YouTube

```bash
# Stream to YouTube Live
ratteil stream --surahs 1,2,3 --reciters alafasy --youtube

# With custom title and description
ratteil stream --random --surahs-count 5 --youtube \
    --title "My Quran Stream" \
    --description "Automated Quran recitation"
```

### Prepare Stream Files

```bash
# Prepare files without streaming
ratteil prepare --surahs 1-5 --reciters alafasy,husary

# Validate stream configuration
ratteil validate --surahs 1-5 --reciters alafasy,husary
```

## Architecture

### Directory Structure

```
ratteil/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for module execution
├── config/
│   ├── __init__.py
│   ├── exceptions.py    # Custom exceptions
│   └── settings.py      # Application settings
├── models/
│   ├── __init__.py
│   ├── reciter.py       # Reciter and Moshaf models
│   ├── stream.py        # Stream models
│   └── surah.py         # Surah models
├── repositories/
│   ├── __init__.py
│   ├── reciter_repository.py  # Reciter data access
│   └── surah_repository.py    # Surah data access
├── services/
│   ├── __init__.py
│   ├── audio_service.py        # Audio processing
│   ├── download_service.py     # Download functionality
│   ├── randomizer_service.py   # Random selection
│   ├── stream_service.py       # Streaming
│   └── youtube_service.py      # YouTube integration
├── utils/
│   ├── __init__.py
│   ├── file_utils.py     # File utilities
│   ├── logging.py        # Logging configuration
│   └── validation.py     # Validation functions
└── cli/
    ├── __init__.py
    ├── parser.py         # Argument parsing
    └── commands.py        # CLI commands
```

### Key Components

- **Models**: Dataclasses representing domain objects (Surah, Reciter, StreamDetails, etc.)
- **Repositories**: Data access layer (LocalSurahRepository, LocalReciterRepository)
- **Services**: Business logic (AudioService, DownloadService, StreamService, etc.)
- **Utils**: Helper functions (file operations, validation, logging)
- **CLI**: Command-line interface

## Development

### Running Tests

```bash
pytest
pytest --cov=ratteil --cov-report=html
```

### Code Formatting

```bash
black ratteil
isort ratteil
```

### Type Checking

```bash
mypy ratteil
```

### Linting

```bash
flake8 ratteil
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- All Quran audio is sourced from public domain or properly licensed sources
- Special thanks to all the reciters whose beautiful recitations make this possible

## Contact

For questions or support, please open an issue on GitHub.
