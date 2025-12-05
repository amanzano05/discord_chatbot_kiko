from flask import Flask
from threading import Thread
from waitress import serve

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
  # Use waitress for production-ready server
  serve(app, host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
