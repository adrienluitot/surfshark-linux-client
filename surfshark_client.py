import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import urllib.request
import json
import hashlib
import base64
import subprocess
import threading
import time
import os
from datetime import date

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad, unpad

from log_window import LogWindow
from main_window import MainWindow
from popup import Popup

class Main():
    def __init__(self):
        if os.geteuid() != 0:
            root_popup = Popup('Error', 'You need to be root to run the VPN.')
            root_popup.set_icon_from_file("surfshark_linux_client.png")
            root_popup.connect('destroy', Gtk.main_quit)
            Gtk.main()
            return None

        self.debug_on = True  # set to False to disable debug infos

        # TODO : Make a loader
        # TODO : Find a way to have a popup to run the app as root

        self.folder_path = os.path.abspath(os.path.dirname(__file__)) + "/"


        self.servers = self.get_servers()
        self.unhash_pass = ""
        self.config_files = {}
        self.vpn_command = False
        self.thread = False
        self.ip = ""

        with open(self.folder_path + "config.json", "r") as file:
            self.config = json.load(file)

        style = Gtk.CssProvider()
        #Theme
        if(self.config['theme'] == 'light'):
            style.load_from_path(self.folder_path + "style/style_lightmode.css")
        else:
            style.load_from_path(self.folder_path + "style/style_darkmode.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        if (self.config['password_needed'] or not self.config['registered']):
            self.log_window = LogWindow(self)
            self.log_window.connect("destroy", Gtk.main_quit)
            self.log_window.show_all()

        self.main_window = MainWindow(self)
        self.main_window.connect("destroy", self.soft_quit_g)

        if (not self.config['password_needed'] and self.config['registered']):
            screen = self.main_window.get_display()
            monitor_size = screen.get_monitor_at_window(Gdk.get_default_root_window()).get_geometry()
            self.main_window.move(monitor_size.width / 2 - self.main_window.get_size().width / 2,
                                  monitor_size.height / 2 - self.main_window.get_size().height / 2)
            self.main_window.credentials_username.set_text(self.config['vpn_username'])
            self.main_window.credentials_password.set_text(self.config['vpn_password'])
            self.main_window.show_all()

        try:
            Gtk.main()
        except (KeyboardInterrupt, SystemExit):
            self.soft_quit()

    def log_action(self, widget):
        hashed_password = self.hash_pass(self.log_window.password.get_text())
        if self.config['registered']:
            if (hashed_password == self.config['password']):
                self.log_in()
            else:
                self.log_window.password.get_style_context().add_class('error')
                self.debug("Wrong password")
        else:
            if (widget == self.log_window.log_without_pass_button):
                self.config['registered'] = True
                self.config['password_needed'] = False

                self.save_config()
                self.log_in()
            else:
                if (self.log_window.password.get_text() == self.log_window.confirm_password.get_text()):
                    self.config['registered'] = True
                    self.config['password_needed'] = True
                    self.config['password'] = hashed_password

                    self.save_config()
                    self.debug("Account created")

                    self.log_in()
                else:
                    self.log_window.password.get_style_context().add_class('error')
                    self.log_window.confirm_password.get_style_context().add_class('error')

    def get_servers(self):
        with urllib.request.urlopen("https://api.surfshark.com/v3/server/clusters/all") as url:
            return json.loads(url.read().decode())

    def log_in(self):
        if(self.config['password_needed']):
            self.unhash_pass = self.log_window.password.get_text()

        old_pos = self.log_window.get_position()
        self.log_window.hide()
        self.main_window.move(old_pos.root_x, old_pos.root_y)
        self.main_window.show_all()

        if ('vpn_password' in self.config and 'vpn_username' in self.config and self.config['vpn_username'] != "" and
                self.config['vpn_password'] != ""):
            if (self.config['password_needed']):
                try:
                    vpn_username = self.sym_decrypt(self.config['vpn_username'])
                    vpn_password = self.sym_decrypt(self.config['vpn_password'])
                except:
                    vpn_username = ""
                    vpn_password = ""
            else:
                vpn_username = self.config['vpn_username']
                vpn_password = self.config['vpn_password']
            self.main_window.credentials_username.set_text(vpn_username)
            self.main_window.credentials_password.set_text(vpn_password)


        self.debug("Logged In")

    def save_config(self):
        with open(self.folder_path + "config.json", "w") as file:
            file.write(json.dumps(self.config))
            self.debug("Config saved")

    def debug(self, message, type=None):
        if (self.debug_on):
            type = "INFO" if not type else type
            print(type + ": " + message)

    def save_credentials(self, widget):
        vpn_username = self.main_window.credentials_username.get_text()
        vpn_password = self.main_window.credentials_password.get_text()
        error_count = 0
        if (vpn_username == ""):
            self.main_window.credentials_username.get_style_context().add_class('error')
            error_count += 1
        if (vpn_password == ""):
            self.main_window.credentials_password.get_style_context().add_class('error')
            error_count += 1
        if (error_count > 0): return


        if (self.config['password_needed']):
            vpn_username = self.sym_encrypt(vpn_username)
            vpn_password = self.sym_encrypt(vpn_password)

        self.config['vpn_username'] = vpn_username
        self.config['vpn_password'] = vpn_password
        self.save_config()
        
        creds_updated = threading.Thread(target=self.credential_updated)
        creds_updated.start()


    def sym_encrypt(self, raw):
        private_key = hashlib.sha256(self.unhash_pass.encode("utf-8")).digest()
        raw = pad(raw.encode('utf-8'), AES.block_size)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf8')

    def sym_decrypt(self, encrypted_text):
        private_key = hashlib.sha256(self.unhash_pass.encode("utf-8")).digest()
        encrypted_text = base64.b64decode(encrypted_text)
        iv = encrypted_text[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_text[16:]), AES.block_size).decode('utf8')

    def hash_pass(self, password):
        return base64.b64encode(hashlib.sha3_512(password.encode("utf-8")).hexdigest().encode()).decode()

    def change_protocol(self, switch, is_tcp):
        if (is_tcp):
            self.config["connection_protocol"] = "tcp"
            self.main_window.udp_label.set_markup("UDP")
            self.main_window.tcp_label.set_markup("<b>TCP</b>")
        else:
            self.config["connection_protocol"] = "udp"
            self.main_window.udp_label.set_markup("<b>UDP</b>")
            self.main_window.tcp_label.set_markup("TCP")
        self.save_config()


    def change_password_need(self, button):
        button.set_sensitive(False)
        if(self.config['password_needed']):
            self.config['password_needed'] = False
            self.config['vpn_username'] = self.sym_decrypt(self.config['vpn_username'])
            self.config['vpn_password'] = self.sym_decrypt(self.config['vpn_password'])
            button.set_label("Enable Pass")
        else:
            self.config['password_needed'] = True
            self.config['vpn_username'] = self.sym_encrypt(self.config['vpn_username'])
            self.config['vpn_password'] = self.sym_encrypt(self.config['vpn_password'])
            button.set_label("Disable Pass")

        self.save_config()
        button.set_sensitive(True)

    def update_password(self, button):
        self.main_window.new_password.get_style_context().remove_class("error")
        self.main_window.confirm_new_password.get_style_context().remove_class("error")

        if(self.main_window.new_password.get_text() == self.main_window.confirm_new_password.get_text()):
            self.config['password'] = self.hash_pass(self.main_window.new_password.get_text())
            if(self.config['password_needed']):
                vpn_user = self.sym_decrypt(self.config['vpn_username'])
                vpn_pass = self.sym_decrypt(self.config['vpn_password'])
            else:
                vpn_user = self.config['vpn_username']
                vpn_pass = self.config['vpn_password']
                self.config['password_needed'] = True
                self.main_window.disable_pass_button.set_label("Disable Pass")
                self.main_window.enable_password_container.set_sensitive(True)

            self.unhash_pass = self.main_window.new_password.get_text()
            self.config['vpn_username'] = self.sym_encrypt(vpn_user)
            self.config['vpn_password'] = self.sym_encrypt(vpn_pass)
            self.main_window.new_password.set_text("")
            self.main_window.confirm_new_password.set_text("")

            self.save_config()

            password_updated_t = threading.Thread(target=self.password_updated)
            password_updated_t.start()
        else:
            self.main_window.new_password.get_style_context().add_class("error")
            self.main_window.confirm_new_password.get_style_context().add_class("error")

    def password_updated(self):
        self.main_window.updated_password_label.set_label("Password updated")
        time.sleep(2)
        self.main_window.updated_password_label.set_label("")

    def credential_updated(self):
        self.main_window.updated_vpn_credential_label.set_label("Credentials updated")
        time.sleep(2)
        self.main_window.updated_vpn_credential_label.set_label("")

    def change_theme(self, switch, current_theme):
        style = Gtk.CssProvider()

        if(current_theme):
            style.load_from_path(self.folder_path + "style/style_darkmode.css")
            self.config['theme'] = "dark"
            self.main_window.light_label.set_markup("Light")
            self.main_window.dark_label.set_markup("<b>Dark</b>")
        else:
            style.load_from_path(self.folder_path + "style/style_lightmode.css")
            self.config['theme'] = "light"

            self.main_window.light_label.set_markup("<b>Light</b>")
            self.main_window.dark_label.set_markup("Dark")
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.save_config()


    def change_killswitch(self, switch, killswitch_status):
        if (killswitch_status):
            self.config["killswitch"] = "on"
            self.main_window.killswitch_off_label.set_markup("OFF")
            self.main_window.killswitch_on_label.set_markup("<b>ON</b>")
            if(self.vpn_command):
                self.enable_killswitch()
            success_popup = Popup("Killswitch activated", "The killswitch is now activated!\nThe current version of the killswitch can leak on port 1194")
        else:
            self.config["killswitch"] = "off"
            self.main_window.killswitch_off_label.set_markup("<b>OFF</b>")
            self.main_window.killswitch_on_label.set_markup("ON")       
            self.disable_killswitch()         
            success_popup = Popup("Killswitch deactivated", "The killswitch is now inactive!\nYour network traffic is now possible to leak")
        self.save_config()

    def credential_updated(self):
        self.main_window.updated_vpn_credential_label.set_label("Credentials updated")
        time.sleep(2)
        self.main_window.updated_vpn_credential_label.set_label("")

    def switch_server(self, button):
        text = self.main_window.selected_label.get_text()
        if (text == "Nothing"): return False

        self.main_window.connected_to_label.set_label("Connecting...")
        self.main_window.switch_server_btn.set_sensitive(False)
        openvpn_config_file = self.config_files[text] + "_" + self.config['connection_protocol'] + ".ovpn"

        if (self.vpn_command):
            self.vpn_command.terminate()
            self.thread.join()
            self.main_window.ip_label.set_label("")

        with open(self.folder_path + '.tmp_creds_file', 'a+') as cred_file:
            cred_file.write(str(keyring.get_password("SurfShark", "openvpn_username")) + "\n" + str(keyring.get_password("SurfShark", "openvpn_password")))

        subprocess.call(["cp", self.folder_path + "vpn_config_files/" + openvpn_config_file, self.folder_path + ".tmp_cfg_file"])

        try:
            i = 0
            with open(self.folder_path + '.tmp_cfg_file', 'r+') as cfg_file:
                file = cfg_file.readlines()
                for line in file:
                    if ("auth-user-pass" in line): break
                    i += 1
        except:
            self.debug("VPN config file is missing", "ERROR")
            self.main_window.connected_to_label.set_label("ERROR")
            self.main_window.switch_server_btn.set_sensitive(True)

            Popup('Error', "Couldn't find config file for this server, try to update the config files.", self.main_window)

            return False

        with open(self.folder_path + '.tmp_cfg_file', 'w') as cfg_file:
            file[i] = "auth-user-pass "+ self.folder_path +".tmp_creds_file"
            cfg_file.writelines(file)

        #disable the killswitch to connect to a new server
        if(self.config["killswitch"] == "on"):
            self.disable_killswitch()
        
        self.vpn_command = subprocess.Popen(["openvpn", self.folder_path + ".tmp_cfg_file"], stdout=subprocess.PIPE)

        self.thread = threading.Thread(target=self.command_log)
        self.thread.start()

    def command_log(self):
        time.sleep(.1)
        subprocess.call(["rm", self.folder_path + ".tmp_cfg_file"])
        subprocess.call(["rm", self.folder_path + ".tmp_creds_file"])

        for line in iter(self.vpn_command.stdout.readline, b''):
            line = line.decode()[:-1]
            if ("Exiting due to fatal error" in line):
                self.debug('Fatal error, VPN disconnected', type="ERROR")
                self.ip = ""
                self.main_window.vpn_exited()
            elif ("AUTH_FAILED" in line):
                self.debug('Wrong credentials', type="ERROR")
                self.ip = ""
                self.main_window.vpn_connection_failed()
            elif ("Initialization Sequence Completed" in line):
                self.debug('Connected to VPN')
                p = subprocess.Popen(["curl", "ipecho.net/plain"], stdout=subprocess.PIPE)
                ip, err = p.communicate()
                self.ip = ip.decode()
                self.main_window.confirm_connection()
                if(self.config["killswitch"] == "on"):
                    self.enable_killswitch()

            with open(self.folder_path + "logs/openvpn-logs-" + str(date.today()) + ".txt", 'a') as logfile:
                logfile.write(line + "\n")

    def disconnect(self, button):
        self.debug('DISCONNECTED')
        self.vpn_command.terminate()
        self.thread.join()
        self.disable_killswitch()

        self.ip = ""
        self.main_window.connected_to_label.set_label("Disconnected")
        self.main_window.ip_label.set_label("")
        self.main_window.disconnect_btn.set_sensitive(False)
        self.main_window.switch_server_btn.set_sensitive(True)


    def check_updates(self, button):
        subprocess.call(["wget", "https://account.surfshark.com/api/v1/server/configurations", "-O", self.folder_path + "vpn_config_files/conf.zip"])
        p = subprocess.Popen(["md5sum", self.folder_path + "vpn_config_files/conf.zip"], stdout=subprocess.PIPE)
        checksum, err = p.communicate()
        checksum = checksum.decode().split("  ")[0]

        if(checksum != self.config['config_md5']):
            subprocess.call("rm " + self.folder_path + "vpn_config_files/*.ovpn", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.call(["unzip", self.folder_path + "vpn_config_files/conf.zip", "-d", self.folder_path + "vpn_config_files"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.config['config_md5'] = checksum
            self.save_config()
            self.main_window.updates_info.set_label("The config files were updated !")
        else:
            self.main_window.updates_info.set_label("Everything is okay !")

        subprocess.call(["rm", self.folder_path + "vpn_config_files/conf.zip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    def soft_quit(self):
        if self.vpn_command and self.thread:
            self.vpn_command.terminate()
            self.thread.join()
        self.disable_killswitch()
        self.create_tray()
        Gtk.main_quit()

    def soft_quit_g(self, window):
        self.soft_quit()

    def enable_killswitch(self):
        #enable killswitch
        enable_killswitch_command = "sudo ./enablekillswitch.sh"

        command = enable_killswitch_command.split()
        subprocess.run(command)

    def disable_killswitch(self):
        #restore old iptable rules
        restore_iptables_command= "sudo ./restoreiptables.sh"
        command = restore_iptables_command.split()
        subprocess.run(command)

    def create_tray(self):
        #TODO
        pass

Main()
