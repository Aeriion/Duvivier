import os
import sys
import logging
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ma_clé_ultra_secrète'
# On réduit le verbosité du logger Werkzeug (serveur web Flask)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    client_ip = request.remote_addr
    print(f"[INFO] Connexion d'un nouveau client (IP={client_ip}).")
    emit('server_message', f"Bienvenue sur le chat ! (IP={client_ip})")

@socketio.on('message')
def handle_message(msg):
    """
    Quand un message est reçu, on vérifie s'il s'agit d'un mot clé
    pour simuler des bugs (bug1, bug2, bug3...).
    Sinon, on le rediffuse.
    """
    print(f"[CHAT] Message reçu : {msg}")

    # -- Simulation de bugs en fonction du message --
    if msg.lower() == "bug1":
        # Simuler un plantage volontaire
        print("[SIM-BUG] BUG1 DETECTED. On se termine brutalement (sys.exit).")
        sys.exit(1)

    elif msg.lower() == "bug2":
        # Simuler une exception non gérée
        print("[SIM-BUG] BUG2 DETECTED. On lève une exception pour voir le crash.")
        raise RuntimeError("BUG2 - Exception simulée")

    elif msg.lower() == "bug3":
        # Simuler une boucle infinie => le serveur se fige
        print("[SIM-BUG] BUG3 DETECTED. Boucle infinie simulée, le serveur va geler.")
        while True:
            time.sleep(1)

    else:
        # Comportement normal : broadcast
        send(msg, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    print("[INFO] Un client s'est déconnecté.")

# Gérer les erreurs HTTP basiques
@app.errorhandler(404)
def not_found_error(error):
    return "Page non trouvée", 404

@app.errorhandler(500)
def internal_error(error):
    return "Erreur interne du serveur (500)", 500

if __name__ == '__main__':
    try:
        print("[INFO] Démarrage du serveur Flask/SocketIO sur le port 5000...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"[ERREUR] Le serveur Flask a rencontré une exception : {e}", file=sys.stderr)
        sys.exit(1)