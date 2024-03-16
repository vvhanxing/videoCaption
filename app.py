from flask import Flask, request, jsonify
from videoCaption import caption
app = Flask(__name__)
import os
@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Video Upload Preview</title>
  <style>
    video {
      border: 1px solid black;
      display: block;
    }
  </style>
</head>
<body>
  <input id="file-input" type="file" accept="video/*">
  <video id="video" width="300" height="300" controls></video>
  <div id="success-message"></div>

  <script>
    const input = document.getElementById('file-input');
    const video = document.getElementById('video');
    const videoSource = document.createElement('source');
    const successMessage = document.getElementById('success-message');

    input.addEventListener('change', function () {
      const files = this.files || [];

      if (!files.length) return;

      const reader = new FileReader();

      reader.onload = function (e) {
        videoSource.setAttribute('src', e.target.result);
        video.appendChild(videoSource);
        video.load();
        video.play();
      };

      reader.readAsDataURL(files[0]);

      // Send the file to the server
      const formData = new FormData();
      formData.append('video_file', files[0]);

      fetch('/upload', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        successMessage.textContent = data.message;
      })
      .catch(error => console.error('Error:', error));
    });
  </script>
</body>
</html>
'''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['video_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # You can save the file or process it as needed here

    # For demonstration purposes, we'll just return a success message
    print(os.path.join(r'./uploads',file.filename))
    file.save(os.path.join(r'./uploads',file.filename))

       
    message = caption(os.path.join(r'./uploads',file.filename)  )
    #message = "success"


    return jsonify({'message': message}), 200

if __name__ == '__main__':
    app.run(host = "192.168.43.220",debug=True)
