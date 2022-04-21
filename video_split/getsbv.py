import re
def sbv_extract(subtitle_name, output_subtitle, output_time):
    textfile = open(output_subtitle, "w+")
    timefile = open(output_time, "w+")
    with open(subtitle_name, "r")as sbvfile:
        while line := sbvfile.readline():
            pattern_time = re.compile(r'(\d*):(\d*):(\d*.\d*),(\d*):(\d*):(\d*.\d*)')
            pattern_script = re.compile(r'(.+)')
            time_search = pattern_time.search(line)
            print(time_search)
            script_search = pattern_script.search(line)
            if(time_search != None):
                start_hour = float(time_search.group(1))
                start_minute = float(time_search.group(2))
                start_second = float(time_search.group(3))
                end_hour = float(time_search.group(4))
                end_minute = float(time_search.group(5))
                end_second = float(time_search.group(6))
                start_time = start_hour + start_minute + start_second
                end_time = end_hour + end_minute + end_second
                time_range = str(start_time)+'-'+str(end_time)
                timefile.write(time_range)
                timefile.write("\n")

            elif(script_search != None):
                textfile.write(script_search.group(1))
                textfile.write("\n")





