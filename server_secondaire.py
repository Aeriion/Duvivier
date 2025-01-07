import os

# Chemins des tubes nommés
tube1_path = "/tmp/dwtube1"  # Tube principal -> secondaire
tube2_path = "/tmp/wdtube1"  # Tube secondaire -> principal

print("Serveur secondaire prêt à se connecter aux tubes nommés.")

MAX_MESSAGE_LENGTH = 200  # Limitation de la taille des messages

try:
    with open(tube1_path, "r") as tube1, open(tube2_path, "w") as tube2:
        while True:
            # Lecture du message du serveur principal
            message = tube1.readline().strip()
            if message.lower() == "exit":
                print("Serveur secondaire : fin des échanges.")
                break
            print(f"Serveur secondaire reçoit : {message}")

            # Lecture de la réponse utilisateur
            response = input("Réponse à envoyer au serveur principal : ")

            # Vérification de la taille du message
            if len(response) > MAX_MESSAGE_LENGTH:
                print(f"Message trop long (limite : {MAX_MESSAGE_LENGTH} caractères). Il sera tronqué.")
                response = response[:MAX_MESSAGE_LENGTH]

            tube2.write(response + "\n")
            tube2.flush()

finally:
    print("Serveur secondaire terminé.")