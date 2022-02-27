
import os
os.system("ffmpeg -i 1test.mp4 -vf subtitles=1test.srt out.mp4") 

#import ffmpeg
#import sys
#sys.path.append(r'/Users/justinchen/Downloads') # your ffmpeg file path
#stream = ffmpeg.input('1test.mp4') # video location

#stream = stream.trim(start = 10, duration=15).filter('setpts', 'PTS-STARTPTS')
#stream = stream.filter('fps', fps=5, round='up').filter('scale', w=128, h=128)

#stream = ffmpeg.output(stream, 'output.mp4')

#ffmpeg.run(stream)

#stream_2 = ffmpeg.input('helloworld.mov')

#audio = stream.audio

#stream_2 = ffmpeg.drawtext(stream_2,text='helloworld',x=100,y=100,fontsize=50)
#stream = ffmpeg.output(ffmpeg.concat(stream_2, audio, v=1, a=1),'output.mp4')

#ffmpeg.run(stream)