from getTime import *
from videosplit import *
from textsplit import *
def submain(subtitle_name, video_name):
    output_subtitle = "./middle_file/subtitle_only.txt"  # output data which only contains subtitles
    output_time = "./middle_file/time_only.txt"  # output data which only contains the time range
    subtitle_extract(subtitle_name, output_subtitle, output_time)
    output_total_time_in_sec = "./middle_file/time_in_sec.txt"  # output time range in second and pass into time_slot function as input
    get_time_srt(output_time, output_total_time_in_sec)
    time_slot = clip_time(output_total_time_in_sec)
    video_split(time_slot, video_name)
    output_subtitle_txt(output_subtitle) #output subtitle text