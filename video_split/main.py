"""The main function for video split"""
from video_split_submain import *
if __name__ == '__main__':
    subtitle_name = "./serverfile/input/subtitle.txt" #input data which is the srt text file
    video_name = "./serverfile/input/Iamalive.mp4" #input data which should be a mp4 file
    file_format = 2 # 0 means srt file, 1 means lrc file, 2 means sbv file
    submain(subtitle_name, video_name, file_format) #become black box



