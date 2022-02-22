def subtitle_extract():
    with open("subtitle.txt", "r") as subtitle_file:
        line = subtitle_file.readlines()
        subtitle_list = [line[i: i + 4] for i in range(0, len(line), 4)]
        subtitle_dict = {}
        numberlist = []
        for i in subtitle_list:
            number = i[0].strip('\n')
            numberlist.append(number)
            subtitle_dict[number] = i[2].strip('\n')
            subtitle_dict[f"{number}time"] = i[1].strip('\n')
    textfile = open("subtitle_text.txt", "w+")
    timefile = open("time_text.txt", "w+")
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


