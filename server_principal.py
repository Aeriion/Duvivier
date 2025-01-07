import os

# Chemins des tubes nommés
tube1_path = "/tmp/dwtube1"  # Tube principal -> secondaire
tube2_path = "/tmp/wdtube1"  # Tube secondaire -> principal

# Création des tubes nommés
os.mkfifo(tube1_path, 0o600)
os.mkfifo(tube2_path, 0o600)
print("Tubes nommés créés.")

MAX_MESSAGE_LENGTH = 200  # Limitation de la taille des messages

try:
    with open(tube1_path, "w") as tube1, open(tube2_path, "r") as tube2:
        print("Serveur principal prêt à échanger des messages.")
        while True:
            # Lecture du message utilisateur
            message = input("Message à envoyer au serveur secondaire (ou 'exit' pour quitter) : ")

            # Vérification de la taille du message
            if len(message) > MAX_MESSAGE_LENGTH:
                print(f"Message trop long (limite : {MAX_MESSAGE_LENGTH} caractères). Il sera tronqué.")
                message = message[:MAX_MESSAGE_LENGTH]

            tube1.write(message + "\n")
            tube1.flush()

            if message.lower() == "exit":
                print("Serveur principal : fin des échanges.")
                break

            # Lecture de la réponse du serveur secondaire
            response = tube2.readline().strip()
            print(f"Serveur principal reçoit : {response}")

finally:
    os.unlink(tube1_path)  # Nettoyage du tube 1
    os.unlink(tube2_path)  # Nettoyage du tube 2
    print("Tubes nommés détruits.")