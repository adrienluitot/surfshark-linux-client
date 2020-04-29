import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class Popup(Gtk.Window):
    def __init__(self, title, message, parent=None):
        Gtk.Window.__init__(self, title=title)
        self.set_resizable(False)

        hbox = Gtk.HBox()
        self.add(hbox)

        vbox = Gtk.VBox()
        hbox.pack_start(vbox, False, False, 20)

        message_label = Gtk.Label()
        message_label.set_label(message)
        vbox.pack_start(message_label, False, False, 25)

        self.show_all()
        self.hide()

        if(parent == None):
            screen = self.get_display()
            monitor_size = screen.get_monitor_at_window(Gdk.get_default_root_window()).get_geometry()
            self.move(monitor_size.width / 2 - self.get_size().width / 2,
                      monitor_size.height / 2 - self.get_size().height / 2)
        else:
            self.move(parent.get_position().root_x + parent.get_size().width/2 - self.get_size().width/2,
                      parent.get_position().root_y + parent.get_size().height/2 - self.get_size().height/2)

        self.show_all()
