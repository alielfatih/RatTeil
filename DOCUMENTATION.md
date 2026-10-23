# RatTeil - Comprehensive Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [CLI Commands](#cli-commands)
5. [Services Layer](#services-layer)
6. [Authentication System](#authentication-system)

---

## Overview

### What is RatTeil?

**RatTeil** is a comprehensive Python application for downloading, managing, and streaming Quran recitations from various reciters. It provides functionality to stream to YouTube Live and Facebook Live using non-GUI authentication that works on any platform.

### Key Features

- **Multi-Platform Streaming**: Stream to YouTube Live and Facebook Live simultaneously
- **Non-GUI Authentication**: Uses device flow authentication that works without a browser
- **Cross-Platform**: Supports Linux, Windows, macOS, Android (Termux), and iOS (Pythonista)
- **Async/Await Support**: Full asynchronous support for I/O operations
- **Clean Architecture**: Proper separation of concerns with SOLID principles
- **Type Safety**: Full type hints with Pydantic-based settings
- **Dependency Injection**: Container-based dependency management
- **Comprehensive Testing**: 60+ passing tests with mockable dependencies

---

## Architecture

### System Architecture Diagram

```
RatTeil Application
├── CLI Interface (main.py, parser.py, commands.py)
├── Services Layer (stream, download, audio, youtube, facebook)
├── Authentication (google_auth, facebook_auth)
├── Repositories (surah, reciter)
├── Models (surah, reciter, stream, auth)
├── Configuration (settings, constants)
└── Utilities (logging, file_utils, validation, platform)
```

### Design Patterns Used

1. **Repository Pattern**: Separates data access from business logic
2. **Dependency Injection**: Enables easy testing and extension
3. **Factory Pattern**: Used for creating services and repositories
4. **Strategy Pattern**: Different authentication strategies
5. **Protocol/Interface Pattern**: Defines contracts for repositories

---

## Core Components

### 1. CLI Module

The CLI module provides the command-line interface with subcommands:

- `main.py`: Main entry point with argument parsing
- `parser.py`: Argument parser configuration  
- `commands.py`: Command handlers

**Main Commands:**
- `stream`: Stream Quran recitations
- `download`: Download Quran audio
- `list`: List available resources
- `auth`: Manage authentication
- `prepare`: Prepare stream files
- `validate`: Validate stream configuration
- `config`: Manage configuration
- `copyright`: Show copyright information

### 2. Configuration Module

Pydantic-based settings with:
- Environment variable support
- .env file support
- Default values
- Runtime validation

### 3. Models Module

Dataclasses for domain objects:
- `SurahInfo`: Surah information
- `Reciter`: Reciter information
- `StreamConfig`: Stream configuration
- `StreamDetails`: Stream details
- `AuthCredentials`: Authentication credentials
- `OAuthToken`: OAuth token information

### 4. Services Module

Business logic services:
- `StreamService`: Streaming functionality
- `DownloadService`: Audio file downloading
- `AudioService`: Audio processing
- `RandomizerService`: Random selection
- `YouTubeService`: YouTube API integration
- `FacebookService`: Facebook API integration

### 5. Authentication Module

Authentication services:
- `GoogleAuthService`: Google OAuth 2.0 device flow
- `YouTubeAuthService`: YouTube-specific authentication
- `FacebookAuthService`: Facebook authentication

### 6. Repositories Module

Data access layer:
- `SurahRepository`: Surah data access
- `ReciterRepository`: Reciter data access
- Protocol-based interfaces for easy mocking

---

## CLI Commands

### Basic Usage

```bash
ratteil [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose logging |
| `-d, --dev` | Enable development mode |

### 1. `stream` - Stream Quran Recitations

**Usage:** `ratteil stream -p PLATFORM [OPTIONS]`

**Required:**
- `-p, --platform`: youtube, yt, fb, facebook

**Options:**
- `-R, --reciter`: Reciter code(s)
- `-s, --surah`: Specific surah (1-114)
- `-n, --surahs`: Number of surahs (default: 30)
- `-q, --qaris`: Number of reciters (default: 5)
- `--max-length`: Max stream length in minutes (default: 75.0)
- `--min-length`: Min stream length in minutes (default: 120.0)
- `--no-download`: Use existing files
- `--skip-validation`: Skip validation
- `-t, --title`: Custom title
- `-D, --description`: Custom description

**Examples:**
```bash
ratteil stream -p youtube
ratteil stream -p youtube facebook -R alafasy husary -n 10
ratteil stream -p youtube -t "My Stream" -D "Description"
```

### 2. `download` - Download Quran Audio

**Usage:** `ratteil download -R RECITER [OPTIONS]`

**Required:**
- `-R, --reciter`: Reciter code(s)

**Options:**
- `-s, --surah`: Specific surah (1-114)
- `-n, --surahs`: Number of surahs (default: 10)
- `-o, --output`: Output directory
- `-a, --all`: Download all surahs

**Examples:**
```bash
ratteil download -R alafasy --all
ratteil download -R alafasy -n 10
ratteil download -R alafasy -s 1 -o /path/to/output
```

### 3. `list` - List Resources

**Usage:** `ratteil list [RESOURCE]`

**Resource:** reciters, surahs, all (default: reciters)

**Options:**
- `-v, --verbose`: Show detailed info

**Examples:**
```bash
ratteil list reciters
ratteil list surahs
ratteil list all -v
```

### 4. `auth` - Manage Authentication

**Usage:** `ratteil auth [PROVIDER] [OPTIONS]`

**Provider:** youtube, facebook, all (default: all)

**Options:**
- `--revoke`: Revoke token
- `--check`: Check status

**Examples:**
```bash
ratteil auth youtube
ratteil auth all
ratteil auth youtube --check
ratteil auth youtube --revoke
```

### 5. `prepare` - Prepare Stream Files

**Usage:** `ratteil prepare [OPTIONS]`

**Options:**
- `-R, --reciter`: Reciter code(s)
- `-s, --surah`: Specific surah
- `-n, --surahs`: Number of surahs (default: 30)
- `--max-length`: Max length in minutes (default: 75.0)

### 6. `validate` - Validate Configuration

**Usage:** `ratteil validate [OPTIONS]`

**Options:**
- `-R, --reciter`: Reciter code(s)
- `-m, --min-length`: Min length in minutes (default: 120.0)

### 7. `config` - Manage Configuration

**Usage:** `ratteil config ACTION [KEY] [VALUE]`

**Actions:** show, set, get

**Examples:**
```bash
ratteil config show
ratteil config get max_stream_length
ratteil config set language ar
```

---

## Services Layer

### StreamService

Core service for streaming operations:
- Prepares audio files into stream segments
- Generates stream titles and descriptions
- Creates streams on YouTube and Facebook
- Handles stream execution

**Key Methods:**
```python
prepare_stream_files(stream_files)
generate_stream_details(stream)
create_youtube_stream(title, description)
create_facebook_stream(title, description)
execute_stream(stream)
```

### DownloadService

Handles audio file downloading:
- Downloads from MP3Quran.net
- Manages concurrent downloads
- Handles file cleanup
- Validates downloads

**Key Methods:**
```python
download_audios(max_len, surahs_list, reciters_db, resources_path)
```

### AudioService

Audio processing:
- Gets audio duration
- Validates audio files
- Converts audio formats
- Uses FFmpeg

**Key Methods:**
```python
get_audio_length(file_path)
validate_audio(file_path)
convert_audio(input_path, output_path, format)
```

### RandomizerService

Random selection:
- Randomly selects reciters
- Randomly selects surahs
- Ensures balanced distribution

**Key Methods:**
```python
generate_random_reciters_list(count, reciters_list, reciters_db)
generate_random_surahs_list(count, start_surah, selected_reciters)
```

---

## Authentication System

### YouTube Device Flow

1. User runs `ratteil auth youtube`
2. Application displays device code and verification URL
3. User visits URL on any device with browser
4. User enters device code
5. Application receives access token
6. Token stored securely

### Facebook Authentication

1. Set `RATTEIL_FACEBOOK_ACCESS_TOKEN` environment variable
2. Application validates token on first use
3. Token used for all API calls

### Token Storage

Tokens stored in platform-specific locations:
- Linux/macOS: `~/.config/ratteil/tokens/`
- Windows: `%APPDATA%\ratteil\tokens\`
- Termux: `$PREFIX/var/lib/ratteil/tokens/`

---

## Configuration

### Settings Hierarchy

1. Environment Variables (RATTEIL_*)
2. .env File
3. Default Values

### Key Configuration Options

**Application:**
- `app_name`, `app_version`, `debug`

**Directories:**
- `data_dir`, `audio_dir`, `img_dir`

**Authentication:**
- YouTube: `youtube_client_id`, `youtube_client_secret`
- Facebook: `facebook_access_token`, `facebook_app_secret`, `facebook_page_id`

**Streaming:**
- `max_stream_length`, `min_stream_length`

**Download:**
- `max_concurrent_downloads`, `download_timeout`

**FFmpeg:**
- `ffmpeg_path`, `ffprobe_path`

### .env File Example

```ini
RATTEIL_YOUTUBE_CLIENT_ID=your_client_id
RATTEIL_YOUTUBE_CLIENT_SECRET=your_client_secret
RATTEIL_FACEBOOK_ACCESS_TOKEN=your_token
RATTEIL_MAX_STREAM_LENGTH=75.0
RATTEIL_LOG_LEVEL=INFO
```

---

## Platform Support

| Platform | Support | Notes |
|----------|---------|-------|
| Linux | Full | Native support |
| Windows | Full | Uses .exe files |
| macOS | Full | Native support |
| Android (Termux) | Full | Uses Termux paths |
| iOS (Pythonista) | Partial | Limited by sandbox |

---

## Development

### Setup

```bash
git clone https://github.com/alielfatih/RatTeil.git
cd RatTeil
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Tests

```bash
pytest
pytest --cov=ratteil --cov-report=html
```

### Quality

```bash
black src/ratteil
isort src/ratteil
mypy src/ratteil
flake8 src/ratteil
```

---

## License

MIT License - See LICENSE file for details.

---

*Made with love by Moddaker Team*
