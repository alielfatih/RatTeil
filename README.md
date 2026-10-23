# RatTeil - Quran Recitation Streaming Tool

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CI Status](https://github.com/alielfatih/RatTeil/actions/workflows/ci.yml/badge.svg)](https://github.com/alielfatih/RatTeil/actions)

**RatTeil** is a comprehensive Python application for downloading, managing, and streaming Quran recitations from various reciters. It provides functionality to stream to YouTube Live and Facebook Live using non-GUI authentication that works on any platform.

## ✨ Features

### 🏗️ Clean Architecture
- **Proper separation of concerns**: Models, Repositories, Services, Utils, CLI
- **SOLID principles** applied throughout
- **Protocol-based interfaces** for repositories enabling easy mocking and testing
- **Dependency Injection** container for managing application dependencies

### 🔒 Type Safety
- **Full type hints** throughout the codebase
- **Pydantic-based settings** with environment variable support
- **Dataclasses** for all models
- **Validation** at runtime with clear error messages

### 🚀 Async Support
- **Async/await** ready for all I/O operations
- **Async generators** for streaming operations
- **Concurrent downloads** with configurable limits
- **Non-blocking** operations where appropriate

### 🎯 Non-GUI Authentication
- **Google OAuth 2.0 Device Flow** for YouTube authentication
- **Facebook Graph API** authentication
- **Token management** with secure storage
- **Works on any OS** without browser/GUI requirements

### 📱 Cross-Platform Support
- **Linux**: Native support
- **Windows**: Full support with .exe handling
- **macOS**: Native support
- **Android (Termux)**: Full support
- **iOS (Pythonista)**: Supported

### 🔧 Configuration Management
- **Environment-based settings** via Pydantic
- **.env file support** for local development
- **No hardcoded keys** - all configurable
- **Sensible defaults** with validation

### 💻 Modern CLI
- **Subcommands** for all operations (stream, download, list, auth, prepare, validate, config, copyright)
- **Comprehensive help** with examples
- **Consistent argument** naming and behavior
- **Backward compatible** with legacy mode

### 🧪 Testability
- **Comprehensive test structure**
- **Mockable dependencies** via protocols
- **Unit tests** for models, services, and utils
- **60+ passing tests**

## 📦 Installation

### Prerequisites

- **Python 3.8 or higher**
- **FFmpeg** (for audio processing)
- **pip** (Python package manager)

### Install from PyPI

```bash
pip install ratteil
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/alielfatih/RatTeil.git
cd RatTeil

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

### Install FFmpeg

FFmpeg is required for audio processing:

- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **Mac**: `brew install ffmpeg`
- **Windows**: Download from [FFmpeg official site](https://ffmpeg.org/)
- **Android (Termux)**: `pkg install ffmpeg`
- **iOS (Pythonista)**: Use the built-in ffmpeg or install via StaSh

## 📝 Configuration

### Environment Variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
# Edit .env with your settings
```

Or set environment variables directly:

```bash
# YouTube Authentication
export RATTEIL_YOUTUBE_CLIENT_ID="your_client_id"
export RATTEIL_YOUTUBE_CLIENT_SECRET="your_client_secret"

# Facebook Authentication
export RATTEIL_FACEBOOK_ACCESS_TOKEN="your_access_token"
export RATTEIL_FACEBOOK_APP_SECRET="your_app_secret"
export RATTEIL_FACEBOOK_PAGE_ID="your_page_id"

# Application Settings
export RATTEIL_DEBUG="True"
export RATTEIL_DATA_DIR="/path/to/data"
export RATTEIL_MAX_STREAM_LENGTH="75"
export RATTEIL_MIN_STREAM_LENGTH="120"
```

### Required Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `RATTEIL_YOUTUBE_CLIENT_ID` | Google OAuth 2.0 Client ID | For YouTube |
| `RATTEIL_YOUTUBE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret | For YouTube |
| `RATTEIL_FACEBOOK_ACCESS_TOKEN` | Facebook Access Token | For Facebook |
| `RATTEIL_FACEBOOK_APP_SECRET` | Facebook App Secret | For Facebook |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RATTEIL_DATA_DIR` | Directory for data files | `~/RatTeil-resources` |
| `RATTEIL_MAX_STREAM_LENGTH` | Maximum stream length in minutes | `75.0` |
| `RATTEIL_MIN_STREAM_LENGTH` | Minimum stream length in minutes | `120.0` |
| `RATTEIL_MAX_CONCURRENT_DOWNLOADS` | Maximum concurrent downloads | `5` |
| `RATTEIL_FFMPPEG_PATH` | Path to ffmpeg executable | `ffmpeg` |
| `RATTEIL_FFPROBE_PATH` | Path to ffprobe executable | `ffprobe` |
| `RATTEIL_LOG_LEVEL` | Logging level | `INFO` |
| `RATTEIL_DEBUG` | Enable debug logging | `False` |

## 🚀 Usage

### Basic Usage

```bash
# Run with default settings (random selection)
ratteil stream -t youtube

# List available reciters
ratteil list reciters

# List available surahs
ratteil list surahs

# List all resources
ratteil list all
```

### Authentication

```bash
# Authenticate with YouTube (uses device flow)
ratteil auth youtube

# Authenticate with Facebook
ratteil auth facebook

# Authenticate with all providers
ratteil auth all

# Check authentication status
ratteil auth --check

# Revoke tokens
ratteil auth --revoke youtube
```

### Download Audio

```bash
# Download all surahs by a specific reciter
ratteil download -R alafasy --all

# Download specific number of surahs
ratteil download -R alafasy -sn 10

# Download to custom directory
ratteil download -R alafasy -sn 5 -o /path/to/output
```

### Stream to YouTube

```bash
# Stream to YouTube Live with random selection
ratteil stream -t youtube

# Stream specific surahs by specific reciters
ratteil stream -t youtube -R alafasy -s 1 -sn 5

# Stream with custom title and description
ratteil stream -t youtube -T "My Quran Stream" -D "Automated Quran recitation"

# Stream to multiple platforms
ratteil stream -t youtube facebook -R alafasy,husary
```

### Stream to Facebook

```bash
# Stream to Facebook Live
ratteil stream -t facebook

# Stream to Facebook with specific configuration
ratteil stream -t facebook -R alafasy -sn 10
```

### Prepare Stream Files

```bash
# Prepare files without streaming
ratteil prepare -R alafasy,husary -sn 20

# Prepare with custom max length
ratteil prepare -mx 60 -sn 15
```

### Validate Stream Configuration

```bash
# Validate stream configuration
ratteil validate -m 120

# Validate with specific reciters
ratteil validate -R alafasy,husary -m 180
```

### Configuration Management

```bash
# Show current configuration
ratteil config show

# Get specific configuration value
ratteil config get max_stream_length

# Set configuration value (stores in .env)
ratteil config set max_stream_length 90
```

### Show Copyright

```bash
ratteil copyright
```

## 📁 Project Structure

```
ratteil/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point for module execution
├── container.py             # Dependency injection container
├── cli/
│   ├── __init__.py
│   ├── main.py              # CLI entry point with subcommands
│   ├── parser.py            # Argument parsing
│   └── commands.py          # CLI command handlers
├── config/
│   ├── __init__.py
│   ├── constants.py         # Application constants
│   ├── exceptions.py        # Custom exceptions
│   └── settings.py          # Pydantic-based settings
├── models/
│   ├── __init__.py
│   ├── auth.py              # Authentication models
│   ├── reciter.py           # Reciter model
│   ├── stream.py            # Stream models
│   └── surah.py             # Surah model
├── repositories/
│   ├── __init__.py
│   ├── protocols.py         # Repository protocols (interfaces)
│   ├── reciter_repository.py
│   └── surah_repository.py
├── services/
│   ├── __init__.py
│   ├── audio_service.py     # Audio processing
│   ├── download_service.py  # Download functionality
│   ├── randomizer_service.py # Random selection
│   ├── stream_service.py    # Streaming
│   ├── youtube_service.py   # YouTube API integration
│   ├── facebook_service.py  # Facebook API integration
│   └── youtube_stream_service.py # YouTube stream creation
├── auth/
│   ├── __init__.py
│   ├── base.py              # Base auth classes
│   ├── google_auth.py       # Google OAuth 2.0 device flow
│   └── facebook_auth.py     # Facebook authentication
├── utils/
│   ├── __init__.py
│   ├── file_utils.py        # File utilities
│   ├── logging.py           # Structured logging
│   ├── platform.py          # Platform compatibility
│   └── validation.py        # Validation functions
└── tests/
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures
    ├── test_config.py       # Configuration tests
    ├── test_models.py       # Model tests
    ├── test_services.py     # Service tests
    └── test_utils.py        # Utility tests
```

## 🏗️ Architecture

### Key Components

1. **Models**: Dataclasses representing domain objects (Surah, Reciter, StreamConfig, StreamDetails, OAuthToken, AuthCredentials)
2. **Repositories**: Data access layer with protocol interfaces (SurahRepositoryProtocol, ReciterRepositoryProtocol, etc.)
3. **Services**: Business logic (AudioService, DownloadService, StreamService, YouTubeService, FacebookService, etc.)
4. **Auth**: Authentication services with device flow support (GoogleAuthService, FacebookAuthService)
5. **Utils**: Helper functions (file operations, validation, logging, platform detection)
6. **CLI**: Command-line interface with subcommands
7. **Container**: Dependency injection container for managing dependencies

### Design Patterns

- **Repository Pattern**: Separates data access from business logic
- **Dependency Injection**: Enables easy testing and extension
- **Factory Pattern**: Used for creating services and repositories
- **Strategy Pattern**: Different authentication strategies for different platforms
- **Protocol/Interface Pattern**: Defines contracts for repositories

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=ratteil --cov-report=html

# Run specific test module
pytest src/ratteil/tests/test_models.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Code formatting
black ratteil
isort ratteil

# Type checking
mypy ratteil

# Linting
flake8 ratteil
```

### Environment Setup

```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

## 📜 Authentication Flow

### YouTube Device Flow

1. User runs `ratteil auth youtube`
2. Application displays device code and verification URL
3. User visits the URL on any device with a browser
4. User enters the device code
5. Application receives access token
6. Token is stored securely for future use

### Facebook Authentication

1. User sets `RATTEIL_FACEBOOK_ACCESS_TOKEN` environment variable
2. Application validates the token on first use
3. Token is used for all Facebook API calls

## 🎯 Platform Support

| Platform | Support | Notes |
|----------|---------|-------|
| Linux | ✅ Full | Native support |
| Windows | ✅ Full | Uses .exe files |
| macOS | ✅ Full | Native support |
| Android (Termux) | ✅ Full | Uses Termux paths |
| iOS (Pythonista) | ✅ Partial | Limited by Pythonista |

### Platform-Specific Paths

The application automatically detects the platform and adjusts:
- **FFmpeg/FFprobe paths**
- **Temporary directories**
- **Cache directories**
- **Path separators**
- **Executable suffixes**

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- All Quran audio is sourced from public domain or properly licensed sources
- Special thanks to all the reciters whose beautiful recitations make this possible
- Built with love and care by the Moddaker Team

## 📞 Contact

For questions or support, please open an issue on [GitHub](https://github.com/alielfatih/RatTeil/issues).

---

**Made with ❤️ & ^_^ by Moddaker Team**
