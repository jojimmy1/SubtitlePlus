from moviepy.editor import *
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
            pattern = re.compile(r'(\d*.\d*)-(\d*.\d*)')

            searching = pattern.search(line)
            min_digit = float(searching.group(1))
            max_digit = float(searching.group(2))
            time_slot[num_of_line] = (min_digit, max_digit)
            num_of_line += 1
    return time_slot
def video_split(time_slot, video_name):
    for i, j in time_slot.items():
        min_val = j[0]
        max_val = j[1]
        key = str(i)
        target = key + "test.mp4"
        #ffmpeg_extract_subclip("Iamalive.mp4", min_val, max_val, targetname=target)
        input_video_path = video_name
        output_video_path = target
        with VideoFileClip(input_video_path) as video:
            new = video.subclip(min_val, max_val)
            new.write_videofile(output_video_path, codec = "libx264")
    key = int(key)
    mp4_2_mp3(key)
def mp4_2_mp3(key):
    for i in range (1, key + 1):
        target = str(i) + "test.mp4"
        video = AudioFileClip(target)
        video.write_audiofile(str(i) + "test.mp3")
        video.close()













