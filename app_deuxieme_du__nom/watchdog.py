import subprocess
import time
import signal
import sys

principal_proc = None
secondaire_proc = None

def start_principal():
    global principal_proc
    if principal_proc and principal_proc.poll() is None:
        print("[WatchDog] Principal tourne déjà.")
        return
    print("[WatchDog] Lancement du serveur principal.")
    principal_proc = subprocess.Popen(["python3", "server_pprincipal.py"])

def start_secondaire():
    global secondaire_proc
    if secondaire_proc and secondaire_proc.poll() is None:
        print("[WatchDog] Secondaire tourne déjà.")
        return
    print("[WatchDog] Lancement du serveur secondaire.")
    secondaire_proc = subprocess.Popen(["python3", "server_secondaire.py"])

def stop_process(proc):
    if proc and proc.poll() is None:
        print(f"[WatchDog] Arrêt du process PID={proc.pid}.")
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            print("[WatchDog] Kill forcé.")
            proc.kill()
            proc.wait()

def sigint_handler(signum, frame):
    print("\n[WatchDog] Interruption clavier. Arrêt de tout.")
    stop_process(principal_proc)
    stop_process(secondaire_proc)
    sys.exit(0)

def main():
    print("[WatchDog] Démarré.")
    signal.signal(signal.SIGINT, sigint_handler)

    # Lancement initial
    start_principal()
    start_secondaire()

    try:
        while True:
            # Surveillance du principal
            if principal_proc and principal_proc.poll() is not None:
                print("[WatchDog] Principal est mort. Relance.")
                start_principal()
            # Surveillance du secondaire
            if secondaire_proc and secondaire_proc.poll() is not None:
                print("[WatchDog] Secondaire est mort. Relance.")
                start_secondaire()
            time.sleep(3)
    except SystemExit:
        pass
    finally:
        print("[WatchDog] Fin, arrêt des process.")
        stop_process(principal_proc)
        stop_process(secondaire_proc)

if __name__ == '__main__':
    main()