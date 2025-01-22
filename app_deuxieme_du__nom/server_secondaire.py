import os
import time
import sys
import mmap
import posix_ipc



TUBE_REQUEST = "/tmp/sp_request"
TUBE_RESPONSE = "/tmp/sp_response"
SHM_NAME = "/sp_shm"
SHM_SIZE = 1024



BANNED_WORDS = ["méchant", "bar", "insulte"]

def censor_message(original):
    words = original.split()
    for i in range(len(words)):
        w = words[i].lower()
        if w in BANNED_WORDS:
            words[i] = "*" * len(words[i])
    return " ".join(words)


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

                    parts = line.split("|")
                    cmd = parts[0]
                    arg = parts[1] if len(parts) > 1 else ""

                    # On lit la mémoire partagée pour voir le drapeau
                    shm_map.seek(0)
                    flag = shm_map.read(16).strip(b'\x00').decode()
                    print(f"[Secondaire] Flag en shm: {flag}")



                    if cmd == "CENSOR":
                        # "arg" = "Pseudo###TexteOriginal"
                        subparts = arg.split("###", 1)
                        user_pseudo = subparts[0]
                        raw_msg = subparts[1] if len(subparts) > 1 else ""

                        # On censure
                        censored = censor_message(raw_msg)

                        # renvoyer "CENSORED|Pseudo###MessageCensure"
                        with open(TUBE_RESPONSE, "w") as resp_tube:
                            resp_tube.write(f"CENSORED|{user_pseudo}###{censored}\n")
                            resp_tube.flush()


                    else:
                        print("[Secondaire] Commande inconnue.")
    except KeyboardInterrupt:
        print("[Secondaire] Interrompu par Ctrl+C.")
    finally:
        shm_map.close()

if __name__ == '__main__':
    main()