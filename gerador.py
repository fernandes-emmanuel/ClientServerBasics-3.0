import random
import string

COMANDOS = ['UPPER', 'LOWER', 'REVERSE', 'VOWELS']
CARACTERES = string.ascii_letters + '      '


def gerar_requisicoes(n, semente=None):
    rng = random.Random(semente)
    requests = []
    for _ in range(n):
        cmds = rng.choices(COMANDOS, k=rng.randint(1, 3))
        texto = ''.join(rng.choices(CARACTERES, k=rng.randint(10, 80)))
        requests.append(f"{','.join(cmds)} {texto}")
    return requests
