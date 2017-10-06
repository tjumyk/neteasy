<img align="right" src="neteasy/static/image/logo-64.png"/>

# NetEasy Music Player

## Introduction

This is a simple yet useful web app that allow you to play the **cached songs** from [NetEase Cloud Music (网易云音乐)](http://music.163.com) client program.

It is really annoying when you have a lot of cached music files but are not able to play them when you are **offline**.

## System Support

Currently, we support **Windows 10** and **Ubuntu 16.04**. 

However, the support for MacOS seems not hard to implement. Welcome to contribute! :smile: 

## Disclaimer

- This web application only uses the local cached files and extracts the music meta data from the public web pages.
- There is no decryption or hacking in the source code to access some data or files with illegal intentions. 
- The copyrights of the music files and the music meta data belong to NetEase Cloud Music.
- There is no warranty about the quality and usability of the source code due to the potential changes in the NetEase Cloud Music client program or its official website.
- Last but not least, this is only a hobby project. Do not be too serious and just enjoy the music (and the code, if you like).  

## How-To-Run

1. Install system-specific dependencies
   1. **Windows**: no need to install anything at this step
   2. **Linux**: `PyGObject` is required, please refer to [this documentation](https://pygobject.readthedocs.io/en/latest/getting_started.html) for installment instructions
   3. **MacOS**: currently unknown
2. Prepare a virtual environment with **Python 3** (use `virtualenv -p python3 --system-site-packages ...`)
3. Activate the virtual environment
4. Navigate to the **root folder** of this repo
5. Install the dependencies by `pip install -r requirements.txt`
6. Change the configurations in `config.json` if required
7. Start the server via `python start.py`

## Screenshot

![screenshot](screenshot.png)

## License

The MIT License (MIT)

Copyright (c) 2017 Yukai (Kelvin) Miao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

