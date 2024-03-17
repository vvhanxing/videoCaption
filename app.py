from flask import Flask, request, jsonify,render_template
from videoCaption import getCaption
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
        return jsonify({'error': 'No selected file'}), 400


    # For demonstration purposes, we'll just return a success message
    
    file.save(os.path.join(r'./uploads',file.filename))
    caption = getCaption(os.path.join(r'./uploads',file.filename)  )

    return jsonify({'message': caption,'fileName':file.filename}), 200

if __name__ == '__main__':
    app.run(host = "192.168.43.220",debug=True)
