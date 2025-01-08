import os
import sys

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
tube1_path = "/tmp/dwtube1"  # Tube principal -> secondaire
tube2_path = "/tmp/wdtube1"  # Tube secondaire -> principal
MAX_MESSAGE_LENGTH = 200     # Limitation de la taille des messages

def main():
    """
    Programme : serveur principal
    - Crée les deux tubes nommés s'ils n'existent pas déjà
    - Envoie les messages saisis dans la console au serveur secondaire
    - Reçoit et affiche les réponses du serveur secondaire
    - Si l'utilisateur tape 'exit', on arrête les échanges
    """
    print("=== Serveur Principal ===")

    # 1) Création (ou vérification) des tubes nommés
    create_fifo(tube1_path)
    create_fifo(tube2_path)

    print("Tubes nommés créés/prêts.")

    try:
        with open(tube1_path, "w") as tube1, open(tube2_path, "r") as tube2:
            print("Serveur principal prêt à échanger des messages.")
            while True:
                # Lecture du message utilisateur
                try:
                    message = input("Message à envoyer au serveur secondaire (ou 'exit' pour quitter) : ")
                except (EOFError, KeyboardInterrupt):
                    # Si Ctrl+D ou Ctrl+C, on arrête aussi
                    message = "exit"

                # Vérification de la taille du message
                if len(message) > MAX_MESSAGE_LENGTH:
                    print(f"Message trop long (limite : {MAX_MESSAGE_LENGTH} caractères). Il sera tronqué.")
                    message = message[:MAX_MESSAGE_LENGTH]

                # Envoi au serveur secondaire
                tube1.write(message + "\n")
                tube1.flush()

                # Condition d'arrêt
                if message.lower() == "exit":
                    print("Serveur principal : fin des échanges.")
                    break

                # Lecture de la réponse du serveur secondaire
                response = tube2.readline()
                if not response:  # Lecture vide => le serveur secondaire est peut-être fermé
                    print("Aucune réponse du serveur secondaire (tube fermé ?)")
                    break
                response = response.strip()
                print(f"Serveur principal reçoit : {response}")

    except OSError as e:
        print(f"[ERREUR] Problème lors de l'ouverture/utilisation des tubes : {e}")
    finally:
        # Nettoyage des tubes nommés
        cleanup_fifo(tube1_path)
        cleanup_fifo(tube2_path)
        print("Tubes nommés détruits. Fin du serveur principal.")

def create_fifo(path):
    """
    Crée un tube nommé s'il n'existe pas déjà.
    Gère les cas d'erreur ou d'existence préalable du fichier.
    """
    if not os.path.exists(path):
        try:
            os.mkfifo(path, 0o600)
        except FileExistsError:
            # Dans le cas très improbable où un autre process vient de le créer
            pass
        except OSError as e:
            print(f"[ERREUR] Impossible de créer le tube nommé {path} : {e}")
            sys.exit(1)

def cleanup_fifo(path):
    """
    Supprime (unlink) un tube nommé si celui-ci existe.
    """
    if os.path.exists(path):
        try:
            os.unlink(path)
        except OSError as e:
            print(f"[AVERTISSEMENT] Impossible de supprimer le tube {path} : {e}")

if __name__ == "__main__":
    main()