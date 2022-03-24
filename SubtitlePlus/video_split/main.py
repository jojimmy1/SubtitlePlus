"""Main function for this repository"""
from video_split.video_split_submain import *
if __name__ == '__main__':
    """The main function is for video split and takes in 2 input which is a srt file and a mp4 file and acts like a black box"""
    subtitle_name = "./input/subtitle.txt" #input data which is the srt text file
    video_name = "./input/Iamalive.mp4" #input data which should be a mp4 file
    submain(subtitle_name, video_name)


