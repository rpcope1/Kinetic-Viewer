Kinetic-Viewer
==============

This is some basic viewer software for the upcoming Seagate Kinetic drives. This is based upon the Seagate Kinetic preview library: https://github.com/Seagate/Kinetic-Preview and is written in Python. The viewer provides a GUI for viewing drives contents and interacting with the drive, providing engineers and developers with a simpler visualization of drive contents. While this program has some limitations, I believe this provides an excellent diving in point (and diagnostic tool) for the Kinetic platform. 

Among the features available or planned: 
-Displays a list of all keys on the drive.
-View the value for any of keys on the drive, simply by selecting the key.
-Copy-to-clipboard buttons for any selected key or value
-Graphical "Put" for easily putting new content to the drive.
-Graphically delete any selected key:value pair from the drive.
-Easy "erase entire drive" button for clearing everything.
-Graphical display of drive logs.
-Graphical ability to load new firmware onto the drive.
-Settings to display keys and values as either hex or ASCII.


The Kinetic Viewer software requires the host PC to have Python 2.7 installed, and for the Tkinter and Kinetic software libraries to be added. Kinetic Viewer can be launched by calling from the command line:

python KeyViewer.py

-OR-

Doubling clicking the script.

Please feel free to submit bugs/comments/suggestions.
As of 1/30/14 the Viewer is still very much in the Alpha state of development.
