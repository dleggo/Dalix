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
InfoType = 1

# Neccesary fields
[Package]

Name = "Your Package Name"
Version = "4.5.6.7"
Arch = "Arch in the same format as debians e.g. amd64 arm64 etc."
Maintainer = "You/Your company's name"
Description = '''
The first line is the short description.
All the other lines are a description
which can span multiple lines.
'''

Dependencies = '''
libsqsh==1.2.3
python>=3.10
joy
happiness
love
etc.
'''

# For use in automated scripts so there only has to be one meta-data file
[Other]
```