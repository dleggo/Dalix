# Misc

> Clarification note: ```Package``` is used to describe a system package. ```Application``` is used
> to describe a user installed application. ```libsqsh``` is a system package. ```LibreOffice```
> is an application. Just to get that out of the way. ```:)```

## A good OS should...
1. Be usable by a 4 year old
2. Be easily managable (Apps, settings, etc)
3. Have wide package availibility
4. Have backward compatability (lots!)
5. Look nice
6. **Never** require the terminal (though it should exist)
7. Have a global menu bar
8. Handle an app existing in multiple versions
9. Be stable
10. Have understandable folder names

## Dalix will attempt to implement this in the following ways
1. Making a custom DE
2. Using AppBundles, and having simple and straight to the point settings
3. Port Linux apps, and if a user tries to install a .deb file it should automatically generate an AppBundle for it
4. FIXME
5. Mac OS like theme
6. Have a graphical tool for ***many*** config options (but not too many)
7. TODO
8. Use AppBundles
9. FIXME
10. Solved by dalixd


## When a user drags a ```.deb``` File into ```/Applications```

```dalixd``` will recognize it and extract the deb into ```tmp/*``` where ```*``` is the name and
version of the package. It will then simulate installation into a chroot. ```tmp/*/chroot``` Then it
will read the dependencies of the application, and place that in its own meta-data file alongside
other important information. It then copies ```tmp/*``` into ```/Applications/*.app``` Each of these
steps will get described in more detail

> ## **Implementation detail.**
> When ```dalixd``` converts a .deb into a AppBundle it creates ```AppRun``` point to the ```.desktop```
> file in ```/usr/share/applications/``` If there is multiple ```.desktop``` files there or if there
> are non then ```dalixd``` will display an error message saying "**Error installing app *. Multiple
> Desktop files exist. This functionality is planned to be implemented in the future. Sorry for the
> inconvenience.**"

### To recognize the .deb
```dalixd``` will use ```watchdog``` to moniter  the directory and will display a message informing
the user that the app will be converted so it can be used.


## Developer information

Applications are not aware of each other, but packages are.

[Applications](Apps.md)

[Packages](Pkgs.md)

### Base FS heiarchy.

```
/
├── Applications
│	└── LibreOffice
├── System
│	├── Packages
│	│	└── libsqsh***1.2.3
│	└── Config
└── Volumes
	└── USB3.0
```