import socket
import threading

def extractHostPortFromRequest(request):
    hostStringStart = request.find(b"Host: ") + len(b"Host: ")
    hostStringEnd = request.find(b"\r\n", hostStringStart)
    hostString = request[hostStringStart : hostStringEnd].decode("utf-8")

    portPos = hostString.find(":")
    port = 80
    host = hostString

    if portPos != -1:
        try:
            port = int(hostString[portPos + 1:])
            host = hostString[:portPos]
        except ValueError:
            pass

    return host, port

def handleClientRequest(clientSocket):
    try:
        request = b""
        clientSocket.settimeout(1)
        while True:
            try:
                data = clientSocket.recv(4096)
                if not data:
                    break
                request += data
            except socket.timeout:
                break
            except Exception:
                break
        
        if not request:
            return

        host, port = extractHostPortFromRequest(request)
        
        destinationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destinationSocket.connect((host, port))

        destinationSocket.sendall(request)

        while True:
            responseData = destinationSocket.recv(4096)
            if len(responseData) > 0:
                clientSocket.sendall(responseData)
            else:
                break

    except Exception as e:
        print(f"Error handling client request: {e}")
    finally:
        if 'destinationSocket' in locals():
            destinationSocket.close()
        clientSocket.close()

def startProxyServer():
    proxyPort = 8888
    proxyHost = "127.0.0.1"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((proxyHost, proxyPort))
    server.listen(10)

    print(f"Python Proxy Server listening on {proxyHost}:{proxyPort}...")

    while True:
        clientSocket, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        clientHandler = threading.Thread(target=handleClientRequest, args=(clientSocket,))
        clientHandler.start()

if __name__ == "__main__":
    startProxyServer()
