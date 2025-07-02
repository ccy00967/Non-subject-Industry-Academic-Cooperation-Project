import socket
import os

# 해당 파일을 서비스로 실행
# /etc/systemd/system/station_server_py.service 추가 후 편집

# 저장할 파일 생성 및 열기
def recive_file(file, size):
    target_file = open(file, "wb") # 파일을 바이너리로 읽고,쓰기

    # 1024만큼씩 입력받기
    remain = size

    while remain > 0:
        data = client_socket.recv(min(1024, remain))
        target_file.write(data)
        remain -= len(data)

    target_file.close()
    return


fly_log_path = os.getcwd() + "/fly_log/"
img_path = os.getcwd() + "/img/"    


# 서버는 라즈베리파이를 ap 모드로 설정함
# 라즈베리파이 주소 192.168.32.1 고정
# 접속하는 클라이언트들은 192.168.32.2 - 192.168.32.10 사이의 주소를 할당받는다
#host = "192.168.32.1"  # 서버의 IP 주소 또는 도메인 이름
host = "0.0.0.0"
port = 12345       # 포트 번호

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # AF는 주소체계
server_socket.bind((host, port))    # 소켓과 AF 연결
server_socket.listen(2)     # 동시접속수

print(f"server start: {host}:{port}")

while True:
    print("connection waiting")
    # 클라이언트 연결 대기
    client_socket, client_address = server_socket.accept()
    print(f"client connected: {client_address}")

    fly_log_files = os.listdir(fly_log_path)
    img_files = os.listdir(img_path)

    print("fly log file list: ")
    print(fly_log_files)
    print("image file list: ")
    print(img_files)
    
    while True:

        # 파일 정보 받기
        try:
            file_info = client_socket.recv(1024).decode()

            # 필요한 파일 전부 받음
            if file_info == "END":
                break
            
            file_name, file_size = file_info.split(',')
            file_size = int(file_size)

            # 만약 이미 존재하는 파일이라면 송수신 생략
            if (file_name in fly_log_files) or (file_name in img_files):
                client_socket.send("T".encode())    # 파일이 존재함을 알림: T
                print(f"{file_name}: already exist")
                continue

            client_socket.send("F".encode())    # 파일이 존재하지 않음을 알림: F

            # 비행로그 파일일 경우
            if (file_name.endswith(".ulg")):
                recive_file(fly_log_path + file_name, file_size)

            # 이미지 파일일 경우
            if (file_name.endswith(".png")):    
                recive_file(img_path + file_name, file_size)
        except:
            break

    # # 버퍼 비우기
    # while True:
    #     try:
    #         data = client_socket.recv(1024)
    #         if not data:
    #             break
    #         print(f"버퍼비우기: {data}")
    #     except:
    #         continue

    client_socket.close()
    
