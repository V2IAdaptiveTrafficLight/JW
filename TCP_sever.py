import socket
import threading
from datetime import datetime
import pickle
import time

client_sockets = []
client_sockets_lock = threading.Lock()

# 서버 호스트의 ip주소 알아옴
HOST = socket.gethostbyname(socket.gethostname())
PORT1 = 9999  # broadcast port
PORT2 = 8261  # tcp 연결을 위한 port
now = datetime.now()

def broadcast_UDP():
    while True:
        # UDP 소켓 생성
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Broadcast 메시지 전송
        message = "Host ip 전송중, 차량 검색중"
        split_address = HOST.split('.')
        split_address = split_address[:3]
        broadcast_ip_address = '.'.join(split_address)
        broadcast_ip_address += '.255'
        sock.sendto(message.encode(), (broadcast_ip_address, PORT1))
        print(message)
        time.sleep(5) # 5초마다 전송


# 클라이언트 메시지 받는 스레드
def server_message_receive(client_socket, addr):
    print(f'>> {addr[0]}({addr[1]})와 연결완료.')

    while True:
        data = client_socket.recv(1024)

        if not data or pickle.loads(data)[0] == 'quit':
            print(f'>> {addr[0]}({addr[1]})와 연결해제.')
            break

        print(f'>> {addr[0]}({addr[1]})의 message : {pickle.loads(data)} ({now.time()})')

    client_socket.close()
    client_sockets[:] = [c for c in client_sockets if c != client_socket]    


# 서버에서 메시지 입력하는 경우
def server_message_input():
    while True:
        message = input()
        send_message_to_clients(message)  # 입력된 메시지를 모든 클라이언트에게 전송


# 서버와 연결된 모든 클라이언트에게 메시지 전달
def send_message_to_clients(message):
    with client_sockets_lock:
        for client in client_sockets:
            data = pickle.dumps([message])
            client.sendall(data)


print('>> Server Start with ip :', HOST)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT2))
server_socket.listen()


def client_acceptance():
    try:
        while True:
            print('>> Wait')
            client_socket, addr = server_socket.accept()
            with client_sockets_lock:
                client_sockets.append(client_socket)
            threading.Thread(target=server_message_input).start()  # 서버 메시지 전송 (서버 -> 클라이언트)
            threading.Thread(target=server_message_receive, args=(client_socket, addr)).start()  # 클라이언트 메시지 스레드 (클라이언트 -> 서버)
            print("참가자 수 : ", len(client_sockets))
            
    finally:
        server_socket.close()
        with client_sockets_lock:
            for client_socket in client_sockets:
                client_socket.close()



threading.Thread(target=broadcast_UDP).start()  # broadcast 쓰레드
threading.Thread(target=client_acceptance).start()  # 클라이언트 연결 대기 쓰레드
