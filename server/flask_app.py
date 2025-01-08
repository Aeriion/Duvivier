import os
from flask import Flask, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ma_clé_ultra_secrète'

# Autorise les connexions cross-origin (depuis n'importe quel domaine).
# En production, on peut restreindre 'cors_allowed_origins' à votre domaine.
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return "Serveur Flask-SocketIO en ligne !"

@socketio.on('connect')
def handle_connect():
    print(f"[INFO] Client connecté : {request.sid}")

@socketio.on('chatMessage')
def handle_chat_message(msg):
    """
    Reçoit un événement 'chatMessage' depuis un client
    et le rediffuse à tous les autres clients connectés via 'chatMessage'.
    """
    print(f"[CHAT] Message reçu : {msg}")
    socketio.emit('chatMessage', msg, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[INFO] Client déconnecté : {request.sid}")

if __name__ == '__main__':
    # On peut lire le port à partir d'une variable d'environnement,
    # sinon on utilise 5000 par défaut
    port = int(os.environ.get('PORT', 5001))
    print(f"[INFO] Lancement du serveur Flask-SocketIO sur le port {port} ...")

    # Si vous avez installé eventlet ou gevent, ça fonctionne également :
    # socketio.run(app, host='0.0.0.0', port=port, debug=True)
    socketio.run(app, host='0.0.0.0', port=port)