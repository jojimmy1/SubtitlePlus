from videosplit import *
from textsplit import *
from getlrc import *
from getsbv import *
def submain(subtitle_name, video_name, file_format = 0):
    output_subtitle = "./serverfile/middle_file/subtitle_only.txt"  # output data which only contains subtitles
    output_time_in_sec = "./serverfile/middle_file/time_only.txt"  # output data which only contains the time range
    if(file_format == 0):
        subtitle_extract(subtitle_name, output_subtitle, output_time_in_sec)
    elif(file_format == 1):
        lrc_extract(subtitle_name, output_subtitle, output_time_in_sec)
    elif(file_format == 2):
        sbv_extract(subtitle_name, output_subtitle, output_time_in_sec)
    time_slot = clip_time(output_time_in_sec)
    video_split(time_slot, video_name)
    output_subtitle_txt(output_subtitle) #output subtitle text