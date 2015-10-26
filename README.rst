====================
Remember The Rhythm
====================

A plugin for rhythbox to remember last playing song and playback time.

Fork - these are the improvements:

 - python3 - for Rhythmbox 3.0 and later
 - start up paused if the music was paused when rhythmbox was shutdown
 - start up playing if the music was playing
 - configurable startup options via plugin-preferences

under development

probably will include the ability to 
 
 - better remember the playlist/source that the music was playing

-------------
Requirements
-------------

Rhythmbox 3 or above

-------------
Installation
-------------


Ubuntu Repository
~~~~~~~~~~~~~~~~~~

sudo add-apt-repository ppa:fossfreedom/rhythmbox-plugins
sudo apt-get update
sudo apt-get install rhythmbox-plugin-remember-the-rhythm


From Source
~~~~~~~~~~~~

Install:
````````

::

    ./install.sh

Remove
```````

::

     ./install.sh --uninstall

Note: This is a fork from the original project which appears to have been abandoned.  I've requested an update from the original maintainer but to-date no answer has been forthcoming.
