from flask import Flask,render_template
import os,sys
import time
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return "Alive"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()

def restart():
    os.execl(sys.executable, sys.executable, *sys.argv)

def keep_restart():
   #restart thread
    t = Thread(target=restart)
    t.start()
