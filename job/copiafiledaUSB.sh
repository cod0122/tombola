#!/bin/bash
#
# This script is called by a udev rule whenever a usb drive is
# plugged into the system or removed from the system.
# Usage:
# auto-usb.sh MODE DEVICE
# where MODE is either mount or cleanup
# and DEVICE is the device basename, i.e. /dev/DEVICE

cd $HOME/tombola/job

if [ "$1" = "mount" ]; then
    # The ID_FS_LABEL enviroment variable is only available
    # When this script is caleld by udev
    mkdir -p "./usb/$ID_FS_LABEL"
    $(mount | grep -q "./usb/$ID_FS_LABEL") || mount /dev/$2 "./usb/$ID_FS_LABEL"
    if [ $? -eq 0 ]; then
       echo "Mount successo!"
       cp ./usb/$ID_FS_LABEL/xtombola/* ./appoggio
       if [ $? -eq 0 ]; then
          cd appoggio
          chmod ugo+rw *
          cd ..
       else
          echo 'manca la cartella xtombola'
          cd /home/pi/tombola
          exit 2
       fi
       umount  "./usb/$ID_FS_LABEL"
    else
       echo "mount fallito!"
       cd $HOME/tombola
       exit 1
    fi
    #ls -l ./usb/$ID_FS_LABEL/tombola/* 
elif [ "$1" = "remove" ]; then
    rm ./appoggio/*
else
    echo "ERROR: Mode $1 should be 'mount' or 'cleanup'."
fi

cd $HOME/tombola
