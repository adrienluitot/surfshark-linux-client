import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import time


class LogWindow(Gtk.Window):
    def __init__(self, main):
        Gtk.Window.__init__(self, title="SurfShark Client")
        self.set_default_size(510, 720)
        self.set_resizable(False)
        self.move(400, 200)
        self.set_icon_from_file("surfshark_linux_client.png")

        self.log_container = Gtk.VBox()
        self.add(self.log_container)

        self.hbox = Gtk.HBox()
        self.log_container.pack_start(self.hbox, True, True, 0)

        self.vbox = Gtk.VBox()
        self.hbox.pack_start(self.vbox, True, True, 25)

        self.vbox.pack_start(Gtk.Label(), True, True, 0)

        self.password_label = Gtk.Label()
        self.password_label.set_markup("Password")
        self.password_label.get_style_context().add_class('label')
        self.vbox.pack_start(self.password_label, False, False, 0)

        self.password = Gtk.Entry()
        self.password.set_placeholder_text("Password")
        self.password.connect("activate", main.log_action)
        self.password.set_visibility(False)
        self.vbox.pack_start(self.password, False, False, 0)

        if not main.config['registered']:
            self.vbox.pack_start(Gtk.Label(), False, False, 0)

            self.confirm_password_label = Gtk.Label()
            self.confirm_password_label.set_markup("Confirm Password")
            self.confirm_password_label.get_style_context().add_class('label')
            self.vbox.pack_start(self.confirm_password_label, False, False, 0)

            self.confirm_password = Gtk.Entry()
            self.confirm_password.set_placeholder_text("Confirm Password")
            self.confirm_password.connect("activate", main.log_action)
            self.confirm_password.set_visibility(False)
            self.vbox.pack_start(self.confirm_password, False, False, 0)

        button_container = Gtk.HBox()
        button_container.pack_start(Gtk.Label(), True, True, 0)
        log_button_text = "Log in" if main.config['registered'] else "Register"
        self.log_button = Gtk.Button(label=log_button_text)
        self.log_button.connect("clicked", main.log_action)
        self.log_button.connect("enter-notify-event", self.hover)
        self.log_button.connect("leave-notify-event", self.not_hover)
        button_container.pack_start(self.log_button, False, False, 0)
        button_container.pack_start(Gtk.Label(), True, True, 0)
        self.vbox.pack_start(button_container, False, False, 30)

        if(not main.config['registered']):
            or_label = Gtk.Label('OR')
            or_label.get_style_context().add_class('or-label')
            self.vbox.pack_start(or_label, False, False, 20)

            self.log_without_pass_button = Gtk.Button(label="Don't use password")
            self.log_without_pass_button.connect("clicked", main.log_action)
            self.log_without_pass_button.connect("enter-notify-event", self.hover)
            self.log_without_pass_button.connect("leave-notify-event", self.not_hover)
            self.vbox.pack_start(self.log_without_pass_button, False, False, 30)

        self.vbox.pack_start(Gtk.Label(), True, True, 0)

    def hover(self, listbox_widget, crossing):
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def not_hover(self, listbox_widget, crossing):
        self.get_window().set_cursor(None)

    def animate_loader(self):
        while True:
            if (not self.load): break

            time.sleep(0.8)
            curr_points = self.loading_label_points.get_text()
            if(curr_points == "..."):
                self.loading_label_points.set_text("   ")
            else:
                n = 0
                new_points = "."
                for c in curr_points:
                    if (c == "."):
                        n += 1
                        new_points += "."
                for i in range(1, 3 - n):
                    new_points += " "

                self.loading_label_points.set_text(new_points)
