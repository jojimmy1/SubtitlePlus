
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import re
def clip_time():
    time_slot = {}
    num_of_line = 1
    with open("time.txt", 'r') as time_file:
        while True:
            line = time_file.readline()
            if not line:
                break
            line = line.strip("\n")
            pattern = re.compile(r'(\d*)-(\d*)')

            searching = pattern.search(line)
            min_digit = float(searching.group(1))
            max_digit = float(searching.group(2))
            time_slot[num_of_line] = (min_digit, max_digit)
            num_of_line += 1
    return time_slot
def video_split(time_slot):
    for i, j in time_slot.items():
        min_val = j[0]
        max_val = j[1]
        print(min_val)
        print(max_val)
        key = str(i)
        target = key + "test.mp4"
        ffmpeg_extract_subclip("Iamalive.mp4", min_val, max_val, targetname=target)









