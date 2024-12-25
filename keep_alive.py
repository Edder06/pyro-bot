from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def index():
  return "Alive"

def run():
  app.run(host=os.getenv("PORT"),port=5000)

def keep_alive():  
  t1 = Thread(target=run)
  t1.start()
