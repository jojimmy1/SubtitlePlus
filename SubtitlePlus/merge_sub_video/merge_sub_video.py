""" Merge video and Subtitle Module"""
import ffmpeg

def merge_video_subtitle(video_filename, subtitle_filename, output_filename):
    """ this function merge video and subtitle
     , input filenames and output filename """
    video = ffmpeg.input(video_filename)
    audio = video.audio
    ffmpeg.concat(video.filter("subtitles", subtitle_filename), audio, v=1, a=1).output(output_filename).run()


'''
video = ffmpeg.input('1test.mp4')
audio = video.audio
ffmpeg.concat(video.filter("subtitles", "1test.srt"), audio, v=1, a=1).output('output_32.mp4').run()




audio = stream.audio
stream = stream.filter("subtitles", "1test.srt")
stream = ffmpeg.output(ffmpeg.concat(stream, audio, v=1, a=1),'output.mp4')
stream = ffmpeg.output(stream, 'output.mp4')

ffmpeg.run(stream)
'''
#import sys
#sys.path.append(r'/Users/justinchen/Downloads') # your ffmpeg file path
#stream = ffmpeg.input('1test.mp4') # video location
#stream = stream.trim(start = 10, duration=15).filter('setpts', 'PTS-STARTPTS')
#stream = stream.filter('fps', fps=5, round='up').filter('scale', w=128, h=128)
#import os
#os.system("ffmpeg -i 1test.mp4 -vf subtitles=1test.srt out.mp4") 
#print('here')


#stream_2 = ffmpeg.input('helloworld.mov')



#stream_2 = ffmpeg.drawtext(stream_2,text='helloworld',x=100,y=100,fontsize=50)
#stream = ffmpeg.output(ffmpeg.concat(stream_2, audio, v=1, a=1),'output.mp4')

#ffmpeg.run(stream)