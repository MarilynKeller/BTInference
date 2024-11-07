import argparse
import os

import cv2

def make_video(render_folder, output_file, frame_rate, img_string='frame_%04d.png', bg='video', bg_video_path=None):
    # Get the resolution of the images
    im0 = os.path.join(render_folder, img_string % 0)
    im = cv2.imread(im0)
    h, w, _ = im.shape
    shape_str = f'{w}x{h}'

    if bg == 'white':
        # White background overlay command
        cmd = f'ffmpeg -f lavfi -i color=c=white:s={shape_str} -y -framerate {frame_rate} -i {render_folder}/{img_string} -filter_complex "[0:v][1:v]overlay=shortest=1,format=yuv420p[out]" -map "[out]" {output_file}'
    elif bg == 'video':
        # Video background overlay command
        cmd = f'ffmpeg -stream_loop -1 -i {bg_video_path} -y -framerate {frame_rate} -i {render_folder}/{img_string} ' \
          f'-filter_complex "[0:v]scale={w}:{h}[bg];[bg][1:v]overlay=shortest=1,format=yuv420p[out]" ' \
          f'-map "[out]" {output_file}'    
    else:
        # Standard command without background
        cmd = f'ffmpeg -i {render_folder}/{img_string} -y -c:v libx264 -vf "fps={frame_rate}" -pix_fmt yuv420p {output_file}'

    print(cmd)
    os.system(cmd)
    print(f"Video saved to {output_file}.")

def cat_video(file_list):
    # Check if file_list has at least two videos
    if len(file_list) < 2:
        raise ValueError("Need at least two videos to concatenate")

    # Get the directory of the first video in the list
    output_dir = os.path.dirname(file_list[0])
    output_path = os.path.join(output_dir, "concatenated.mp4")
    
    # Prepare ffmpeg input arguments
    ffmpeg_inputs = []
    for file in file_list:
        ffmpeg_inputs.extend(["-i", file])

    # Construct the filter_complex argument
    filter_complex = f"hstack=inputs={len(file_list)}"
    
    # Build and run the ffmpeg command
    cmd = ["ffmpeg", *ffmpeg_inputs, "-filter_complex", filter_complex, output_path]
    os.system(cmd)
    print(f"Concatenated video saved to {output_path}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Render all the videos')
    
    parser.add_argument('--exp_name', type=str, help='Name of the experiment', default='P8_69_outdoor_cartwheel')
    parser.add_argument('--fps', type=int, help='Fps of the sequence', default=30)
    parser.add_argument('--folders', type=str, help='List of the folders to make a video from. If not specified, all the folders will be used', nargs='+')
    
    args = parser.parse_args()
    
    render_folder = os.path.join('output', args.exp_name, 'Render')
    video_folder = os.path.join('output', args.exp_name, 'Videos')
    os.makedirs(video_folder, exist_ok=True)
    
    bg_video_path =  os.path.join('output', args.exp_name, 'video.mp4')
    
    # List all the subfolders of the render folder
    if args.folders is not None:
        im_folders = args.folders
    else:
        im_folders = [f for f in os.listdir(render_folder) if os.path.isdir(os.path.join(render_folder, f))]
    
    # for bg in ['white', 'video']:
    # for bg in ['white']:
    # for bg in ['black']:
    for bg in ['video', 'white']:
        os.makedirs(os.path.join(video_folder, bg+'_bg'), exist_ok=True)
        for folder in im_folders:
            # if folder != 'smpl':
            #     continue
            # If the folder has less than 10 images, skip it
            files = os.listdir(os.path.join(render_folder, folder))
            if len(files) < 10:
                continue
            try: 
                make_video(os.path.join(render_folder, folder), os.path.join(video_folder, bg+'_bg', f'{folder}.mp4'), 
                           args.fps, bg=bg, bg_video_path=bg_video_path)
            except Exception as e:
                print(f"Error rendering video for folder {folder}. {e}")
                
    if args.cat:
        print("Concatenating videos from left to right")
        # list all the videos in the folder 'video' background
        bg_mode = 'video'
        videos = []
        for video_name in ['smpl', 'osso', 'skel_skel', 'lt']:
            videos.append(os.path.join(video_folder, 'white_bg', f'{video_name}.mp4'))
        cat_video(videos)
                
