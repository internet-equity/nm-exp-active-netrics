"""functions for piping a video stream"""

from subprocess import Popen
import psutil
import time
import toml
import sys

class PipeVideo():
    def __init__(self, config):
        """Initiates pipe video object"""
        self.config = config
        self.ffmpeg_proc = -1

    def start_pipe(self):
        """Starts the piping of video in a separate thread"""
        reset_iface_cmd = "sudo modprobe -r v4l2loopback"
        create_iface_cmd = 'sudo modprobe v4l2loopback device=1 device_nr=1 card_label="VirtCam" ' \
                           'exclusive_caps=1 max_buffers=2'
        pipe_video = f"nohup ffmpeg -stream_loop -1 -re -i {self.config['default']['video-path']} -f v4l2 " \
                     f"-pix_fmt yuv420p /dev/video0 1> /tmp/nohup.out &"
        print("Resetting interface")
        _ = Popen(reset_iface_cmd, shell=True)
        time.sleep(1)
        print("Creating interface")
        _ = Popen(create_iface_cmd, shell=True)
        time.sleep(1)
        print("Piping video", pipe_video)
        self.ffmpeg_proc = Popen(pipe_video, shell=True)
        time.sleep(1)

    def end_pipe(self):
        """ends process which is piping the video"""
        Popen(f'killall ffmpeg', shell=True)


if __name__ == "__main__":
    config_file = sys.argv[1]
    op = sys.argv[2]
    config = toml.load(config_file)
    pipe_video = PipeVideo(config)
    if len(sys.argv) > 2 and sys.argv[2] == "start":
        pipe_video.start_pipe()
    else:
        pipe_video.end_pipe()
    

