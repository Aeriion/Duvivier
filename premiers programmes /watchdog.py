import subprocess
import time
import signal
import sys
import os

PYTHON_CMD = "python3"    # adapter si besoin
SERVER_SCRIPT = "flask_app.py"
CHECK_INTERVAL = 2.0      # intervalle de surveillance (secondes)
FREEZE_TIMEOUT = 5.0      # on considère que si BUG3 a été détecté, on attend 5s puis on tue

server_process = None
bug3_detected_time = None  # stocke l'heure où on a vu "[SIM-BUG] BUG3 DETECTED"

# --------------------------------------------------------------------
# Signaux
# --------------------------------------------------------------------
def handle_sigchld(signum, frame):
    """
    Signale qu'un enfant (server_process) est mort.
    On redémarre si c'est le cas.
    """
    global server_process
    if server_process and server_process.poll() is not None:
        print("[Watch-Dog] Le serveur est mort (SIGCHLD). On redémarre.")
        restart_server()

def handle_sigint(signum, frame):
    """
    Ctrl+C dans la console du watch-dog.
    """
    print("\n[Watch-Dog] Interruption (Ctrl+C). On arrête le serveur et on quitte.")
    stop_server()
    sys.exit(0)

# --------------------------------------------------------------------
# Gestion du serveur
# --------------------------------------------------------------------
def start_server():
    global server_process
    if server_process and server_process.poll() is None:
        print("[Watch-Dog] Le serveur tourne déjà.")
        return

    print("[Watch-Dog] Lancement du serveur Flask...")
    try:
        server_process = subprocess.Popen(
            [PYTHON_CMD, SERVER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"[Watch-Dog] Serveur lancé. PID={server_process.pid}")
    except Exception as e:
        print(f"[ERREUR] Impossible de lancer le serveur : {e}")
        server_process = None

def stop_server():
    global server_process
    if server_process and server_process.poll() is None:
        print(f"[Watch-Dog] Arrêt du serveur (PID={server_process.pid})...")
        try:
            server_process.terminate()
            server_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            print("[Watch-Dog] Le serveur ne s'arrête pas, on kill !")
            server_process.kill()
            server_process.wait()
        except Exception as e:
            print(f"[ERREUR] en arrêtant le serveur : {e}")

    server_process = None

def restart_server():
    stop_server()
    time.sleep(1)
    start_server()

# --------------------------------------------------------------------
# Lecture et analyse des logs serveur (stdout)
# --------------------------------------------------------------------
def flush_server_output():
    """
    Lit les lignes disponibles sur stdout du serveur et agit selon
    les bugs détectés. (Non-bloquant)
    """
    global bug3_detected_time

    if not server_process:
        return

    try:
        while True:
            line = server_process.stdout.readline()
            if not line:
                break
            line = line.rstrip("\n")
            print(f"[SERVEUR-OUT] {line}")

            # Analyser la ligne pour voir s'il y a un bug simulé
            if "[SIM-BUG] BUG3 DETECTED" in line:
                # On note l'heure pour gérer un timeout
                bug3_detected_time = time.time()
                print("[Watch-Dog] BUG3 détecté => boucle infinie probable.")
            if "[SIM-BUG]" in line and "DETECTED" in line:
                # Pour tout bug simulé, on log
                print(f"[Watch-Dog] On a détecté un bug simulé dans les logs: {line}")

    except Exception as e:
        print(f"[ERREUR] flush_server_output() : {e}")

# --------------------------------------------------------------------
# Boucle principale du Watch-Dog
# --------------------------------------------------------------------
def main():
    print("=== Watch-Dog démarré ===")
    signal.signal(signal.SIGCHLD, handle_sigchld)
    signal.signal(signal.SIGINT, handle_sigint)

    # Démarrage initial
    start_server()

    try:
        while True:
            # Si le serveur a fini (poll != None), on relance
            if server_process and server_process.poll() is not None:
                print("[Watch-Dog] Le serveur est terminé. Redémarrage...")
                restart_server()

            # On lit la sortie du serveur
            flush_server_output()

            # Gérer le cas BUG3 => on tue le serveur après FREEZE_TIMEOUT
            if bug3_detected_time is not None:
                # si ça fait plus de 5s, on considère qu'il est figé
                if time.time() - bug3_detected_time > FREEZE_TIMEOUT:
                    print("[Watch-Dog] BUG3 - Le serveur est figé depuis trop longtemps, on le tue.")
                    stop_server()
                    start_server()
                    bug3_detected_time = None

            time.sleep(CHECK_INTERVAL)
    except SystemExit:
        pass
    except Exception as e:
        print(f"[ERREUR] Exception dans la boucle watch-dog : {e}")
    finally:
        print("[Watch-Dog] Arrêt final, on stoppe le serveur.")
        stop_server()
        print("[Watch-Dog] Fin.")

if __name__ == "__main__":
    main()