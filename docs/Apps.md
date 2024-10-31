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

When an app is installed to its own chroot there is a basic skeleton that exists.
That skeloten is the base (debian) installation. Almost all of the root directory folders are
```--overlay```ed read-only into the chroot. Bubblewrap 0.11.0 (should) supports this. As of writing stable debian only has 0.8.0, so we must provide this seperatly.

In an AppBundle ```AppRun``` Can be a link to a .desktop file, a link to an executable, a shell file,
or a script with a proper shebang.