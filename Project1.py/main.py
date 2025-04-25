import json
import socket
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')
DATA_FILE = Path("storage/data.json")
UDP_IP = "127.0.0.1"
UDP_PORT = 5000

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        data = {
            'username': request.form.get('username', ''),
            'message': request.form.get('message', '')
        }
        send_udp_data(data)
        return redirect(url_for('index'))
    return render_template('message.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html'), 404

# --- UDP CLIENT ---

def send_udp_data(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(data).encode('utf-8'), (UDP_IP, UDP_PORT))
    sock.close()

# --- UDP SERVER ---

def run_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, _ = sock.recvfrom(1024)
        message_data = json.loads(data.decode('utf-8'))
        timestamp = str(datetime.now())

        if not DATA_FILE.parent.exists():
            DATA_FILE.parent.mkdir(parents=True)

        if DATA_FILE.exists():
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        existing_data[timestamp] = message_data

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2)

# --- MAIN THREAD ---

def run_flask():
    app.run(port=3000)

if __name__ == '__main__':
    udp_thread = threading.Thread(target=run_udp_server, daemon=True)
    udp_thread.start()
    run_flask()
