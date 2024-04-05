from bluepy.btle import Scanner, DefaultDelegate
import subprocess

class BeaconDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.found_beacon = False

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if not self.found_beacon:
            for (adtype, desc, value) in dev.getScanData():
                if value.startswith("aafe"):
                    # 'aafe'로 시작하는 경우, 맨 앞에서부터 8글자를 삭제 - URL 문자열 부분
                    hex_value = value[8:]
                
                    # 2f(/)를 기준으로 SSID와 패스워드 분리
                    ssid_hex, password_hex = hex_value.split("2f")
                    
                    # 16진수를 ASCII문자열로 변환하여 SSID와 패스워드 추출
                    ssid = ''.join([chr(int(ssid_hex[i:i+2], 16)) for i in range(0, len(ssid_hex), 2)])
                    password = ''.join([chr(int(password_hex[i:i+2], 16)) for i in range(0, len(password_hex), 2)])
                    
                    # 문자열 내 공백 제거
                    ssid = ssid.replace(" ", "")
                    password = password.replace(" ", "")
                    
                    # Wi-Fi에 연결 시도
                    connect_to_wifi(ssid, password)
                    self.found_beacon = True
                    break

def connect_to_wifi(ssid, password):
    # nmcli 명령을 사용하여 Wi-Fi에 연결
    command = f"nmcli device wifi connect '{ssid}' password '{password}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # 명령 실행 결과 확인
    if result.returncode == 0:
        print(f"Wi-Fi에 {ssid}에 성공적으로 연결되었습니다!")
        return True
    else:
        print(f"{ssid}에 연결하는 데 실패했습니다.")
        print("오류:", result.stderr)
        return False

if __name__ == "__main__":
    scanner = Scanner().withDelegate(BeaconDelegate())
    scanner.start()
    scanner.process(timeout=3)  # 3초 동안 스캔
    scanner.stop()
