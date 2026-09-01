import socket
import sys
import os
import threading 

CHUNK_SIZE = 4096
MAX_REQUEST_LINE = 4096

def recv_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        byte = conn.recv(1)
        if not byte:
            break
        data += byte
        if len(data) > MAX_REQUEST_LINE:
            raise ValueError("linha de requisição muito grande.")
    return data.decode("utf-8", errors="replace").strip()

def send_error(conn, message):
    conn.sendall(f"ERRO {message}\n".encode("utf-8"))

def send_file(conn, filepath):
    filesize = os.path.getsize(filepath)
    header = f"OK {filesize}\n".encode("utf-8")
    conn.sendall(header)

    with open(filepath, "rb") as f:
        while True:
            chunk = f,read(CHUNK_SIZE)
            if not chunk:
                break
            conn.sendall(chunk)

def handle_client(conn, addr, base_dir):
    print(f"[+] Conexão de {addr}")
    try:
        request = recv_line(conn)
        print(f"    Requisição: {request!r}")

        if not request.startswith("GET "):
            send_error(conn, "comando invalido, use: GET <arquivo>")
            return
        filename = request[len("GET "):].strip()
        if not filename:
            send_error(conn, "nome de arquivo vazio.")
            return
        safe_path = os.path.normpath(os.path.join(base_dir, filename))
        if not safe_path.startswith(os.path.abspath(base_dir)):
            send_error(conn, "acesso negado.")
            return
        if not os.path.isfile(safe_path):
            send_error(conn, f"arquivo '{filename}' não encontrado.")
            return 
        send_file(conn, safe_path)
        print(f"    Arquivo '{filename}' enviado com sucesso.")
    except Exception as e:
        try:
            send_error(conn, f"erro interno no servidor: {e}")
        except OSError: 
            pass
        print(f"[-] Conexão com {addr} encerrada.")
    finally:
        conn.close()
        print(f"[-] Conexão com {addr} encerrada.")

def main():
    if len(sys.argv) < 3:
        print(f"Uso: python3 {sys.argv[0]} <endereco-ip> <porta> [pasta-de-arquivos]")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2])
    base_dir = sys.argv[3]
    base_dir = os.path.abspath(base_dir)

    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)
        print(f"Pasta '{base_dir}' criada.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))
    server_socket.listen(5)

    print(f"Servidor escutando em {ip}:{port}")
    print(f"Servindo arquivos da pasta: {base_dir}")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            conn, addr = server_socket.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr, base_dir), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nEncerrando servidor.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()