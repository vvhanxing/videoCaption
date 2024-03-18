from flask import Flask, request, jsonify,render_template
from videoCaption import getCaption,split_video_into_scenes
import json
app = Flask(__name__)
# clip_info_list = [{"video file name":"",
#              "video file path":"",
#              "video clips":[ {  "clip file name":"", 
#                                 "video clip caption":"content" , 
#                                 "video clip path":"content",
#                                 "time span":[]
#                                } 
#                                ]}]
clip_info_list = []

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

    clip_info_dict = {"video file name":file.filename,"video file path":video_save_name}#
    clip_info_dict["video clips"]  = []#
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
    caption_all = ""
    if len(split_video_list)==0:
        caption_all = getCaption(video_save_name  )
        clip_info_dict["video clips"] = [{"clip file name":file.filename, 
                                          "video clip caption":caption_all,
                                          "video clip path":video_save_name,
                                          "time span": ["00:00:00.000","Full original video"]}]#
     
    else:
        
        for index, cut_time in enumerate(split_video_list):
            print(cut_time)
            video_cut_save_name = video_save_name[:-4] + "-Scene-"+"0"*(3-len(str(index+1)))+str(index+1) + ".mp4"

            try : # maybe to short
                caption = getCaption(video_cut_save_name  )
                caption_all += "<br>"+str(cut_time[0])+" "+caption
                clip_info_dict["video clips"] .append({"clip file name":file.filename[:-4]+"-Scene-"+"0"*(3-len(str(index+1)))+str(index+1) + ".mp4", 
                                                  "video clip caption":caption,
                                                  "video clip path":os.path.join(video_save_path,file.filename[:-4]+"-Scene-"+"0"*(3-len(str(index+1)))+str(index+1) + ".mp4"),
                                                  "time span":[cut_time[0].get_timecode(),cut_time[1].get_timecode()]
                                                  })
               
            except Exception as e:
                print(e)
    clip_info_list.append(clip_info_dict)
    with open("clip_info_list.json","w") as f:
        json.dump(clip_info_list,f)
    clip_info_dict['message'] = caption_all
    return jsonify(clip_info_dict), 200

if __name__ == '__main__':
    app.run(host = "192.168.43.220",debug=True)
