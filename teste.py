import os
dir = "D:\\MEGA\\__IST"
for file in os.listdir(dir):
    if os.path.isfile(file):
        print(file)