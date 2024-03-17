from flask import Flask, request, jsonify,render_template
from videoCaption import getCaption,split_video_into_scenes
app = Flask(__name__)
import os
@app.route('/')
def index():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['video_file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    video_save_path = os.path.join(r'./uploads',file.filename[:-4])
    video_save_name =  os.path.join(video_save_path,file.filename)
    if not os.path.exists(video_save_path):
        os.makedirs(video_save_path)
        print("Folder created")
        file.save(video_save_name)
        print("saved video")
    else:
        print("Folder already exists")
        file.save(os.path.join(video_save_name))
        print("saved video")
    split_video_list = split_video_into_scenes(video_save_name,video_save_path)
    if len(split_video_list)==0:
        caption = getCaption(video_save_name  )
    else:
        caption = ""
        for index, cut_time in enumerate(split_video_list):
            print(cut_time)
            video_cut_save_name = video_save_name[:-4] + "-Scene-"+"0"*(3-len(str(index+1)))+str(index+1) + ".mp4"
            try : # maybe to short
                caption += "<br>"+str(cut_time[0])+" "+getCaption(video_cut_save_name  )
            except Exception as e:
                print(e)
        
    return jsonify({'message': caption,'fileName':file.filename}), 200

if __name__ == '__main__':
    app.run(host = "0.0.0",port=5001,debug=True)
