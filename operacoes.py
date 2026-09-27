import time


def processar(msg, atraso=0):
    if atraso:
        time.sleep(atraso)

    # O formato da mensagem esperada eh: "CMD1,CMD2 payload"
    parts = msg.split(' ', 1)
    if len(parts) < 2:
        return "Erro: Formato invalido. Use 'CMD payload'"

    cmds_str, payload = parts[0], parts[1]
    response = payload
    for cmd in cmds_str.split(','):
        if cmd == 'UPPER':
            response = response.upper()
        elif cmd == 'LOWER':
            response = response.lower()
        elif cmd == 'REVERSE':
            response = response[::-1]
        elif cmd == 'VOWELS':
            response = ''.join([c for c in response if c.lower() in 'aeiou'])
        else:
            return f"Erro: Comando desconhecido '{cmd}'"
    return response
