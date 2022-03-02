from getTime import *
from videosplit import *
from textsplit import *
if __name__ == '__main__':
    subtitle_name = "subtitle.txt" #input data which is the srt text file
    output_subtitle = "subtitle_only.txt" #output data which only contains subtitles
    output_time = "time_only.txt" #output data which only contains the time range
    subtitle_dict = subtitle_extract(subtitle_name, output_subtitle, output_time)
    video_name = "Iamalive.mp4" #input data which should be a mp4 file
    output_total_time_in_sec = "time_in_sec.txt" #output time range in second and pass into time_slot function as input
    get_time_srt(output_time, output_total_time_in_sec)
    time_slot = clip_time(output_total_time_in_sec)
    video_split(time_slot, video_name)

