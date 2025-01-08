import os
import time
import sys
import mmap
import posix_ipc

# Noms (identiques)
TUBE_REQUEST = "/tmp/sp_request"
TUBE_RESPONSE = "/tmp/sp_response"
SHM_NAME = "/sp_shm"
SHM_SIZE = 1024

def main():
    print("[Secondaire] Démarrage...")

    # 1) Vérifier si le tube request existe
    if not os.path.exists(TUBE_REQUEST) or not os.path.exists(TUBE_RESPONSE):
        print("[Secondaire] Les tubes nommés n'existent pas. Lancez d'abord le principal.")
        sys.exit(1)
    # 2) Attacher la mémoire partagée
    try:
        shm = posix_ipc.SharedMemory(SHM_NAME)
        shm_map = mmap.mmap(shm.fd, shm.size)
        shm.close_fd()
    except posix_ipc.ExistentialError:
        print("[Secondaire] Mémoire partagée introuvable. Abandon.")
        sys.exit(1)

    # 3) Boucle principale : on lit le tube request en bloc (bloquant)
    try:
        while True:
            print("[Secondaire] En attente d'une requête...")
            with open(TUBE_REQUEST, "r") as req_tube:
                for line in req_tube:
                    line = line.strip()
                    if not line:
                        continue
                    print(f"[Secondaire] Requête reçue: {line}")

                    # Ex: "TRAITER|foo"
                    parts = line.split("|")
                    cmd = parts[0]
                    arg = parts[1] if len(parts) > 1 else ""

                    # On lit la mémoire partagée pour voir le drapeau
                    shm_map.seek(0)
                    flag = shm_map.read(16).strip(b'\x00').decode()
                    print(f"[Secondaire] Flag en shm: {flag}")

                    if cmd == "TRAITER":
                        # Simuler un traitement
                        print("[Secondaire] Simulation de traitement...")
                        time.sleep(3)

                        # Écrire un message de réponse
                        with open(TUBE_RESPONSE, "w") as resp_tube:
                            resp_tube.write(f"Resultat pour {arg} = OK\n")
                            resp_tube.flush()

                        # On peut aussi changer le flag
                        shm_map.seek(0)
                        shm_map.write(b"DONE")
                        shm_map.flush()
                    else:
                        print("[Secondaire] Commande inconnue.")
    except KeyboardInterrupt:
        print("[Secondaire] Interrompu par Ctrl+C.")
    finally:
        shm_map.close()

if __name__ == '__main__':
    main()