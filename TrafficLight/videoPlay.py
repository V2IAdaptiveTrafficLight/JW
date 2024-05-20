# 영상 Load 하는 파일
import _threading_local
import cv2
import tkinter as tk
from tkinter import filedialog

class VideoPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("동영상 재생")
        
        # 파일 경로, 신호등 시간
        self.file_path = None
        self.traffic_light_time = None

        # 파일 경로 입력 라벨과 버튼 생성
        self.label_path = tk.Label(self.root, text="파일 경로:")
        self.label_path.pack()

        self.entry_path = tk.Entry(self.root, width=50)
        self.entry_path.pack()

        self.browse_button = tk.Button(self.root, text="경로 찾기", command=self.browse_file)
        self.browse_button.pack()

        # 시간 입력 라벨과 입력 창 생성
        self.label_duration = tk.Label(self.root, text="신호등 시간(초)")
        self.label_duration.pack()

        self.entry_duration = tk.Entry(self.root, width=10)
        self.entry_duration.pack()

        # 재생 버튼 생성
        self.play_button = tk.Button(self.root, text="확인", command=self.play_video)
        self.play_button.pack()

    def browse_file(self):
        self.file_path = filedialog.askopenfilename()
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(0, self.file_path)

    def play_video(self):
        file_path = self.get_file_path()
        duration = self.get_traffic_time()  # 입력된 재생 시간 가져오기
        
        # 나중에 지울 코드
        print("File path:", file_path)
        print("Play duration (seconds):", duration)

    def get_file_path(self):
        return self.file_path

    def get_traffic_time(self):
        self.traffic_light_time = int(self.entry_duration.get())
        return self.traffic_light_time
    
    def get_time(self):
        return self.traffic_light_time
    
    def run(self):
        self.root.mainloop()

# if __name__ == "__main__":
#     player = VideoPlayer()
#     player.run()
