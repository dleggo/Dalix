# Packages

## Pkg Bundle Structure
For an example package of libsqsh
```
/System/Packages/libsqsh.pkg/
├── pkg-info
└── chroot
	├── usr
	│	└── ...
	└── ... (basically an app installed to a chroot)
```

## Metadata file
```toml
# ./pkg-info

# currently only type 1 description files are supported.
info-type = 1

# Neccesary fields
[pkg]

name = "Your Package Name"
version = "4.5.6.7"
arch = "Arch in the same format as debians e.g. amd64 arm64 etc."
maintainer = "You/Your company's name"
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

# For use in automated scripts so there only has to be one meta-data file
[other]
```