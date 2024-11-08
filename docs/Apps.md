# Applications

## App Bundle Structure
For an example package of LibreOffice
```
/Applications/LibreOffice.app/
├── info
├── AppRun -> chroot/usr/bin/...
├── icon.png
└── chroot
	├── usr
	│	└── ...
	└── ... (basically a pkg installed to a chroot)
```

## Metadata file
```toml
# ./info

# currently only type 1 description files are supported.
info-type = 1

# Neccesary fields
[main]

name = "Your App Name"
version = "4.5.6.7"
developer = "You/Your company's name"
description = '''
The first line is the short description.
All the other lines are a description
which can span multiple lines.
'''

dependencies = '''
libsqsh==1.2.3
python>=3.10
joy
happiness
love
etc.
'''
```

Bubblewrap 0.11.0 supports overlaying FSs. As of writing stable debian only has 0.8.0, so we must provide this seperatly.

In an AppBundle ```AppRun``` Can bee link to an executable, a shell file, or a script with a
proper shebang.