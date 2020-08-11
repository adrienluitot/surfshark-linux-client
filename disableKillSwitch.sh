#!/bin/bash
echo 'This will reset all previous rules are you sure that you want to proceed?'
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable