import selectors
import socket
import time
import traceback

from client_message import ClientMessage

HOST = '127.0.0.1'
PORT = 65432

uuids = []


def main():
    """
    Simulation of a client connecting to the server
    """
    item = {'action': 'register', 'ip': '127.0.0.1', 'port': 65433, 'type': 'hive'}
    print(f'registering service: {item["type"]} {item["ip"]} {item["port"]}')
    send_request(item)

    item = {'action': 'register', 'ip': '192.168.99.99', 'port': 65438, 'type': 'world'}
    print(f'registering service: {item["type"]} {item["ip"]} {item["port"]}')
    send_request(item)

    item = {'action': 'heartbeat', 'uuid': uuids[1]}
    print(f'heartbeat for service: {uuids[1]}')
    send_request(item)
    time.sleep(1)

    item = {'action': 'register', 'ip': '127.0.0.1', 'port': 66554, 'type': 'hive'}
    print(f'registering service: {item["type"]} {item["ip"]} {item["port"]}')
    send_request(item)

    item = {'action': 'query', 'type': 'hive'}
    print(f'query for services: {item["type"]}')
    send_request(item)
    time.sleep(3)

    item = {'action': 'query', 'type': 'hive'}
    print(f'query for services: {item["type"]}')
    send_request(item)
    time.sleep(1)


def send_request(action):
    """
    sends a request to the server
    :param action:
    :return:
    """
    sel = selectors.DefaultSelector()
    request = create_request(action)
    start_connection(sel, HOST, PORT, request)

    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f'Main: Error: Exception for {message.ipaddr}:\n'
                        f'{traceback.format_exc()}'
                    )
                    message._close()
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print('Caught keyboard interrupt, exiting')
    finally:
        sel.close()
    process_response(action, message)


def process_response(action, message):
    """
    process the response from the server
    :param action:
    :param message:
    :return:
    """
    if action['action'] == 'register':
        uuids.append(message.response.decode('utf-8'))


def create_request(action_item):
    return dict(
        type='text/json',
        encoding='utf-8',
        content=action_item,
    )


def start_connection(sel, host, port, request):
    addr = (host, port)
    print(f'Starting connection to {addr}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = ClientMessage(sel, sock, addr, request)
    sel.register(sock, events, data=message)


if __name__ == '__main__':
    main()
