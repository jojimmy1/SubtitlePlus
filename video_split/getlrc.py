import re
def lrc_extract(subtitle_name, output_subtitle, output_time):
    textfile = open(output_subtitle, "w+")
    timefile = open(output_time, "w+")
    with open(subtitle_name, "r")as lrcfile:
        lrc_sec_list = []
        lrc_subtitle = []
        i = 0;
        while line := lrcfile.readline():
            if i == 0:
                pattern = re.compile(r'length:(\d*):(\d*.\d*)')
                searching = pattern.search(line)
                minute = float(searching.group(1))
                second = float(searching.group(2))
                total_sec = minute * 60.0 + second
            elif i == 1:
                pattern = re.compile(r're:(.*)')
                searching = pattern.search(line)
                website = searching.group((1))
            elif i == 2:
                pattern = re.compile(r've:(.*)')
                searching = pattern.search(line)
                version = searching.group((1))
            else:
                pattern = re.compile(r'\[(\d*):(\d*.\d*)\](.*)')
                searching = pattern.search(line)
                minute = float(searching.group(1))
                second = float(searching.group(2))
                lrc_sec_list.append(str(minute * 60.0 + second))
                lrc_subtitle.append(searching.group(3))
            i = i + 1
        for i in range(len(lrc_sec_list)):
            if 0 <= (i + 1) < len(lrc_sec_list):
                start_time = str(lrc_sec_list[i])
                end_time = str(lrc_sec_list[i + 1])
            else:
                start_time = str(lrc_sec_list[i])
                end_time = str(total_sec)
            output = start_time + "-" + end_time
            timefile.write(output)
            timefile.write("\n")
        for i in lrc_subtitle:
            textfile.write(i)
            textfile.write("\n")
