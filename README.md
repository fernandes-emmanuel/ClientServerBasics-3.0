# Processador de Texto Remoto Multithread (Cliente/Servidor)

Este projeto estende o processador de texto remoto da tarefa anterior (ASR 04) com **multithreading** no cliente e no servidor, geração automática de requisições e um experimento de desempenho comparando as versões single-threaded e multithreaded.

O comportamento funcional é o mesmo da versão anterior: o cliente envia um texto (payload) junto com uma ou mais operações, e o servidor devolve o texto processado.

## Funcionalidades Disponíveis

- `UPPER`: Converte todo o texto para letras maiúsculas.
- `LOWER`: Converte todo o texto para letras minúsculas.
- `REVERSE`: Inverte a ordem dos caracteres do texto.
- `VOWELS`: Filtra e retorna apenas as vogais presentes no texto.

As operações podem ser encadeadas em uma única requisição, no formato `COMANDO1,COMANDO2 texto_a_processar`.

Exemplos:
- `UPPER hello, world` -> `HELLO, WORLD`
- `UPPER,REVERSE testes de rede` -> `EDER ED SETSET`
- `VOWELS,UPPER sistemas distribuidos` -> `IEAIIUIO`

## Estrutura

| Arquivo | Descrição |
|---|---|
| `constCS.py` | Endereço, porta, backlog do servidor e limite de threads simultâneas no cliente |
| `operacoes.py` | Processamento das requisições (compartilhado pelos dois servidores) |
| `gerador.py` | Geração automática de requisições aleatórias (comandos e textos) |
| `server.py` | Servidor single-threaded |
| `server_mt.py` | Servidor multithreaded |
| `client.py` | Cliente single-threaded (requisições enviadas em sequência) |
| `client_mt.py` | Cliente multithreaded (uma thread por requisição) |
| `experimento.py` | Executa o experimento de desempenho automaticamente |

## Arquitetura Multithread

**Servidor (`server_mt.py`):** a thread principal fica em loop aceitando conexões. A cada conexão aceita, ela recebe a requisição e dispara uma nova thread para executá-la. Essa thread processa a requisição, envia a resposta ao cliente e fecha a conexão. Enquanto isso, a thread principal já volta a aceitar a próxima conexão.

**Cliente (`client_mt.py`):** para cada requisição, o cliente cria uma nova thread, que abre a conexão, envia a requisição e aguarda a resposta. Assim, várias requisições ficam em andamento ao mesmo tempo, inclusive para servidores diferentes: as requisições são distribuídas em rodízio entre as portas informadas. O número de threads ativas ao mesmo tempo é limitado por um semáforo (`MAX_THREADS`), para não esgotar os recursos do sistema quando milhares de requisições são geradas.

Cada requisição usa uma conexão TCP própria nas duas versões, então a única diferença entre elas é o uso de threads. O servidor fecha a conexão depois de enviar a resposta, e o cliente lê até o fim da conexão (EOF). Com isso, o estado `TIME_WAIT` fica do lado do servidor, e o cliente não esgota as portas efêmeras quando envia milhares de requisições seguidas.

## Como Executar

Servidores (`-p` porta, `-a` tempo de processamento simulado em ms, `-v` exibe as requisições recebidas):

```
python server.py
python server_mt.py -v
```

Clientes (`-n` quantidade de requisições, `-p` uma ou mais portas de servidores, `-s` semente do gerador aleatório, `-v` exibe requisições e respostas):

```
python client.py -n 10 -v
python client_mt.py -n 1000
python client_mt.py -n 1000 -p 5678 5679
```

Experimento completo (inicia e encerra os servidores sozinho):

```
python experimento.py -n 5000 -r 5 -a 0 1 5
```

Com a mesma semente (`-s`), os dois clientes geram as mesmas requisições e produzem exatamente a mesma saída, o que mostra que o comportamento funcional é idêntico nas duas versões. O `experimento.py` também confere isso a cada execução: compara as respostas de todas as configurações com as da versão single-threaded.

## Experimento de Desempenho

### Metodologia

- O mesmo conjunto de **5000 requisições** aleatórias (semente fixa 42) foi enviado em cada configuração, com **5 repetições**. O tempo medido vai do envio da primeira requisição até o recebimento da última resposta.
- Configurações comparadas:
  1. **Single-threaded**: `client.py` + `server.py` (versão da tarefa anterior, com geração automática de requisições);
  2. **Multithread apenas no servidor**: `client.py` + `server_mt.py`;
  3. **Multithread no cliente e no servidor**: `client_mt.py` + `server_mt.py`;
  4. **Multithread no cliente com 2 servidores multithread**: `client_mt.py` + 2 × `server_mt.py`.
- As operações de texto são muito rápidas (microssegundos). Por isso, o experimento foi repetido com um tempo de processamento simulado no servidor (`sleep` de 0, 1 e 5 ms por requisição), para representar um serviço com custo real, como acesso a disco ou banco de dados.
- Ambiente: Windows 11, Python 3.14.3, processador com 24 threads lógicas, cliente e servidor na mesma máquina (`127.0.0.1`), no máximo 100 threads simultâneas no cliente.
- Em todas as execuções, as respostas foram idênticas às da versão single-threaded, e não houve nenhuma falha de conexão.

### Resultados

**Processamento de 0 ms (apenas as operações de texto):**

| Configuração | Tempo médio (s) | Desvio padrão (s) | Vazão (req/s) | Speedup |
|---|---|---|---|---|
| Single-threaded | 1.175 | 0.188 | 4257 | 1.00x |
| Multithread apenas no servidor | 2.181 | 0.243 | 2293 | 0.54x |
| Multithread no cliente e no servidor | 1.472 | 0.285 | 3397 | 0.80x |
| Multithread no cliente + 2 servidores | 1.583 | 0.055 | 3159 | 0.74x |

**Processamento de 1 ms:**

| Configuração | Tempo médio (s) | Desvio padrão (s) | Vazão (req/s) | Speedup |
|---|---|---|---|---|
| Single-threaded | 8.239 | 0.171 | 607 | 1.00x |
| Multithread apenas no servidor | 9.330 | 0.802 | 536 | 0.88x |
| Multithread no cliente e no servidor | 1.062 | 0.158 | 4706 | 7.75x |
| Multithread no cliente + 2 servidores | 1.553 | 0.151 | 3220 | 5.31x |

**Processamento de 5 ms:**

| Configuração | Tempo médio (s) | Desvio padrão (s) | Vazão (req/s) | Speedup |
|---|---|---|---|---|
| Single-threaded | 28.412 | 0.489 | 176 | 1.00x |
| Multithread apenas no servidor | 28.990 | 0.342 | 172 | 0.98x |
| Multithread no cliente e no servidor | 1.408 | 0.138 | 3550 | 20.18x |
| Multithread no cliente + 2 servidores | 1.542 | 0.091 | 3242 | 18.42x |

### Análise

- **Multithread apenas no servidor não trouxe ganho; na verdade, foi mais lento.** O cliente single-threaded só envia a próxima requisição depois de receber a resposta da anterior. Então nunca há mais de uma requisição no servidor ao mesmo tempo, e as threads do servidor não têm nada para executar em paralelo. O que resta é o custo de criar uma thread por requisição, que é maior que o próprio processamento. Por isso esta versão foi a mais lenta com 0 ms.
- **Com multithread no cliente e no servidor, o ganho aparece assim que a requisição tem algum custo.** Com 1 ms de processamento, o tempo caiu de 8,2 s para 1,1 s (7,7x). Com 5 ms, caiu de 28,4 s para 1,4 s (20x). Com até 100 requisições em andamento, o tempo de espera de uma se sobrepõe ao das outras. O tempo total quase não muda com o custo da requisição, enquanto na versão sequencial ele cresce linearmente (5000 × tempo de cada requisição).
- **Sem custo de processamento (0 ms), o multithreading não compensa.** As operações de texto levam microssegundos, e na rede local a comunicação também é muito rápida. Nesse cenário, criar threads e disputar o GIL do Python custa mais do que se ganha em paralelismo.
- **Dois servidores não foram mais rápidos que um.** O gargalo passou a ser o próprio cliente: um único processo Python, com GIL, criando e gerenciando milhares de threads e conexões. O servidor multithread sozinho já atende todas as requisições concorrentes que o cliente consegue gerar. Distribuir entre servidores só ajudaria com servidores em máquinas diferentes ou com processamento que use CPU de verdade.
- **Conclusão:** o multithreading só melhora o desempenho quando existe concorrência real, ou seja, várias requisições em andamento ao mesmo tempo, o que exige threads também no cliente. Além disso, o custo de cada requisição precisa ser maior que o custo de criar as threads. Nessas condições, o sistema multithread processou a mesma carga até 20 vezes mais rápido que a versão single-threaded.
