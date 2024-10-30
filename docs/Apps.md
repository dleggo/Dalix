# Applications

## App Bundle Structure
For an example package of LibreOffice
```
/Applications/LibreOffice.app/
├── app-info
├── AppRun -> chroot/usr/bin/...
├── icon.png
└── chroot
	├── usr
	│	└── ...
	└── ... (basically a pkg installed to a chroot)
```

When an app is installed to this chroot there is a basic skeleton that exists.
That skeloten is the base (debian) installation. Almost all of the root directory folders are
mounted read-only into the chroot. So for example.



In an AppBundle ```AppRun``` Can be a link to a .desktop file, a link to an executable, a shell file,
or a script with a proper shebang.