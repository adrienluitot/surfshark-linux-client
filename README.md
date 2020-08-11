# Surfshark Linux Client

Surfshark Linux Client is simply a client for Linux for the VPN [SurfShark](https://surfshark.com). It’s made with python 3 and [PyGObject](https://pygobject.readthedocs.io/en/latest/index.html) (GTK).

## Installation / Usage

```bash
git clone https://github.com/adrienluitot/surfshark-linux-client.git
cd surfshark-linux-client
pip install -r requirements.txt

python surfshark_client.py
```

## Contribute

If you want to contribute it’s awesome ! Any help is appreciated even the littlest one !
You can open issues if you have any suggestion or bug, and if you want to improve the code of the application you can fork and make pull requests, I’ll do my best to treat them as quickly as possible.

If you never used PyGObject I suggest you these two docs : 

- [https://pygobject.readthedocs.io](https://pygobject.readthedocs.io/en/latest/index.html)
- [https://python-gtk-3-tutorial.readthedocs.io](https://python-gtk-3-tutorial.readthedocs.io/en/latest/)

## Problems with the Killswitch

If you get any problems with the killswitch and can't connect to the internet anymore you have three options

    1. You can use the restoreiptables.sh script which will try to restore a backup of your iptable rules 
    2. You can use the disableKillSwitch.sh which will reset ufw to its initial state(the best method when you haven't added custom firewall rules)
    3. You can try to fix it yourself
    
If you switch the server while the killswitch is turned on your real ip address might leak!
The Killswitch will stop working when you close the Window!

## Screenshots 
|                Main window                |                  Settings window                  |
| :---------------------------------------: | :-----------------------------------------------: |
| ![Main](https://i.luitot.fr/sslc_main.png)| ![Settings](https://i.luitot.fr/sslc_settings.jpg) |

|            Main window (Dark)             |               Settings window (Dark)               |
| :---------------------------------------: | :-----------------------------------------------:  |
| ![Main](https://jonahstrotmann.me/assets/img/resources/home_dark.png)| ![Settings](https://jonahstrotmann.me/assets/img/resources/settings_dark.png) |