from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Content Creator AI Server'

@app.route('/legal/<path:filename>')
def legal(filename):
    return send_from_directory('legal', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
