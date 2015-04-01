## Simple and corny cross-platform clipboard tracker (to start with...) ##
Currently built with Python and PyGTK.

You should only need these PyGTK runtimes:

For Mac OSX - http://sourceforge.net/projects/macpkg/files/PyGTK

For Win GTK - http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/

For Ubuntu  - should already be there in good stead

Others      - please check according to your distro

BEWARE: By design, text entries from the system clipboard are persisted to a file and reloaded upon restart of the application.

Kornitop began life as Kornitop for Windows programmed in Delphi:

http://www.chileserve.net/component/option,com_joomlaboard/Itemid,73/func,listcat/catid,3/lang,en/

http://www.chileserve.net/component/option,com_joomlaboard/Itemid,73/func,view/id,18/catid,4/lang,en/

I wanted to build an open source version using a cross-platform dynamic language and GUI toolkit. After much messing around I picked on Python with PyGTK. So far I am pretty happy with this decision.

To get going I used the PyGTK 2.0 Tutorial, section 15.1.5. A Clipboard Example, as a starting point:

http://www.pygtk.org/pygtk2tutorial/

http://www.pygtk.org/pygtk2tutorial/ch-NewInPyGTK2.2.html#sec-ClipboardExample

http://www.pygtk.org/pygtk2tutorial/examples/clipboard.py
