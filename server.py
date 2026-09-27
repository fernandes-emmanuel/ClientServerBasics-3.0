import argparse
from socket import *
from constCS import *
from operacoes import processar

parser = argparse.ArgumentParser(description="Servidor single-threaded")
parser.add_argument('-p', '--porta', type=int, default=PORT)
parser.add_argument('-a', '--atraso', type=float, default=0, help="tempo de processamento simulado (ms)")
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind((HOST, args.porta))
s.listen(BACKLOG)
print(f"Servidor (single-threaded) aguardando conexões na porta {args.porta}...", flush=True)

while True:
    conn, addr = s.accept()
    data = conn.recv(1024)
    if data:
        msg = bytes.decode(data)
        response = processar(msg, args.atraso / 1000)
        conn.send(str.encode(response))
        if args.verbose:
            print(f"{addr} Recebido: {msg} -> {response}")
    conn.close()
