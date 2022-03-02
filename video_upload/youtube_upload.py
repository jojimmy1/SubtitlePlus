import os

def youtube_upload(file_path, title="Test Title", description="Video description", category="22", keywords="", privacyStatus="public" ):
    command = 'python3 upload_video.py --file="%s" --title="%s" --description="%s" --category="%s" --keywords="%s" --privacyStatus="%s"' % (file_path, title, description, category, keywords, privacyStatus)
    os.system(command) 
    #print(command)
    

# example function call:
# youtube_upload(file_path="/Users/justinchen/Desktop/helloworld.mov")