import threading
import time
from constCS import *
from client import enviar, main


def executar(requests, servidores):
    responses = [None] * len(requests)
    limite = threading.BoundedSemaphore(MAX_THREADS)

    def tarefa(i, req):
        try:
            responses[i] = enviar(req, servidores[i % len(servidores)])
        finally:
            limite.release()

    threads = []
    inicio = time.perf_counter()
    for i, req in enumerate(requests):
        limite.acquire()
        t = threading.Thread(target=tarefa, args=(i, req))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return responses, time.perf_counter() - inicio


if __name__ == '__main__':
    main(executar, "Cliente multithreaded")
