# T1 - Aplicação Cliente-Servidor com Sockets TCP - Julia Fernandes e Luiza Rosito

Servidor de arquivos simples em Python usando sockets TCP puros (sem dependências externas).

## Requisitos

- Python 3 instalado (`python3 --version` para conferir)

## Estrutura de arquivos

```
.
├── servidor.py
├── cliente.py
├── arquivos/ # pasta de onde o servidor le os arquivos disponiveis para download
└── downloads/ # pasta onde o cliente salva os arquivos recebidos (criada automaticamente)
```

Antes de rodar o servidor, coloque os arquivos que devem ficar disponíveis para download dentro da pasta `arquivos/` (crie a pasta se ela não existir).

## Como executar

### Opção 1 — Testando na mesma máquina (localhost)

1. Abra **dois terminais** na pasta do projeto.

2. No primeiro terminal, suba o servidor:
   ```bash
   python3 servidor.py 127.0.0.1 5000
   ```
   Você deve ver:
   ```
   [servidor] Escutando em 127.0.0.1:5000
   ```

3. No segundo terminal, rode o cliente pedindo um arquivo que esteja dentro de `arquivos/`:
   ```bash
   python3 cliente.py 127.0.0.1 5000 nome-do-arquivo.txt
   ```

4. O arquivo será salvo em `downloads/nome-do-arquivo.txt`.

### Opção 2 — Testando em dois computadores diferentes

Os dois computadores precisam estar **na mesma rede local** (mesmo Wi-Fi ou mesmo cabo/switch).

#### Passo 1: Escolher quem é o servidor e quem é o cliente

Decidam qual máquina vai hospedar os arquivos (**servidor**) e qual vai baixar (**cliente**).

#### Passo 2: Descobrir o IP da máquina servidora

Na máquina que vai rodar o **servidor**, descubra o IP na rede local:

- **Linux/Mac**:
  ```bash
  ip a
  ```
  ou
  ```bash
  ifconfig
  ```
  Procure a interface conectada à rede (ex: `eth0`, `enp1s0`, `wlan0`) e o endereço `inet` no formato `192.168.x.x`.

- **Windows**:
  ```powershell
  ipconfig
  ```
  Procure o adaptador que está realmente conectado ("Media disconnected" = não está em uso) e anote o campo **Endereço IPv4** (ex: `192.168.1.115`).

#### Passo 3: Colocar os arquivos na pasta do servidor

Na máquina servidora, coloque o(s) arquivo(s) que o cliente vai poder baixar dentro da pasta `arquivos/`.

#### Passo 4: Subir o servidor

Na máquina servidora, rode (substituindo a porta se quiser usar outra):

```bash
python3 servidor.py 0.0.0.0 5000
```

Usar `0.0.0.0` faz o servidor aceitar conexões vindas de qualquer IP da rede, não só da própria máquina.

Confirme que aparece:
```
[servidor] Escutando em 0.0.0.0:5000
```

#### Passo 5: Rodar o cliente na outra máquina

Na máquina cliente, use o IP anotado no Passo 2:

```bash
python3 cliente.py <IP-DO-SERVIDOR> 5000 nome-do-arquivo.txt
```

Exemplo:
```bash
python3 cliente.py 192.168.1.115 5000 mensagem.txt
```

O arquivo será salvo em `downloads/` na máquina cliente.

## Problema que tivemos: Firewall do Windows

### Liberando a porta no Firewall do Windows

No **PowerShell como Administrador**, na máquina que vai rodar o servidor:

```powershell
New-NetFirewallRule -DisplayName "Servidor T1 Sockets" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

(troque `5000` pela porta usada, se for diferente)


## Testando arquivo inexistente

Para verificar o tratamento de erro do servidor, peça um arquivo que não existe na pasta `arquivos/`:

```bash
python3 cliente.py <IP-DO-SERVIDOR> 5000 arquivo-que-nao-existe.txt
```

O cliente deve exibir a mensagem de erro enviada pelo servidor, sem travar.
