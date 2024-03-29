import av
import numpy as np
import torch
from transformers import AutoImageProcessor, AutoTokenizer, VisionEncoderDecoderModel


from scenedetect import open_video, SceneManager, split_video_ffmpeg
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg


from moviepy.editor import VideoFileClip, concatenate_videoclips




device = "cuda" if torch.cuda.is_available() else "cpu"
# load pretrained processor, tokenizer, and model
image_processor = AutoImageProcessor.from_pretrained("MCG-NJU/videomae-base",cache_dir="./model")
tokenizer = AutoTokenizer.from_pretrained("gpt2",cache_dir="./model")
model = VisionEncoderDecoderModel.from_pretrained("Neleac/timesformer-gpt2-video-captioning",cache_dir="./model").to(device)


def split_video_into_scenes(video_path,output_dir="./",threshold=27.0):
    # Open our video, create a scene manager, and add a detector.
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(
        ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video, show_progress=True)
    scene_list = scene_manager.get_scene_list()
    split_video_ffmpeg(video_path, scene_list,output_dir=output_dir, show_progress=True)
    return scene_list

def getCaption(video_path):
    # load video
    # video_path = "./1658_circle.mp4"
    container = av.open(video_path)

    # extract evenly spaced frames from video
    seg_len = container.streams.video[0].frames
    clip_len = model.config.encoder.num_frames
    indices = set(np.linspace(0, seg_len, num=clip_len, endpoint=False).astype(np.int64))
    frames = []
    container.seek(0)
    for i, frame in enumerate(container.decode(video=0)):
        if i in indices:
            frames.append(frame.to_ndarray(format="rgb24"))

    # generate caption
    gen_kwargs = {
        "min_length": 10, 
        "max_length": 20, 
        "num_beams": 8,
    }
    pixel_values = image_processor(frames, return_tensors="pt").pixel_values.to(device)
    tokens = model.generate(pixel_values, **gen_kwargs)
    caption = tokenizer.batch_decode(tokens, skip_special_tokens=True)[0]
    print(caption) # A man and a woman are dancing on a stage in front of a mirror.
    return caption


# 定义要合并的视频文件路径
def concatenate_video(video_path_list):
    video_list = list(map(lambda x:VideoFileClip(x),video_path_list))

    # 如果两个视频尺寸不同，可以通过调整大小使它们具有相同的尺寸
    # 这里使用video1的尺寸作为标准，将video2调整为相同尺寸
    for index,video in enumerate(video_list) :
        video_list[index] = video_list[index].resize(video_list[0].size)

    # 将调整后的视频添加到视频列表中
    videos = video_list

    # 合并视频
    final_video = concatenate_videoclips(videos)

    # 保存合并后的视频
    final_video.write_videofile('./video.mp4', codec='libx264')

    # 输出合并成功信息
    print("视频合并完成！")

if __name__ =="__main__" :
    split_video_into_scenes("./SVID_20240317_044051_1.mp4")
