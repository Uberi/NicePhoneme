#!/bin/bash

# install dependencies
sudo pip3 install pillow
sudo pip3 install scipy
sudo pip3 install numpy
sudo pip3 install cython
sudo pip3 install matplotlib

# install library
sudo apt-get install unzip
unzip word_cloud-master.zip
sudo python3 word_cloud-master/setup.py install
