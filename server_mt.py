import argparse
import threading
from socket import *
from constCS import *
from operacoes import processar

parser = argparse.ArgumentParser(description="Servidor multithreaded")
parser.add_argument('-p', '--porta', type=int, default=PORT)
parser.add_argument('-a', '--atraso', type=float, default=0, help="tempo de processamento simulado (ms)")
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()


def atender(conn, addr, msg):
    try:
        response = processar(msg, args.atraso / 1000)
        conn.send(str.encode(response))
        if args.verbose:
            print(f"[{threading.current_thread().name}] {addr} Recebido: {msg} -> {response}")
    finally:
        conn.close()


s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind((HOST, args.porta))
s.listen(BACKLOG)
print(f"Servidor (multithreaded) aguardando conexões na porta {args.porta}...", flush=True)

while True:
    conn, addr = s.accept()
    data = conn.recv(1024)
    if not data:
        conn.close()
        continue
    threading.Thread(target=atender, args=(conn, addr, bytes.decode(data))).start()
