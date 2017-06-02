# SimpleHTTPSMediaServer

## Installation

requires ink files in a folder in html_files/ink

wget https://github.com/sapo/Ink/releases/download/3.1.10/ink-3.1.10.zip
unzip ink-3.1.10.zip
mv ink-3.1.10 html_files/ink

## Invocation

usage SimpleAuthServer.py [port] [password_file] [.pem file] [media_dir]

- port https default is 443
- password file is a list of 'username:password\n' entries
- .pem file is a .pem file
- media_dir a the media directory

## The Media Directory

```
/media/
├── Formatted Video Title
│   ├── video.mp4
│   ├── splash.jpg
│   └── year.txt
├── Formatted Second Video Title
│   ├── video.mp4
│   ├── splash.jpg
│   └── year.txt
...
```

### Video formats

Use `.mp4` s

ffmpeg is great at generating these
`ffmpeg -i input.anyformat -l lib264 outputfile.mp4`

### year.txt

Just the year. Typically 4 or 5 bytes (with newline)


