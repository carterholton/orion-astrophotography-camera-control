import time
import os, signal, subprocess
import readchar
import init
#import focuser
from rpi_lcd import LCD
lcd = LCD()

iso_index = {
0:'AUTO',
1:100,
2:200,
3:400,
4:800,
5:1600,
6:3200,
7:6400,
8:12800}

def main():
    dbase = init.run()
    focuser.run()
    print(dbase)

main()
