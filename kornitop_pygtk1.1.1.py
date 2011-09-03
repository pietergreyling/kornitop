#!/usr/bin/env python

'''
Kornitop: Clipboard Notes Manager
Copyright: pietergreyling.com
Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

Simple and corny cross-platform clipboard tracker (to start with...)
Currently built with Python and PyGTK.

BEWARE: By design, text entries from the system clipboard are persisted 
to a file and reloaded upon restart of the application.

Kornitop began life as Kornitop for Windows programmed in Delphi:
http://www.chileserve.net/component/option,com_joomlaboard/Itemid,73/func,listcat/catid,3/lang,en/
http://www.chileserve.net/component/option,com_joomlaboard/Itemid,73/func,view/id,18/catid,4/lang,en/

I wanted to build an open source version using a cross-platform dynamic language and GUI toolkit. 
After much messing around I picked on Python with PyGTK. So far I am pretty happy with this decision.

To get going I used the PyGTK 2.0 Tutorial, section 15.1.5. A Clipboard Example, as a starting point:
http://www.pygtk.org/pygtk2tutorial/
http://www.pygtk.org/pygtk2tutorial/ch-NewInPyGTK2.2.html#sec-ClipboardExample
http://www.pygtk.org/pygtk2tutorial/examples/clipboard.py 
'''

import sys
import os, os.path
import pygtk
if not sys.platform == "win32":
    pygtk.require("2.0")
import gtk
import gobject
import time

class Constants: #-- just a namespace ------------------------------------------
    APP_VERSION = "1.1.1"
    APP_TITLE = "Kornitop: Clipboard Notes Manager"
    APP_TITLE_VERSION = APP_TITLE + " [v." + APP_VERSION + "]"
    APP_ICON = "kornitop_green_bat.png"
    CLIPS_FILENAME = "kornitop_pygtk" + APP_VERSION + ".clips.log"
    NOTES_FILENAME = "kornitop_pygtk" + APP_VERSION + ".notes.log"
    ABOUT_FILENAME = "README"
    STAMP_TAG = "[//STAMP//]"
    STAMP_FILE_WRITE = "[//FILE-WRITE//]"
    STAMP_FORMAT = "[%Y.%m.%d-%H:%M:%S]"

class AppStrings: #-- just a namespace -----------------------------------------
    SNIPS_LABEL_TEXT = "Clipboard Snippets"
    CLIPS_LABEL_TEXT = "Clipboard Log"
    NOTES_LABEL_TEXT = "Notes"
    ABOUT_LABEL_TEXT = "About Kornitop"
    COPY_BUTTON_TEXT = "Copy back to Clipboard"
    SAVE_BUTTON_TEXT = "Save Clipboard and Notes Files"
    SEARCH_BUTTON_TEXT = "Search Clipboard and Notes Files"    

class KornitopFile(object):
    def __init__(self, filename): # file name is mandatory
        self.filename = filename
        self.filepath = os.path.dirname(__file__) + '/' + self.filename
        self.buffer = ''
        self.last_write_text = ''
        self.last_timestamp = ''
        self.load()
    def load(self):
        '''
        Read file entries from file into internal buffer.
        '''
        if os.path.isfile(self.filepath): # check for file existence
        #if sys.version_info < (2, 6):
            try:
                f = open(self.filepath, 'r')
                self.buffer = f.read()
            finally:
                f.close()
        #else:
        #    with open(self.filepath, 'r') as f:
        #        self.buffer = f.read()
        else:
            pass # assume that save will create the file later
    def save(self):
        '''
        Write file entries from internal buffer to file.
        '''
#        with open(self.filepath,'w') as f:
#            self.buffer =  self.timestamp_file_write() + '\n' + self.buffer
#            f.write(self.buffer)
#            f.flush()
        try:
            f = open(self.filepath,'w')
            self.buffer =  self.timestamp_file_write() + '\n' + self.buffer
            f.write(self.buffer)
            f.flush()
        finally:
            f.close()
    def get_buffer(self):
        return self.buffer
    def set_buffer(self, text):
        self.buffer = text
    def write_prepend(self, write_text):
        self.buffer =  self.timestamp() + '\n' + write_text + '\n' + self.buffer
        self.last_write_text = write_text
    def write_append(self, write_text):
        self.buffer =  self.buffer + '\n' + self.timestamp() + '\n' + write_text
        self.last_write_text = write_text
    def write_prepend_new(self, write_text):
        if write_text != self.last_write_text:
            self.write_prepend(write_text)
    def write_append_new(self, write_text):
        if write_text != self.last_write_text:
            self.write_append(write_text)
    def timestamp_file_write(self):
        self.last_timestamp = \
              Constants.STAMP_FILE_WRITE + \
              time.strftime(Constants.STAMP_FORMAT, time.localtime())
        return self.last_timestamp
    def timestamp(self):
        self.last_timestamp = \
              Constants.STAMP_TAG + \
              time.strftime(Constants.STAMP_FORMAT, time.localtime())
        return self.last_timestamp
    def timestamp_no_tag(self):
        return time.strftime(Constants.STAMP_FORMAT, time.localtime())

class KorniClips(KornitopFile):
    ''' Manages the persistence of kornitop clipboard data to and from a text file. '''
    pass

class KorniNotes(KornitopFile):
    ''' Manages the persistence of kornitop notes data to and from a text file. '''
    pass

class KorniAbout(KornitopFile):
    ''' Displays kornitop README text file. '''
    pass

class ClipboardInfo:
    def __init__(self):
        self.text = ''

class KornitopMain(object):
    def __init__(self):
        self.app_dir = os.path.dirname(__file__) # + '/' + "any_filename"
        self.app_icon = self.app_dir + '/' + Constants.APP_ICON
        #-- init clipboard log -------------------------------------------------
        self.korniclips = KorniClips(filename = Constants.CLIPS_FILENAME)
        self.korninotes = KorniNotes(filename = Constants.NOTES_FILENAME)
        self.korniabout = KorniNotes(filename = Constants.ABOUT_FILENAME)
        self.clipboard_text_received_last = ''

        #-- init the main window of the application ----------------------------
        self.window = gtk.Window()
        self.window.set_title(Constants.APP_TITLE_VERSION)
        self.window.connect("destroy", lambda w: gtk.main_quit())
        self.window.set_border_width(1)
        try: #-- application icon ----------------------------------------------
            self.window.set_icon_from_file(self.app_icon)
        except Exception, e:
            print e.message
            #sys.exit(1) #-- let it pass

        #-- set up gui etc. ----------------------------------------------------
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.window.add(self.notebook)

        #-- add pages to notebook ----------------------------------------------
        self.snips_hbox = gtk.HBox()
        self.snips_label = gtk.Label(AppStrings.SNIPS_LABEL_TEXT)
        self.clips_hbox = gtk.HBox()
        self.clips_label = gtk.Label(AppStrings.CLIPS_LABEL_TEXT)
        self.notes_hbox = gtk.HBox()
        self.notes_label = gtk.Label(AppStrings.NOTES_LABEL_TEXT)
        self.about_hbox = gtk.HBox()
        self.about_label = gtk.Label(AppStrings.ABOUT_LABEL_TEXT)
        self.notebook.insert_page(self.snips_hbox, self.snips_label)
        self.notebook.insert_page(self.clips_hbox, self.clips_label)
        self.notebook.insert_page(self.notes_hbox, self.notes_label)
        self.notebook.insert_page(self.about_hbox, self.about_label)

        self.num_buttons = 20
        self.buttons = self.num_buttons * [None]
        self.clipboard_history = self.num_buttons * [None]

        vbbox = gtk.VButtonBox()
        vbbox.show()
        vbbox.set_layout(gtk.BUTTONBOX_START)

        # display (show) the notebook and tabs ---------------------------------
        self.snips_hbox.pack_start(vbbox, False)
        self.snips_hbox.show()
        self.clips_hbox.show()
        self.notes_hbox.show()
        self.about_hbox.show()
        self.notebook.show()

        self.button_tips = gtk.Tooltips()
        for i in range(self.num_buttons):
            self.buttons[i] = gtk.Button("---")
            self.buttons[i].set_use_underline(False)
            #!!!self.buttons[i].set_width(100)
            vbbox.pack_start(self.buttons[i])
            self.buttons[i].show()
            self.buttons[i].connect("clicked", self.clicked_cb)

        # build snips textview -------------------------------------------------
        self.build_snips_view()

        # build and load clips textview ----------------------------------------
        self.build_clips_view()
        self.load_clips_view()

        # build and load korninotes textview -----------------------------------
        self.build_notes_view()
        self.load_notes_view()

        # build and load about textview -----------------------------------
        self.build_about_view()
        self.load_about_view()

        # display window -------------------------------------------------------
        self.snips_hbox.pack_start(self.snips_vbox)
        self.window.add(self.snips_hbox)
        self.clips_hbox.pack_start(self.clips_vbox)
        self.window.add(self.clips_hbox)
        self.notes_hbox.pack_start(self.notes_vbox)
        self.window.add(self.notes_hbox)
        self.about_hbox.pack_start(self.about_vbox)
        self.window.add(self.about_hbox)
        self.window.show()

        #-- hook up system clipboard -------------------------------------------
        self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
        self.clipboard.request_text(self.clipboard_text_received)
        gobject.timeout_add(1500, self.fetch_clipboard_info)

        return

    def build_snips_view(self):
        #-- build snips textview -----------------------------------------------
        self.snips_vbox = gtk.VBox()
        self.snips_vbox.show()
        self.snips_scrolledwin = gtk.ScrolledWindow()
        self.snips_scrolledwin.show()
        self.snips_textview = gtk.TextView()
        self.snips_textview.show()
        self.snips_textview.set_size_request(400,600)
        self.snips_textview.set_wrap_mode(gtk.WRAP_CHAR)
        self.snips_textbuffer = self.snips_textview.get_buffer()
        self.snips_scrolledwin.add(self.snips_textview)
        self.snips_vbox.pack_start(self.snips_scrolledwin)
        cmd_copy = gtk.Button(AppStrings.COPY_BUTTON_TEXT)
        cmd_copy.show()
        cmd_copy.connect('clicked', self.set_clipboard)
        self.snips_vbox.pack_start(cmd_copy, False)
        #-- 'save' button to flush buffers to files ----------------------------
        cmd_snips_save = gtk.Button(AppStrings.SAVE_BUTTON_TEXT)
        cmd_snips_save.show()
        cmd_snips_save.connect('clicked', self.save_files)
        self.snips_vbox.pack_start(cmd_snips_save, False)

    def build_clips_view(self):
        #-- build clips textview -----------------------------------------------
        self.clips_vbox = gtk.VBox()
        self.clips_vbox.show()
        self.clips_scrolledwin = gtk.ScrolledWindow()
        self.clips_scrolledwin.show()
        self.clips_textview = gtk.TextView()
        self.clips_textview.show()
        self.clips_textview.set_size_request(400,600)
        self.clips_textview.set_wrap_mode(gtk.WRAP_CHAR)
        self.clips_textbuffer = self.clips_textview.get_buffer()
        self.clips_scrolledwin.add(self.clips_textview)
        self.clips_vbox.pack_start(self.clips_scrolledwin)
        #-- 'search' text entry field to find in file buffers ------------------
        self.txt_clips_search_for = gtk.Entry()
        self.txt_clips_search_for.show()
        self.clips_vbox.pack_start(self.txt_clips_search_for, False)
        #-- 'search' button to find text in file buffers -----------------------
        cmd_clips_search = gtk.Button(AppStrings.SEARCH_BUTTON_TEXT)
        cmd_clips_search.show()
        cmd_clips_search.connect('clicked', self.search_clips_file)
        self.clips_vbox.pack_start(cmd_clips_search, False)
        #-- 'save' button to flush buffers to files ----------------------------
        cmd_clips_save = gtk.Button(AppStrings.SAVE_BUTTON_TEXT)
        cmd_clips_save.show()
        cmd_clips_save.connect('clicked', self.save_files)
        self.clips_vbox.pack_start(cmd_clips_save, False)

    def build_notes_view(self):
        #-- build korninotes textview ------------------------------------------
        self.notes_vbox = gtk.VBox()
        self.notes_vbox.show()
        self.notes_scrolledwin = gtk.ScrolledWindow()
        self.notes_scrolledwin.show()
        self.notes_textview = gtk.TextView()
        self.notes_textview.show()
        self.notes_textview.set_size_request(400,600)
        self.notes_textview.set_wrap_mode(gtk.WRAP_CHAR)
        self.notes_textbuffer = self.notes_textview.get_buffer()
        self.notes_scrolledwin.add(self.notes_textview)
        self.notes_vbox.pack_start(self.notes_scrolledwin)
        #-- 'save' button to flush buffers to files ----------------------------
        cmd_notes_save = gtk.Button(AppStrings.SAVE_BUTTON_TEXT)
        cmd_notes_save.show()
        cmd_notes_save.connect('clicked', self.save_files)
        self.notes_vbox.pack_start(cmd_notes_save, False)

    def build_about_view(self):
        #-- build korninotes textview ------------------------------------------
        self.about_vbox = gtk.VBox()
        self.about_vbox.show()
        self.about_scrolledwin = gtk.ScrolledWindow()
        self.about_scrolledwin.show()
        self.about_textview = gtk.TextView()
        self.about_textview.show()
        self.about_textview.set_size_request(400,600)
        self.about_textview.set_wrap_mode(gtk.WRAP_CHAR)
        self.about_textbuffer = self.about_textview.get_buffer()
        self.about_scrolledwin.add(self.about_textview)
        self.about_vbox.pack_start(self.about_scrolledwin)

    def load_clips_view(self):
        self.clips_textbuffer.set_text( self.korniclips.get_buffer() )

    def load_notes_view(self):
        self.notes_textbuffer.set_text( self.korninotes.get_buffer() )

    def load_about_view(self):
        self.about_textbuffer.set_text( self.korniabout.get_buffer() )

    #-- flush entries to files -------------------------------------------------
    def save_clips_file(self):
        self.synch_clips_file_buffer()
        self.korniclips.save()
        self.load_clips_view() # reload the view

    def save_notes_file(self):
        self.synch_notes_file_buffer()
        self.korninotes.save()
        self.load_notes_view() # reload the view

    def save_files(self, button):
        self.save_clips_file()
        self.save_notes_file()
        self.window.set_title( \
            "{0} [saved: {1}]".format( \
                Constants.APP_TITLE_VERSION, self.korniclips.timestamp_no_tag()))
        
    def search_clips_file(self, button):
        '''
        search_str =  self.text_to_find.get_text()
        start_iter =  textbuffer.get_start_iter()
        # don't need these lines anymore
        #match_start = textbuffer.get_start_iter() 
        #match_end =   textbuffer.get_end_iter() 
        found =       start_iter.forward_search(search_str,0, None) 
        if found:
            match_start,match_end = found #add this line to get match_start and match_end
            textbuffer.select_range(match_start,match_end)       
        '''
        text_to_search_for = self.txt_clips_search_for.get_text()
        textbuffer_to_search_in = self.clips_textbuffer
        start_iter = textbuffer_to_search_in.get_start_iter()
        try:
            found = start_iter.forward_search(text_to_search_for, 0, None)
            if found:
                match_start, match_end = found
                textbuffer_to_search_in.select_range(match_start,match_end)               
        except:
            pass

    #-- synchronize gui and file buffers ---------------------------------------
    def synch_clips_file_buffer(self):
        '''
        Copies data from GUI text view buffer to korninotes file object buffer.
        '''
        self.korniclips.set_buffer( \
            self.clips_textbuffer.get_text(*self.clips_textbuffer.get_bounds()))

    def synch_notes_file_buffer(self):
        '''
        Copies data from GUI text view buffer to korninotes file object buffer.
        '''
        self.korninotes.set_buffer( \
            self.notes_textbuffer.get_text(*self.notes_textbuffer.get_bounds()))

    #-- update button label and tooltips ---------------------------------------
    def update_buttons(self):
        for i in range(len(self.clipboard_history)):
            info = self.clipboard_history[i]
            if info:
                button = self.buttons[i]
                if info.text:
                    button.set_label(' '.join(info.text[:24].split('\n')))
                if info.targets:
                    # put target info in button tootip
                    self.button_tips.set_tip(button, info.targets)
        return

    #-- signal handler called when clipboard returns target data ---------------
    def clipboard_targets_received(self, clipboard, targets, info):
        if targets:
            # have to remove dups since Netscape is broken
            targ = {}
            for t in targets:
                targ[str(t)] = 0
            targ = targ.keys()
            targ.sort()
            info.targets = '\n'.join(targ)
        else:
            info.targets = None
            print 'No targets for:', info.text
        self.update_buttons()
        return

    #-- signal handler called when the clipboard returns text data -------------
    def clipboard_text_received(self, clipboard, text, data):
        if not text or text == '':
            return
        cbinfo = ClipboardInfo()
        cbinfo.text = text
        # log to logger
        self.korniclips.write_prepend_new(text)
        if text != self.clipboard_text_received_last:
            clips_text = self.clips_textbuffer.get_text(*self.clips_textbuffer.get_bounds())
            self.clips_textbuffer.set_text( self.korniclips.timestamp() + '\n' + \
                                            text + '\n' + \
                                            clips_text)
            self.clipboard_text_received_last = text
        # prepend and remove duplicate
        history = [info for info in self.clipboard_history
                   if info and info.text<>text]
        self.clipboard_history = ([cbinfo] + history)[:self.num_buttons]
        self.clipboard.request_targets(self.clipboard_targets_received, cbinfo)
        return

    # display the clipboard history text associated with the button
    def clicked_cb(self, button):
        i = self.buttons.index(button)
        try:
            if self.clipboard_history[i]:
                self.snips_textbuffer.set_text(self.clipboard_history[i].text)
            else:
                self.snips_textbuffer.set_text('')
        except:
            pass #-- for now
        return

    # get the clipboard text
    def fetch_clipboard_info(self):
        self.clipboard.request_text(self.clipboard_text_received)
        return True

    def set_clipboard(self, button):
        text = self.snips_textbuffer.get_text(*self.snips_textbuffer.get_bounds())
        self.clipboard.set_text(text)
        return

    def main(self):
        '''
        All PyGTK applications must have a gtk.main(). Control ends here
        and waits for an event to occur (like a key press or mouse event).
        '''
        gtk.main()
        # flush entries to files -----------------------------------------------
        self.save_files(None)
        return 0

    def destroy(self, widget, data=None):
        gtk.main_quit()

if __name__ == '__main__':
    kornitop = KornitopMain()
    kornitop.main()
