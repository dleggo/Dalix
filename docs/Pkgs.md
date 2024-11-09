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
DepsIncluded = false

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
libsqsh (>= 1.2.3),
python (>= 3.10),
joy,
happiness,
love,
etc.
'''

# For use in automated scripts so there only has to be one meta-data file
[Other]
```

## When (a) package(s) are/is pulled in by an app.

First, all of the packages are added to a list of needed ones, this prevents recursion issues. Then,
in an involved process, ```pkg``` calulates ```bwrap``` arguments. This process goes as follows.

 - First, We ```overlay``` the base system read-only with a tmpfs overtop so we can bind mount without
	changing the base system. e.g.
```
	...
	--overlay-src /
	--tmp-overlay /
	...
```
 - Then we bind mount the ```System```, ```Users```, and ```Volumes```.

 ```
	--bind /System /System
	--bind /Users /Users
	--bind /Volumes /Volumes
 ```

 - Then we develop a tree of all the files and folders that need to be symlinked, along with their
	occurence count. As a bare minimum example.

 ```
 usr             = 2
 usr/bin         = 2
 usr/bin/bwrap   = 1
 usr/bin/bash    = 1
 usr/share/bwrap = 1
 usr/share/bash  = 1
 ```
> Any files or folders that have an occurence count of 1 can be symlinked. For files with an occurence
> count greater then 1, the file closest to the main package in the dependency tree will be chosen.
> For folders with an occurence count greater then 1, they will be created in the argument list
 - Then we symlink those. For example

```
	--mkdir usr
	--mkdir usr/bin
	--mkdir usr/share
	--symlink /System/Packages/bubblewrap0.11.0/chroot/usr/bin/bwrap /usr/bin/bwrap
	--symlink /System/Packages/bash5.6.7/chroot/usr/bin/bash /usr/bin/bash
	--symlink /System/Packages/bubblewrap0.11.0/chroot/usr/share/bubblewrap /usr/share/bubblewrap
	--symlink /System/Packages/bash5.6.7/chroot/usr/share/bash /usr/share/bash
```

> Potentially, if the cost of preforming the symlinks for every package/application gets to high, a
> static solution may have to be implemented. For now it will be done for each package/application.

> Also, there is a special package in the system called ```base```, it is not the system but rather
> a special package that is pulled in by all the others, it is nothing more then a pkg-info and
> an empty chroot. An application with sufficient privalages, can add itself/another package
> to ```base```'s dependencies, to get automatically pulled in. For instance, an application
> installing a font, would create a package for the font, and add it into ```base```'s deps.