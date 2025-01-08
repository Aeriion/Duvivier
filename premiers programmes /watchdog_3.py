import subprocess
import time
import signal
import sys
import os

def main():
    print("=== Watch-Dog démarré ===")

    # 1) Lancer le serveur principal
    print("[Watch-Dog] Lancement du serveur principal...")
    principal_proc = start_principal()

    # 2) Attendre un peu que le principal crée ses tubes /tmp/dwtube1 et /tmp/wdtube1
    time.sleep(1)

    # 3) Lancer le serveur secondaire
    print("[Watch-Dog] Lancement du serveur secondaire...")
    secondary_proc = start_secondary()

    try:
        # Boucle de surveillance
        while True:
            # Vérifier si le principal est encore vivant
            if principal_proc.poll() is not None:
                print("[Watch-Dog] Principal s'est arrêté. Redémarrage...")
                # Tuer le serveur secondaire (qui dépend du principal) s'il tourne encore
                if secondary_proc.poll() is None:
                    secondary_proc.kill()
                    secondary_proc.wait()
                # Relancer le principal
                principal_proc = start_principal()
                time.sleep(1)
                # Relancer le secondaire
                secondary_proc = start_secondary()

            # Vérifier si le secondaire est encore vivant
            if secondary_proc.poll() is not None:
                print("[Watch-Dog] Secondaire s'est arrêté. Redémarrage...")
                # Simplement relancer le secondaire
                secondary_proc = start_secondary()

            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[Watch-Dog] Interruption clavier (Ctrl+C). On arrête tout.")
    finally:
        # Tuer proprement tout le monde avant de quitter
        stop_process(principal_proc)
        stop_process(secondary_proc)
        print("[Watch-Dog] Fin.")

def start_principal():
    """
    Lance le script server_principal.py dans un sous-processus et retourne le Popen.
    """
    # stdout/stderr redirigés vers la console du watch-dog
    # si vous voulez séparer, voir plus bas
    return subprocess.Popen(["python3", "server_principal.py"])

def start_secondary():
    """
    Lance le script server_secondaire.py dans un sous-processus et retourne le Popen.
    """
    return subprocess.Popen(["python3", "server_secondaire.py"])

def stop_process(proc):
    """
    Tente de stopper un sous-processus (Popen) s'il est encore vivant.
    """
    if proc.poll() is None:  # None => toujours actif
        try:
            proc.kill()
            proc.wait()
        except Exception as e:
            print(f"[Watch-Dog] Erreur en tuant le processus {proc.pid}: {e}")

if __name__ == "__main__":
    main()