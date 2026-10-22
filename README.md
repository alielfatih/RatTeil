*RatTeil*

RatTeil is a Python app to stream the Holy Quran to YouTube. Streaming the Holy Quran to YouTube has never been easier, install RatTeil, run it, and step back - RatTeil will do the rest. RatTeil will auto/manually choose reciters and surahs for each stream, download the required audio files, and start streaming them.

*How to Install*

*Android*

1. Install Termux app.
2. Run `pkg update -y`.
3. Then `pkg install python wget ffmpeg -y`.
4. Then `python -m pip install ratteil`.
5. Run `ratteil -h` to see available options.

*Linux, Debian, etc.*

1. Run `apt-get update -y`.
2. Then `apt-get install python wget ffmpeg -y`.
3. Then `python -m pip install ratteil`.
4. Run `ratteil -h` to see available options.

Or

1. Clone RatTeil repo and change to the RatTeil folder.
2. Run `sh install.sh`.
3. Run `python __main__.py -h` to see options.

Or

1. Download RatTeil package from GitHub or PyPI.
2. Install requirements with `apt-get install python ffmpeg wget -y`.
3. Run `python -m pip install <ratteil_package_file_path>`.

*Quick Start*

Before running this command, make sure you have:

- Placed your images/videos for stream background under `~/RatTeil-resources/imgs/`
- Placed your video introduction and conclusion under `~/RatTeil-resources/fixer/` ( filenames must be `introduction.mp4` and `conclusion.mp4`)

1. Run `python -m pip install ratteil`.
2. Run `ratteil -t youtube`.
3. Copy authentication links.
4. Follow the Google authentication link.
5. Enter the authentication code/token and verify your authority.
6. Done; the stream will start in a few moments.
7. Visit your YouTube channel or Facebook page to see your stream.

*RatTeil Available Commands and Options*

```
console usage: ratteil [-h] [-l] [-m] [-ms] [-n] [-R [...]] [-r] [-sn] [-s] [--no-download] [--no-validation] -t [...]
```

| Command | Description |
| --- | --- |
| -h, --help | Show help message. |
| -l, --list | List all available reciters. |
| -m, --min | Set the minimum length for stream validation in minutes; default is 120 minutes (2 hours). |
| -ms, --streams | Set the number of streams per run; each stream will be 75 minutes or less. This value will automatically recalculate the minimum stream length for validation. |
| -n | Set the number of reciters per stream; default is randomly between 3-7. |
| -R, --reciter | Manually choose stream reciter/reciters. |
| -r, --resume | Coming soon. |
| -sn | Set the number of surahs per stream; default is randomly between 20-50. |
| --no-download | By setting this option, RatTeil will pass the resource downloading process and start streaming pre-existing resources. Note that this will stop the stream validation process. |
| --no-validation | By setting this option, the stream validation process will stop. |
| -t, --site | Set the website to stream to. |

*Examples*

1. Run `ratteil -sn 20 -t youtube`. RatTeil will randomly choose 20 surahs, download them, and start streaming them to YouTube.
2. Run `ratteil -R hazza -m 400 -t youtube facebook`. RatTeil will set Hazza as the stream reciter, set the minimum validation value to 400 minutes.
