from getTime import *
from videosplit import *
from textsplit import *
if __name__ == '__main__':
    subtitle_dict = subtitle_extract()
    video_name = "Iamalive.mp4"
    get_time_srt()
    time_slot = clip_time()
    video_split(time_slot, video_name)

