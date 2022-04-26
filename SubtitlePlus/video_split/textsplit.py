"""This file will split the text from a srt file. It first will extract the text and time and separate and write it to different file."""
import os
import re
def subtitle_extract(subtitle_name, output_subtitle, output_time):
    with open(subtitle_name, "r") as subtitle_file:
        line = subtitle_file.readlines()
        subtitle_list = [line[i: i + 4] for i in range(0, len(line), 4)]
        subtitle_dict = {}
        numberlist = []
        for i in subtitle_list:
            number = i[0].strip('\n')
            numberlist.append(number)
            subtitle_dict[number] = i[2].strip('\n')
            subtitle_dict[f"{number}time"] = i[1].strip('\n')
    textfile = open(output_subtitle, "w+")
    timefile = open(output_time, "w+")
    for i in numberlist:
        for key, value in subtitle_dict.items():
            if(key == i):
                textfile.write(value)
                textfile.write("\n")
            elif(key == f"{i}time"):
                pattern = re.compile(r'(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)')
                searching = pattern.search(value)
                start_hour = float(searching.group(1))
                start_minute = float(searching.group(2))
                start_second = float(searching.group(3))
                start_milisecond = float(searching.group(4))
                end_hour = float(searching.group(5))
                end_minute = float(searching.group(6))
                end_second = float(searching.group(7))
                end_milisecond = float(searching.group(8))
                start_time_hour2sec = start_hour * 60 * 60
                start_time_min2sec = start_minute * 60
                start_time_mili2sec = start_milisecond / 1000
                start_total_second = str(start_time_hour2sec + start_time_min2sec + start_time_mili2sec + start_second)
                end_time_hour2sec = end_hour * 60 * 60
                end_time_min2sec = end_minute * 60
                end_time_mili2sec = end_milisecond / 1000
                end_total_second = str(end_time_hour2sec + end_time_min2sec + end_time_mili2sec + end_second)
                output = start_total_second + "-" + end_total_second
                timefile.write(output)
                timefile.write("\n")
    textfile.close()
    timefile.close()
def output_subtitle_txt(text_file): #output subtitle text

    with open(text_file, "r") as text_file:
        key = 0
        for line in text_file:
            key += 1
            target = "./serverfile/output/" + str(key) + "subtitle_only_output.txt"
            final_output = open(target, "w+")
            final_output.write(line)
    #final_output.close()
    text_file.close()





