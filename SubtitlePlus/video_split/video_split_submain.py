"""This file is the submain function for this repository and it will call all the sub function."""
from video_split.getTime import *
from video_split.videosplit import *
from video_split.textsplit import *
def submain(subtitle_name, video_name):
    """This function acts like a main function for all sub function."""
    output_subtitle = "./serverfile/middle_file/subtitle_only.txt"  # output data which only contains subtitles
    output_time = "./serverfile/middle_file/time_only.txt"  # output data which only contains the time range
    subtitle_extract(subtitle_name, output_subtitle, output_time)
    output_total_time_in_sec = "./serverfile/middle_file/time_in_sec.txt"  # output time range in second and pass into time_slot function as input
    get_time_srt(output_time, output_total_time_in_sec)
    time_slot = clip_time(output_total_time_in_sec)
    video_split(time_slot, video_name)
    output_srt_subtitle_only = "./serverfile/output_file/srt_subtitle_only.txt"
    output_subtitle_txt(output_subtitle)