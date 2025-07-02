import socket
import os
import time
import subprocess


# sudo apt install network-manager need
def connect_wifi(ssid, password):
    try:
        subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password])
        return True
    except :
        return False

ssid = "station-pi5"
password = "dronefield!"

#connect_wifi(ssid, password)

# 보낼 파일 읽기
def send_file(file, size):

    target_file = open(file, "rb") # 파일을 바이너리로 읽고,쓰기

    # 1024만큼씩 보내기
    remain = size

    while remain > 0:
        #data = target_file.read(min(1024, remain))
        data = target_file.read(1024)
        client_socket.sendall(data)
        remain -= len(data)

    # 버퍼 비우기
    #client_socket.sendall(b"ENDASD")
    print(f"{target_file} : send complete")
    target_file.close()

    time.sleep(1)
    return


fly_log_path = os.getcwd() + "/fly_log/"
img_path = os.getcwd() + "/img/"

# 현재 드론이 가지고 있는 파일목록들
fly_log_files = os.listdir(fly_log_path)
img_files = os.listdir(img_path)
# server_fly_log_files = []
# server_img_files = []

# 서버 설정
server_address = "192.168.32.1"  # 서버의 실제 IP 주소 또는 도메인 이름
server_port = 12345         # 서버 포트 번호

# 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # AF는 주소체계
client_socket.connect((server_address, server_port))

for fly_log_file in fly_log_files:

    # 파일 정보 보내기
    file_name = fly_log_file
    file_size = os.path.getsize(fly_log_path + fly_log_file)
    client_socket.send(f"{file_name},{file_size}".encode())

    # 서버에 파일이 존재하면 다음 파일로 넘어가기
    isAlreadyExist = client_socket.recv(1).decode()
    if isAlreadyExist == 'T':
        continue

    # 받아야할 파일이면 send_file 함수를 실행
    if isAlreadyExist == 'F':
        send_file(fly_log_path + file_name, file_size)

for img in img_files:

    # 파일 정보 보내기
    file_name = img
    file_size = os.path.getsize(img_path + img)
    client_socket.send(f"{file_name},{file_size}".encode())

    # 서버에 파일이 존재하면 다음 파일로 넘어가기
    isAlreadyExist = client_socket.recv(1).decode()
    if isAlreadyExist == 'T':
        continue

    # 받아야할 파일이면 send_file 함수를 실행
    if isAlreadyExist == 'F':
        send_file(img_path + file_name, file_size)

# 필요한 파일을 모두 보냄을 알림
client_socket.sendall("END".encode())

client_socket.close()
