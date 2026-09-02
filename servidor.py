import socket
import sys
import os

TAM_BUFFER = 4096
ARQUIVOS = "arquivos"

def enviar_tudo(conexao, dados):
    conexao.sendall(dados)

def enviar_em_pedacos(conexao, caminho_arq):
    """evita ter que carregar tudo na mem"""
    with open(caminho_arq, "rb") as arquivo:
        while True:
            pedaco = arquivo.read(TAM_BUFFER)
            if not pedaco:
                break
            enviar_tudo(conexao, pedaco)

def enviar_ok(conexao, caminho_arq):
    tam = os.path.getsize(caminho_arq)
    cabecalho = f"OK {tam}\n".encode("utf-8")
    enviar_tudo(conexao, cabecalho)
    enviar_em_pedacos(conexao, caminho_arq)

def enviar_erro(conexao, mensagem):
    corpo = mensagem.encode("utf-8")
    cabecalho = f"ERRO {len(corpo)}\n".encode("utf-8")
    enviar_tudo(conexao, cabecalho)
    enviar_tudo(conexao, corpo)

def receber_linha(conexao):
    """vai ler byte a byte para formar a linha de requisicao"""
    linha = b""
    while True: 
        byte = conexao.recv(1)
        if not byte:
            break
        if byte == b"\n":
            break
        linha += byte
    return linha.decode("utf-8")

def tratar_cliente(conexao, end_cliente):
    print(f"[servidor] Conexao recebida de {end_cliente}")
    try:
        requisicao = receber_linha(conexao)
        print(f"[servidor] Requisicao: {requisicao!r}")

        partes = requisicao.strip().split(" ", 1)
        if len(partes) != 2 or partes[0] != "GET":
            enviar_erro(conexao, "Requisicao invalida. Use: GET <nome-arquivo>")
            return

        nome_arq = partes[1]
        caminho_arq = os.path.join(ARQUIVOS, nome_arq)

        """o cliente nao pode pedir por arquivos fora da pasta de arquivos"""
        caminho_abs_pasta = os.path.abspath(ARQUIVOS)
        caminho_abs_pedido = os.path.abspath(caminho_arq)
        if not caminho_abs_pedido.startswith(caminho_abs_pasta):
            enviar_erro(conexao, "Acesso negado")
            return
        if not os.path.isfile(caminho_arq):
            enviar_erro(conexao, f"Arquivo '{nome_arq}' nao encontrado")
            return

        enviar_ok(conexao, caminho_arq)
        print(f"[servidor] Arquivo '{nome_arq}' enviado com sucesso")
    finally:
        conexao.close()

def main():
    if len(sys.argv) != 3:
        print(f"Uso: python3 servidor.py <endereco-ip> <porta>")
        sys.exit(1)

    ip = sys.argv[1]
    porta = int(sys.argv[2])

    if not os.path.isdir(ARQUIVOS):
        os.makedirs(ARQUIVOS)

    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_servidor.bind((ip, porta))
    socket_servidor.listen(5)

    print(f"[servidor] Escutando em {ip}:{porta}")
    print("Pressione Ctrl+C para encerrar\n")

    try:
        while True:
            conexao, end_cliente = socket_servidor.accept()
            tratar_cliente(conexao, end_cliente)
    except KeyboardInterrupt:
        print("\n[servidor] Encerrando")
    finally:
        socket_servidor.close()

if __name__ == "__main__":
    main()