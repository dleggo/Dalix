# Misc

## A good OS should...
1. Be usable by a 4 year old
2. Be easily managable (Apps, settings, etc)
3. Have wide package availibility
4. Have backward compatability (lots!)
5. Look nice
6. **Never** require the terminal (tho it should exist)
7. Have a global menu bar
8. Handle an app existing in multiple versions
9. Be stable
10. Have understandable folder names

## Kadota will attempt to implement this in the following ways
1. Making a custom DE
2. Using AppBundles, and having simple and straight to the point settings
3. Port Linux apps, and if a user tries to install a .deb file it should automatically generate an AppImage for it
4. FIXME
5. Mac OS like theme
6. Have a graphical tool for ***many*** config options (but not too many)
7. TODO
8. Use AppBundles
9. FIXME
10. TODO


## When a user drags a ```.deb``` File into their ```Applications```

```falkond``` will recognize it and extract the deb into ```tmp/*``` where ```*``` is the name and
version of the package. It will then simulate installation into a chroot. ```tmp/*/chroot``` Then

