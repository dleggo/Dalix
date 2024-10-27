# FAQ

## What makes Kadota different
Kadota ditches FHS as much as possible and implements human readable names like ```System```, ```Applications```, etc.
Another thing worth noting is that while Kadota uses these paths, it can install debian packages quite nativly. This
works by having ```kadotad``` running in the background monitering for changes in ```Applications```, and packaging .debs in its native format.
More info in [Misc](Misc.md)
