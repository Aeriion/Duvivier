#! /usr/bin/env python3
# _*_ coding: utf8 _*_

from multiprocessing import shared_memory
import os, sys, time

segment_name = "shared_segment_tp"
segment_size = 1024

try:
    # Création du segment mémoire partagé
    shm = shared_memory.SharedMemory(name=segment_name, create=True, size=segment_size)
    print(f"Segment mémoire créé par le serveur principal. Nom: {shm.name}, Taille: {len(shm.buf)} octets")

    # Serveur principal écrit un premier message dans la mémoire partagée
    initial_message = b"Bonjour, serveur sec!"
    if len(initial_message) > segment_size:
        raise ValueError("Message trop grand pour le segment mémoire partagé.")
    shm.buf[:len(initial_message)] = initial_message
    print("Serveur principal a écrit : Bonjour, serveur sec!")

except (FileExistsError, ValueError, OSError) as e:
    print(f"Erreur : {e}")
    exit(1)

try:
    pid = os.fork()
except OSError as e:
    print(f"Erreur lors du fork : {e}")
    shm.close()
    shm.unlink()
    exit(1)

if pid == 0:  # Serveur secondaire
    try:
        # Attachement au segment mémoire partagé
        shm_secondary = shared_memory.SharedMemory(name=segment_name)
        print("Serveur secondaire attaché au segment mémoire partagé.")

        # Lecture du message du serveur principal
        message_from_principal = bytes(shm_secondary.buf[:20]).decode("utf-8")
        print(f"Serveur secondaire lit : {message_from_principal}")

        # Serveur secondaire répond dans le segment mémoire
        response_message = b"Recu, merci principal!"
        shm_secondary.buf[20:20 + len(response_message)] = response_message
        print("Serveur secondaire a écrit : Recu, merci principal!")

        # Attente pour permettre au serveur principal de lire
        time.sleep(2)

        # Nettoyage avant d'écrire la confirmation
        shm.buf[40:60] = bytearray(b' ' * 20)  # Remplit la section avec des espaces


        # Lecture de la confirmation du serveur principal
        confirmation = bytes(shm_secondary.buf[40:60]).decode("utf-8").strip()
        print(f"Serveur secondaire lit la confirmation : {confirmation}")

        shm_secondary.close()
    except Exception as e:
        print(f"Erreur dans le serveur secondaire : {e}")
    os._exit(0)

else:  # Serveur principal
    try:
        os.waitpid(pid, 0)  # Attente du processus secondaire

        # Lecture de la réponse du serveur secondaire
        response_from_secondary = bytes(shm.buf[20:42]).decode("utf-8")
        print(f"Serveur principal lit : {response_from_secondary}")

        # Nettoyage avant d'écrire la confirmation
        shm.buf[40:60] = bytearray(b' ' * 20)  # Remplit la section avec des espaces

        # Serveur principal envoie une confirmation
        confirmation_message = b"Confirmation bien recu!"
        shm.buf[40:40 + len(confirmation_message)] = confirmation_message
        print("Serveur principal a écrit : Confirmation bien recu!")

    except ChildProcessError as e:
        print(f"Erreur lors de l'attente du processus secondaire : {e}")
    finally:
        # Nettoyage du segment mémoire
        try:
            shm.close()
            shm.unlink()
            print("Segment mémoire partagé détruit.")
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")
