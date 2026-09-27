import argparse
import statistics
import subprocess
import sys
import time
from constCS import *
from gerador import gerar_requisicoes
import client
import client_mt

CONFIGURACOES = [
    ("Single-threaded (cliente e servidor)", client.executar, 'server.py', 1),
    ("Multithread apenas no servidor", client.executar, 'server_mt.py', 1),
    ("Multithread no cliente e no servidor", client_mt.executar, 'server_mt.py', 1),
    ("Multithread no cliente + 2 servidores multithread", client_mt.executar, 'server_mt.py', 2),
]


def iniciar_servidores(script, quantidade, atraso):
    processos = [
        subprocess.Popen([sys.executable, script, '-p', str(PORT + i), '-a', str(atraso)],
                         stdout=subprocess.DEVNULL)
        for i in range(quantidade)
    ]
    time.sleep(1)
    return processos


def parar_servidores(processos):
    for p in processos:
        p.terminate()
        p.wait()


parser = argparse.ArgumentParser(description="Experimento de desempenho single-threaded vs multithreaded")
parser.add_argument('-n', '--requisicoes', type=int, default=2000)
parser.add_argument('-r', '--repeticoes', type=int, default=5)
parser.add_argument('-a', '--atrasos', type=float, nargs='+', default=[0, 1, 5],
                    help="tempos de processamento simulados no servidor (ms)")
parser.add_argument('-s', '--semente', type=int, default=42)
args = parser.parse_args()

requests = gerar_requisicoes(args.requisicoes, args.semente)
print(f"{args.requisicoes} requisições, {args.repeticoes} repetições por configuração, "
      f"até {MAX_THREADS} threads simultâneas no cliente\n")

for atraso in args.atrasos:
    print(f"### Processamento simulado no servidor: {atraso:g} ms\n")
    print("| Configuração | Tempo médio (s) | Desvio padrão (s) | Vazão (req/s) | Speedup |")
    print("|---|---|---|---|---|")
    referencia = None
    base = None

    for nome, executar, script, qtd_servidores in CONFIGURACOES:
        servidores = [(HOST, PORT + i) for i in range(qtd_servidores)]
        processos = iniciar_servidores(script, qtd_servidores, atraso)
        tempos = []
        try:
            for _ in range(args.repeticoes):
                responses, tempo = executar(requests, servidores)
                tempos.append(tempo)
                falhas = sum(1 for r in responses if r.startswith(client.FALHA))
                if falhas:
                    print(f"ATENÇÃO: {falhas} falhas de conexão em '{nome}'")
                if referencia is None:
                    referencia = responses
                elif responses != referencia:
                    print(f"ATENÇÃO: respostas divergentes em '{nome}'")
        finally:
            parar_servidores(processos)

        media = statistics.mean(tempos)
        desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0
        base = base or media
        print(f"| {nome} | {media:.3f} | {desvio:.3f} | {args.requisicoes / media:.0f} | {base / media:.2f}x |",
              flush=True)
    print()
