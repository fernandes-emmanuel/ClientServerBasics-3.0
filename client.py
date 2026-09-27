import argparse
import time
from socket import *
from constCS import *
from gerador import gerar_requisicoes

FALHA = "Falha na conexão"


def enviar(req, servidor):
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(servidor)
        s.send(str.encode(req))
        data = b''
        while chunk := s.recv(1024):
            data += chunk
        s.close()
        return bytes.decode(data)
    except OSError as e:
        return f"{FALHA}: {e}"


def executar(requests, servidores):
    responses = []
    inicio = time.perf_counter()
    for i, req in enumerate(requests):
        responses.append(enviar(req, servidores[i % len(servidores)]))
    return responses, time.perf_counter() - inicio


def main(executar, descricao):
    parser = argparse.ArgumentParser(description=descricao)
    parser.add_argument('-n', '--requisicoes', type=int, default=1000)
    parser.add_argument('-p', '--portas', type=int, nargs='+', default=[PORT])
    parser.add_argument('-s', '--semente', type=int, default=None)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    servidores = [(HOST, p) for p in args.portas]
    requests = gerar_requisicoes(args.requisicoes, args.semente)
    responses, tempo = executar(requests, servidores)

    if args.verbose:
        for req, resp in zip(requests, responses):
            print(f"Enviando: {req}\nResposta do servidor: {resp}\n")

    falhas = sum(1 for r in responses if r.startswith(FALHA))
    print(f"{len(requests)} requisições em {tempo:.3f} s "
          f"({len(requests) / tempo:.0f} req/s, {falhas} falhas)")


if __name__ == '__main__':
    main(executar, "Cliente single-threaded")
