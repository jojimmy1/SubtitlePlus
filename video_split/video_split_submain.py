from videosplit import *
from textsplit import *
from getlrc import *
from getsbv import *
def submain(subtitle_name, video_name):
    output_subtitle = "./middle_file/subtitle_only.txt"  # output data which only contains subtitles
    output_time_in_sec = "./middle_file/time_only.txt"  # output data which only contains the time range
    getfile_format = input("Enter your file format: ")
    if(getfile_format == "srt"):
        subtitle_extract(subtitle_name, output_subtitle, output_time_in_sec)
    elif(getfile_format == "lrc"):
        lrc_extract("./input/example.txt", output_subtitle, output_time_in_sec)
    elif(getfile_format == "sbv"):
        sbv_extract("./input/examplesbv.txt", output_subtitle, output_time_in_sec)
    time_slot = clip_time(output_time_in_sec)
    video_split(time_slot, video_name)
    output_subtitle_txt(output_subtitle) #output subtitle text