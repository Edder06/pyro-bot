from flask import Flask,render_template
import os,sys
import time
from threading import Thread

app = Flask(__name__)
t1 = None
restart = False

@app.route('/')
def index():
  return "Alive"

def run():
  global restart
  while True:
    app.run(host='0.0.0.0', port=8080)

    if restart:
      print("reiniciando", flush= True)
      break

def keep_alive():  
  global t1
  global restart
  t1 = Thread(target=run)
  t1.start()

# def restart():
#   os.execl(sys.executable, sys.executable, *sys.argv)

def keep_restart():
  #restart thread
  global t1
  global restart
  time.sleep(1)
  print("volvi", flush=True)
  restart = True
  t1.join(2)
  # t1.isAlive()
  print(t1.is_alive(), flush=True)
  print("termine", flush=True)
