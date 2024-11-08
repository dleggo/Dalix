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
InfoType = 1

# Neccesary fields
[App]

Name = "Your App Name"
Version = "4.5.6.7"
Maintainer = "You/Your company's name"
# Arch can be any arch in the form of Debians arch field e.g. amd64 arm64 i386 etc.
Arch = "any"
Description = '''
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