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
    Programme : serveur secondaire
    - Se connecte aux tubes nommés existants (créés par le serveur principal).
    - Lit les messages envoyés par le serveur principal.
    - Affiche ces messages.
    - Demande à l'utilisateur une réponse à renvoyer au serveur principal.
    - S'arrête quand il reçoit 'exit'.
    """
    print("=== Serveur Secondaire ===")
    print("Prêt à se connecter aux tubes nommés.")

    # Vérifier que les tubes existent
    if not os.path.exists(tube1_path) or not os.path.exists(tube2_path):
        print(f"[ERREUR] Les tubes {tube1_path} ou {tube2_path} n'existent pas. Lancez d'abord le serveur principal.")
        sys.exit(1)

    try:
        with open(tube1_path, "r") as tube1, open(tube2_path, "w") as tube2:
            print("Connexion aux tubes réussie.")
            while True:
                # Lecture du message du serveur principal
                message = tube1.readline()
                if not message:
                    # Le tube est peut-être fermé (serveur principal arrêté)
                    print("Serveur principal déconnecté (tube fermé ?). Fin du serveur secondaire.")
                    break

                message = message.strip()
                if message.lower() == "exit":
                    print("Serveur secondaire : fin des échanges (reçu 'exit').")
                    break

                print(f"Serveur secondaire reçoit : {message}")

                # Lecture de la réponse utilisateur
                try:
                    response = input("Réponse à envoyer au serveur principal : ")
                except (EOFError, KeyboardInterrupt):
                    # Si Ctrl+D ou Ctrl+C, on arrête le serveur secondaire
                    response = "exit"

                # Vérification de la taille du message
                if len(response) > MAX_MESSAGE_LENGTH:
                    print(f"Message trop long (limite : {MAX_MESSAGE_LENGTH} caractères). Il sera tronqué.")
                    response = response[:MAX_MESSAGE_LENGTH]

                # Envoi de la réponse
                tube2.write(response + "\n")
                tube2.flush()

                if response.lower() == "exit":
                    print("Serveur secondaire : fin des échanges (envoi 'exit').")
                    break

    except OSError as e:
        print(f"[ERREUR] Problème lors de l'ouverture/utilisation des tubes : {e}")
    finally:
        print("Serveur secondaire terminé.")

if __name__ == "__main__":
    main()