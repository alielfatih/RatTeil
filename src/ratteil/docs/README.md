RatTeil
=======
**RatTeil** is a python app to stream the Holly Quran to YouTube.

Streaming the Holly Quran to YouTube now is easier than ever before, install RatTeil run it then step back RatTeil will do the rest. 

RatTeil will auto/manually choose reciters and surahs for each stream, download the required audio files and start streaming them.

How to install on
-----------------

### Android
1. Install Termux app.
2. Run *pkg update -y*.
3. Then *pkg install python wget ffmpeg -y*.
4. Then *python -m pip install ratteil*.
5. Run *ratteil -h* to see availables options.

### Linux, Debian, etc

1. Run *apt-get update -y*
2. Then *apt-get install python wget ffmpeg -y*
3. Then *python -m pip install ratteil*
4. Run *ratteil -h* to see availables options.

Or 

1. clone ratteil repo change to ratteil folder.
2. Run *sh install.sh*.
3. Run *python __main__.py -h* to see options.

Or 

1. download ratteil package from github or PyPI
2. install requirements *apt-get install python ffmpeg wget -y*.
3. Run *python -m pip install <ratteil_package_file_path>*

Quick start
------------

before running this command make sure you put your images/videos that will be used as stream background under.
> *~/RatTeil-resources/imgs/*

and your video introduction and conlusion under 
> *~/RatTeil-resources/fixer/*

file names must be introduction.mp4 and conlusion.mp4

1. Run *python -m pip install ratteil*
2. Run *ratteil -t youtube*
3. copy authentication links 
4. Follow google authentication link
5. Enter the authentication code/token and verfiy your authority.
6. Done; stream'll start in view moments.
7. visit your YouTube channel or Facebook page to see your stream.

RatTeil available commands and options
--------------------------------------
```console
usage: ratteil [-h] [-l] [-m] [-ms] [-n] [-R [...]] [-r] [-sn] [-s] [--no-download] [--no-validation] -t [...]
```


Command      | Description
--------     | -----------
-h, --help   | show help message.
-l, --list   | list all available reciters .
-m, --min    | set the minimum length for stream validation in minutes; by default it will be 120 minutes = 2 hours.
-ms, --streams |   set the number of streams per run;  ``Note each stream will be 75 minute or less.`` this value will automatically recalculate the minimum stream length for validation. 
-n,            | set the number of reciters per stream; by default it be randomly between 3-7.
-R, --reciter  | manually choose stream reciter/reciters.
-r, --resume   | Coming soon.
-sn,           | set the number of surahs per stream; by default it will be randomly between 20-50.
--no-download  | by setting this option RatTeil will pass resources downloading process and start stream the pre-exist resources. ``Note this will stop stream validation process.``
--no-validation  | by setting this stream validation process will stop.
-t, --sitea    | set the website that want to stream to.


### Examples
1. Run *ratteil -sn 20 -t youtube*.
<br>RatTeil will randomly choose 20 surahs, download them and start streaming them to youtube.
2. Run *ratteil -R hazza -m 400 -t youtube facebook*.
RatTeil will set Hazza as the stream reciter; the minimum validation value to 400 minutes and start <s></s>tream to both facebook and youtube.

Coming feature 
-------------- 
  1. Stream to facebook