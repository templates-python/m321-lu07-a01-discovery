import sys
import socket
import selectors
import types

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server
def socket_client():
    selector = selectors.DefaultSelector()
    messages = [
        b'register hive 127.0.0.1 65433',
        b'register hive 192.168.99.99 65434',
        b'query hive'
    ]

    def start_connections(host, port, num_conns):
        server_addr = (host, port)
        for i in range(0, num_conns):
            connid = i + 1
            print(f'Starting connection {connid} to {server_addr}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.connect_ex(server_addr)
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            data = types.SimpleNamespace(
                connid=connid,
                msg_total=sum(len(m) for m in messages),
                recv_total=0,
                messages=messages.copy(),
                outb=b'',
            )
            selector.register(sock, events, data=data)

    def service_connection(key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                print(f'Received {recv_data!r} from connection {data.connid}')
                data.recv_total += len(recv_data)
            if not recv_data or data.recv_total == data.msg_total:
                print(f'Closing connection {data.connid}')
                selector.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)
            if data.outb:
                print(f'Sending {data.outb!r} to connection {data.connid}')
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} <host> <port> <num_connections>')
        sys.exit(1)

    host, port, num_conns = sys.argv[1:4]
    start_connections(host, int(port), int(num_conns))

    try:
        while True:
            events = selector.select(timeout=1)
            if events:
                for key, mask in events:
                    service_connection(key, mask)
            # Check for a socket being monitored to continue.
            if not selector.get_map():
                break
    except KeyboardInterrupt:
        print('Caught keyboard interrupt, exiting')
    finally:
        selector.close()


if __name__ == '__main__':
    socket_client()