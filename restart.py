from subprocess import Popen
from keep_alive import keep_alive
import sys
import os

keep_alive()

filename = sys.argv[1]
while True:
    print("\nStarting " + filename)
    p = Popen("python " + filename, shell=True)
    p.wait()
    if p.returncode == 3:
        os._exit(0)
