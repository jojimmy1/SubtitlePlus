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
                timefile.write(value)
                timefile.write("\n")
    textfile.close()
    timefile.close()

