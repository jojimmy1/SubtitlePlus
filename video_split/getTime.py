import re
def get_time_srt():

  file_object = open("time.txt", "w+")
  with open("time_text.txt", "r") as timing:
    while True:
      line = timing.readline()
      if not line:
        break
      line = line.strip("\n")
      pattern = re.compile(r'(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)')

      searching = pattern.search(line)
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
      file_object.write(output)
      file_object.write("\n")


