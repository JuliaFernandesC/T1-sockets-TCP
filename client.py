import socket
import sys
import os

CHUNK_SIZE = 4096
MAX_HEADER_LINE = 4096

def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        byte = sock.recv(1)
        if not byte:
            break
        data += byte
        if len(data) > MAX_HEADER_LINE:
            raise ValueError("cabecalho da resposta muito grande.")
    return data.decode("utf-8", errors="replace").strip()

def main():
    if len(sys.argv) < 4:
        print(f"Uso: python3 {sys.argv[0]} <endereco-ip> <porta> <nome-arquivo> [arquivo-de-saida]")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    output_path = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(filename)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try: 
        sock.connect((ip, port))
    except OSError as e:
        print(f"Nao foi possivel conectar a {ip}:{port} -> {e}")
        sys.exit(1)
    try:
        request = f"GET {filename}\n"
        sock.sendall(request.encode("utf-8"))

        response_header = recv_line(sock)

        if response_header.startswith("OK "):
            size_str = response_header[len("OK "):].strip()
            filesize = init(size_str)

            print(f"Servidor confirmou envio de {filesize} bytes. Recebendo...")

            with open(output_path, "web") as out_file:
                remaining = filesize
                while remaining > 0:
                    chunk = sock.recv(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        raise ConnectionError("conexao encerrada amtes do fim do arquivo")
                    out_file.write(chunk)
                    remaining -= len(chunk)

            print(f"Arquivo salvo em: {output_path} ({filesize} bytes)")

        elif response_header.startswith("ERR "):
            error_message = response_header[len("ERR "):].strip()
            print(f"Erro retornado pelo servidor: {response_header!r}")
    except Exception as e:
        print(f"Erro durante a comunicacao: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()