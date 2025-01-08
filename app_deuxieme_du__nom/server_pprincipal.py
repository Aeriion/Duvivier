import os
import sys
import time
import mmap
import posix_ipc
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

TUBE_REQUEST = "/tmp/sp_request"
TUBE_RESPONSE = "/tmp/sp_response"
SHM_NAME = "/sp_shm"
SHM_SIZE = 1024

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ma_cle_secrete'
socketio = SocketIO(app, cors_allowed_origins='*')

connected_users = {}  # sid -> pseudo

def setup_ipc():
    for tube in [TUBE_REQUEST, TUBE_RESPONSE]:
        if not os.path.exists(tube):
            os.mkfifo(tube, 0o600)
    try:
        shm = posix_ipc.SharedMemory(SHM_NAME, posix_ipc.O_CREX, size=SHM_SIZE)
    except posix_ipc.ExistentialError:
        posix_ipc.unlink_shared_memory(SHM_NAME)
        shm = posix_ipc.SharedMemory(SHM_NAME, posix_ipc.O_CREX, size=SHM_SIZE)
    mapfile = mmap.mmap(shm.fd, shm.size)
    shm.close_fd()
    mapfile.seek(0)
    mapfile.write(b"READY")
    mapfile.flush()
    return mapfile

shm_map = None

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print("[Principal] Un client SocketIO s'est connecté (sid=",  request.sid, ")")

@socketio.on('join')
def on_join(data):
    """
    Reçoit l'événement 'join' émis par le client juste après connexion,
    contenant le pseudo de l'utilisateur.
    """
    pseudo = data.get('pseudo', '')[:20].strip()  # limite 20 caractères
    sid = request.sid
    connected_users[sid] = pseudo if pseudo else f"User{sid[-3:]}"
    print(f"[Principal] {pseudo} vient de rejoindre (sid={sid})")

    # Notifier tout le monde de la liste à jour
    broadcast_user_list()

@socketio.on('message')
def handle_message(msg):
    """
    Reçoit un message normal de la part du client.
    """
    sid = request.sid
    pseudo = connected_users.get(sid, "Inconnu")
    print(f"[Principal] Message de {pseudo}: {msg}")

    # Diffuser à tous, en préfixant le pseudo
    emit('message', f"{pseudo}: {msg}", broadcast=True)

    # Exemple: si le message commence par "!traiter"
    if msg.startswith("!traiter"):
        with open(TUBE_REQUEST, "w") as req_tube:
            req_tube.write("TRAITER|foo\n")
            req_tube.flush()
        shm_map.seek(0)
        shm_map.write(b"REQUESTED")
        shm_map.flush()
        print("[Principal] Requête envoyée au secondaire (via tube + shm)")

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    pseudo = connected_users.pop(sid, None)
    print(f"[Principal] {pseudo} s'est déconnecté (sid={sid})")
    broadcast_user_list()

def broadcast_user_list():
    """
    Envoie à tous la liste des pseudos connectés
    """
    user_list = list(connected_users.values())
    emit('user_list', user_list, broadcast=True)

def check_response_tube():
    print("[Principal] Thread de lecture du tube RESPONSE démarré.")
    while True:
        with open(TUBE_RESPONSE, "r") as resp_tube:
            for line in resp_tube:
                line = line.strip()
                if line:
                    print(f"[Principal] Reçu depuis le secondaire : {line}")
                    socketio.emit('message', f"[Secondaire] {line}")

def main():
    global shm_map
    shm_map = setup_ipc()
    t = threading.Thread(target=check_response_tube, daemon=True)
    t.start()
    try:
        socketio.run(app, host='0.0.0.0', port=3001)
    except KeyboardInterrupt:
        print("[Principal] Interrompu par Ctrl+C.")
    finally:
        shm_map.close()
        posix_ipc.unlink_shared_memory(SHM_NAME)
        for tube in [TUBE_REQUEST, TUBE_RESPONSE]:
            if os.path.exists(tube):
                try:
                    os.unlink(tube)
                except:
                    pass

if __name__ == '__main__':
    from flask import request
    main()