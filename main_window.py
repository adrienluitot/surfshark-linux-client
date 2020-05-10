import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango

import os.path
import urllib.request


class MainWindow(Gtk.Window):
    def __init__(self, main):
        Gtk.Window.__init__(self, title="SurfShark Client - App")
        self.set_default_size(510, 720)
        self.set_resizable(False)
        self.set_icon_from_file(main.folder_path + "surfshark_linux_client.png")

        self.main = main

        h_parent = Gtk.HBox(spacing=1)
        self.add(h_parent)

        self.tabs = Gtk.Notebook()
        self.tabs.connect("enter-notify-event", self.hover)
        self.tabs.connect("leave-notify-event", self.not_hover)
        h_parent.pack_start(self.tabs, True, True, 0)

        # ================================
        # Servers
        # ================================
        servers_container = Gtk.VBox(spacing=0)
        self.tabs.append_page(servers_container)
        self.tabs.set_tab_label_text(servers_container, "Servers")
        self.tabs.child_set_property(servers_container, 'tab-expand', True)

        self.server_list = Gtk.ListBox()
        self.server_list.connect("enter-notify-event", self.hover)
        self.server_list.connect("leave-notify-event", self.not_hover)
        self.server_list.connect("selected-rows-changed", self.select_server)

        servers_scroll = Gtk.ScrolledWindow()
        servers_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        servers_scroll.add_with_viewport(self.server_list)
        servers_container.pack_start(servers_scroll, True, True, 0)

        i = 0
        for server in self.main.servers:
            if (server['type'] == "double" or server['type'] == "static"): continue
            vpn_server = Gtk.HBox()
            image = Gtk.Image()

            flag_array = server['flagUrl'].split('/')
            if (not os.path.isfile(main.folder_path + 'flags/' + flag_array[len(flag_array) - 1])):
                opener = urllib.request.build_opener()
                opener.addheaders = [
                    ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(server['flagUrl'], main.folder_path + "flags/" + flag_array[len(flag_array) - 1])

            image.set_from_file(main.folder_path + 'flags/' + flag_array[len(flag_array) - 1])
            vpn_server.pack_start(image, False, False, 10)

            city = Gtk.Label(server['country'] + ', ' + server['location'])
            vpn_server.pack_start(city, True, True, 20)

            load = Gtk.Label(str(server['load']) + "%")
            vpn_server.pack_start(load, False, False, 20)
            self.server_list.insert(vpn_server, i)
            self.main.config_files[server['country'] + ', ' + server['location']] = server['connectionName']
            i += 1


        bottom = Gtk.HBox(spacing=0)
        servers_container.pack_start(bottom, False, False, 5)

        connections_info = Gtk.VBox(spacing=0)
        connections_info.get_style_context().add_class('connection-info')
        bottom.pack_start(connections_info, True, True, 5)

        selected = Gtk.HBox(spacing=0)
        connections_info.pack_start(selected, False, False, 3)
        sel_rom_text = Gtk.Label("Selected server : ")
        selected.pack_start(sel_rom_text, False, False, 2)
        self.selected_label = Gtk.Label("Nothing")
        selected.pack_start(self.selected_label, False, False, 2)

        connected_to = Gtk.HBox(spacing=0)
        connections_info.pack_start(connected_to, False, False, 3)
        rom_text = Gtk.Label("Currently connected to : ")
        connected_to.pack_start(rom_text, False, False, 2)
        self.connected_to_label = Gtk.Label("Nothing")
        connected_to.pack_start(self.connected_to_label, False, False, 2)

        ip_container = Gtk.HBox()
        connections_info.pack_start(ip_container, False, False, 3)
        ip_rom_text = Gtk.Label("Ip: ")
        ip_container.pack_start(ip_rom_text, False, False, 2)
        self.ip_label = Gtk.Label()
        ip_container.pack_start(self.ip_label, False, False, 2)

        vpn_buttons = Gtk.VBox()
        bottom.pack_start(vpn_buttons, False, False, 5)

        self.switch_server_btn = Gtk.Button(label="Switch server")
        self.switch_server_btn.connect('clicked', self.main.switch_server)
        self.switch_server_btn.connect("enter-notify-event", self.hover)
        self.switch_server_btn.connect("leave-notify-event", self.not_hover)
        vpn_buttons.pack_start(self.switch_server_btn, False, False, 2)

        self.disconnect_btn = Gtk.Button(label="Disconnect")
        self.disconnect_btn.set_sensitive(False)
        self.disconnect_btn.connect('clicked', self.main.disconnect)
        self.disconnect_btn.connect("enter-notify-event", self.hover)
        self.disconnect_btn.connect("leave-notify-event", self.not_hover)
        vpn_buttons.pack_start(self.disconnect_btn, False, False, 2)

        # ================================
        # Settings
        # ================================
        settings_padding = Gtk.HBox()

        settings_scroll = Gtk.ScrolledWindow()
        settings_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        settings_scroll.add_with_viewport(settings_padding)

        self.tabs.append_page(settings_scroll)
        self.tabs.set_tab_label_text(settings_scroll, "Settings")
        self.tabs.child_set_property(settings_scroll, 'tab-expand', True)

        vpn_settings_container = Gtk.VBox()
        settings_padding.pack_start(vpn_settings_container, True, True, 15)

        credentials_v_container = Gtk.VBox()
        vpn_settings_container.pack_start(credentials_v_container, False, False, 15)

        self.username_label = Gtk.Label()
        self.username_label.set_markup("VPN Username")
        credentials_v_container.pack_start(self.username_label, False, False, 10)

        self.credentials_username = Gtk.Entry()
        self.credentials_username.set_placeholder_text("VPN Username")
        credentials_v_container.pack_start(self.credentials_username, False, False, 0)

        credentials_v_container.pack_start(Gtk.Label(), False, False, 0)

        self.password_label = Gtk.Label()
        self.password_label.set_markup("VPN Password")
        credentials_v_container.pack_start(self.password_label, False, False, 10)

        self.credentials_password = Gtk.Entry()
        self.credentials_password.set_placeholder_text("VPN Password")
        credentials_v_container.pack_start(self.credentials_password, False, False, 0)

        self.save_credentials_button = Gtk.Button(label="Save")
        self.save_credentials_button.connect("clicked", self.main.save_credentials)
        self.save_credentials_button.connect("enter-notify-event", self.hover)
        self.save_credentials_button.connect("leave-notify-event", self.not_hover)
        credentials_v_container.pack_start(self.save_credentials_button, False, False, 7)

        self.updated_vpn_credential_label = Gtk.Label()
        credentials_v_container.pack_start(self.updated_vpn_credential_label, False, False, 0)

        vpn_settings_container.pack_start(Gtk.Separator(), False, False, 10)

        protocol_container = Gtk.HBox()
        protocol_container.pack_start(Gtk.Label(), True, False, 0)

        is_tcp = True if main.config["connection_protocol"] == "tcp" else False
        self.udp_label = Gtk.Label()
        self.udp_label.set_markup("UDP" if is_tcp else "<b>UDP</b>")
        protocol_container.pack_start(self.udp_label, False, False, 0)

        self.protocol_switch = Gtk.Switch()
        self.protocol_switch.set_active(is_tcp)
        self.protocol_switch.connect("state-set", self.main.change_protocol)
        self.protocol_switch.connect("enter-notify-event", self.hover)
        self.protocol_switch.connect("leave-notify-event", self.not_hover)
        protocol_container.pack_start(self.protocol_switch, False, False, 20)

        self.tcp_label = Gtk.Label()
        self.tcp_label.set_markup("<b>TCP</b>" if is_tcp else "TCP")
        protocol_container.pack_start(self.tcp_label, False, False, 0)

        vpn_settings_container.pack_start(protocol_container, False, False, 15)
        protocol_container.pack_start(Gtk.Label(), True, False, 0)

        vpn_settings_container.pack_start(Gtk.Separator(), False, False, 10)

        self.enable_password_container = Gtk.VBox()
        if(not self.main.config['password_needed']):
            self.enable_password_container.set_sensitive(False)
        vpn_settings_container.pack_start(self.enable_password_container, False, False, 3)

        disable_pass_label = Gtk.Label("Disable/Enable the password")
        self.enable_password_container.pack_start(disable_pass_label, False, False, 3)

        self.disable_pass_button = Gtk.Button()
        self.disable_pass_button.set_label("Disable Pass" if self.main.config['password_needed'] else "Enable Pass")
        self.disable_pass_button.connect("clicked", self.main.change_password_need)
        self.disable_pass_button.connect("enter-notify-event", self.hover)
        self.disable_pass_button.connect("leave-notify-event", self.not_hover)
        self.enable_password_container.pack_start(self.disable_pass_button, False, False, 20)

        disable_pass_warn_label = Gtk.Label()
        disable_pass_warn_label.set_markup("<small>Disabling your password will display it uncrypted in the config.json!</small>")
        disable_pass_warn_label.get_style_context().add_class('warn')
        self.enable_password_container.pack_start(disable_pass_warn_label, False, False, 3)

        vpn_settings_container.pack_start(Gtk.Separator(), False, False, 10)

        self.updates_info = Gtk.Label()
        vpn_settings_container.pack_start(self.updates_info, False, False, 0)

        self.check_for_updates_btn = Gtk.Button("Check for VPN updates")
        self.check_for_updates_btn.connect("clicked", self.main.check_updates)
        self.check_for_updates_btn.connect("enter-notify-event", self.hover)
        self.check_for_updates_btn.connect("leave-notify-event", self.not_hover)
        vpn_settings_container.pack_start(self.check_for_updates_btn, False, False, 15)

        vpn_settings_container.pack_start(Gtk.Separator(), False, False, 10)

        update_pass_label = Gtk.Label('Change your password')
        update_pass_label.get_style_context().add_class('title')
        vpn_settings_container.pack_start(update_pass_label, False, False, 5)

        vpn_settings_container.pack_start(Gtk.Label(), False, False, 0)

        self.new_password_label = Gtk.Label()
        self.new_password_label.set_markup("New Password")
        self.new_password_label.get_style_context().add_class('label')
        vpn_settings_container.pack_start(self.new_password_label, False, False, 0)

        self.new_password = Gtk.Entry()
        self.new_password.set_placeholder_text("New Password")
        self.new_password.set_visibility(False)
        vpn_settings_container.pack_start(self.new_password, False, False, 0)

        vpn_settings_container.pack_start(Gtk.Label(), False, False, 0)

        self.confirm_new_password_label = Gtk.Label()
        self.confirm_new_password_label.set_markup("Confirm New Password")
        self.confirm_new_password_label.get_style_context().add_class('label')
        vpn_settings_container.pack_start(self.confirm_new_password_label, False, False, 0)

        self.confirm_new_password = Gtk.Entry()
        self.confirm_new_password.set_placeholder_text("Confirm New Password")
        self.confirm_new_password.set_visibility(False)
        vpn_settings_container.pack_start(self.confirm_new_password, False, False, 0)

        self.update_password = Gtk.Button("Update password")
        self.update_password.connect("clicked", self.main.update_password)
        self.update_password.connect("enter-notify-event", self.hover)
        self.update_password.connect("leave-notify-event", self.not_hover)
        vpn_settings_container.pack_start(self.update_password, False, False, 10)

        self.updated_password_label = Gtk.Label()
        vpn_settings_container.pack_start(self.updated_password_label, False, False, 5)

        vpn_settings_container.pack_start(Gtk.Label(), False, False, 13)

    def hover(self, listbox_widget, crossing):
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def not_hover(self, listbox_widget, crossing):
        self.get_window().set_cursor(None)

    def select_server(self, listbox):
        server_text = listbox.get_selected_row().get_children()[0].get_children()[1].get_text()
        self.selected_label.set_label(server_text)

    def confirm_connection(self):
        text = self.selected_label.get_text()
        self.switch_server_btn.set_sensitive(True)
        self.connected_to_label.set_label(text)
        self.ip_label.set_label(self.main.ip)
        self.disconnect_btn.set_sensitive(True)

    def vpn_connection_failed(self):
        self.switch_server_btn.set_sensitive(True)
        self.connected_to_label.set_label("ERROR")
        self.disconnect_btn.set_sensitive(False)

    def vpn_exited(self):
        self.connected_to_label.set_label("DISCONNECTED")
