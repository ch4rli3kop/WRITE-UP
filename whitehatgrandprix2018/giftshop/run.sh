#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
cd /home/gift
./ptrace_64 ./giftshop m444ndu 1 60 50 blacklist.conf