import socket
import sys
import os

TAM_BUFFER = 4096
DOWNLOADS = "downloads"

def receber_linha(conexao):
    linha = b""
    total_recvs = 0
    while True:
        byte = conexao.recv(1)
        total_recvs += 1
        if not byte:
            break
        if byte == b"\n":
            break
        linha += byte
    return linha.decode("utf-8"), total_recvs

def receber_tudo(conexao, tam):
    """recv em loop ate chegar no tamanho de bytes. Usada so para as mensagens de erro (pequenas)"""
    dados_recebidos = b""
    total_recvs = 0
    while len(dados_recebidos) < tam:
        restante = tam - len(dados_recebidos)
        pedaco = conexao.recv(min(TAM_BUFFER, restante))
        total_recvs += 1
        if not pedaco:
            raise ConnectionError("Conexao encerrada antes de completar o recebimento")
        dados_recebidos += pedaco
    return dados_recebidos, total_recvs

def receber_em_pedacos(conexao, tam, destino):
    """recebe o arquivo em pedasos e escrewve direto no disco"""
    bytes_restantes = tam
    total_recvs = 0

    with open(destino, "wb") as arquivo:
        while bytes_restantes > 0:
            pedaco = conexao.recv(min(TAM_BUFFER, bytes_restantes))
            if not pedaco:
                raise ConnectionError("Conexao encerrada antes de completar o recebimento")
            arquivo.write(pedaco)
            bytes_restantes -= len(pedaco)
            total_recvs += 1

    return total_recvs

def main():
    if len(sys.argv) != 4:
        print(f"Uso: python3 cliente.py <endereco-ip> <porta> <nome-arquivo>")
        sys.exit(1)

    ip = sys.argv[1]
    porta = int(sys.argv[2])
    nome_arq = sys.argv[3]

    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try: 
        socket_cliente.connect((ip, porta))

    except OSError as e:
        print(f"Nao foi possivel conectar a {ip}:{porta} -> {e}")
        sys.exit(1)

    try:
        requisicao = f"GET {nome_arq}\n"
        socket_cliente.sendall(requisicao.encode("utf-8"))

        cabecalho, recvs_cab = receber_linha(socket_cliente)
        print(f"[cliente] Cabecalho recebido: {cabecalho!r}")

        partes = cabecalho.strip().split(" ", 1)
        if len(partes) != 2:
            print("[cliente] Resposta invalida do servidor")

        status, tamanho_str = partes
        tam = int(tamanho_str)

        if status == "OK":
            if not os.path.isdir(DOWNLOADS):
                os.makedirs(DOWNLOADS)
            destino = os.path.join(DOWNLOADS, nome_arq)
            recvs_corpo = receber_em_pedacos(socket_cliente, tam, destino)
            total_recvs = recvs_cab + recvs_corpo
            
            print(f"[cliente] Arquivo salvo em '{destino}' ({tam} bytes)")
            print(f"Total de chamadas de pimitivas de recepção: {total_recvs}")

        elif status == "ERRO":
            mensagem, recvs_corpo = receber_tudo(socket_cliente, tam)
            total_recvs = recvs_cab + recvs_corpo
            
            print(f"[cliente] Erro do servidor: {mensagem.decode('utf-8')}")
            print(f"Total de chamadas de pimitivas de recepção: {total_recvs}")

        else:
            print(f"[cliente] Status desconhecido: {status}")

    except Exception as e:
            print(f"Erro durante a comunicacao: {e}")
    finally:
        socket_cliente.close()

if __name__ == "__main__":
    main()