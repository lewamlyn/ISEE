import os
from PIL import Image, ImageTk
from tkinter import *
import ffmpeg
import argparse
import pyaudio
import random
import _thread as thread
from time import sleep
from array import array
from generate import *

def generate_frame(in_filename, out_filename, time, width, height):    
    (
        ffmpeg
        .input(in_filename, ss=time)
        .filter('scale', width, height, force_original_aspect_ratio=1)
        .filter('pad', width, height, -1, -1)
        .output(out_filename, vframes=1)              
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )

def check_mp4(value):
    if not value.endswith('.mp4'):
        raise argparse.ArgumentTypeError("%s should be an .mp4 file" % value)
    return value

def random_pic(picdir):
    pics = os.listdir(picdir)
    x = random.randint(0, len(pics)-1)
    return os.path.join(picdir, pics[x])

# Ensure this is the correct path to your video folder 
viddir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'video/')
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pics/')
logdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log/')

parser = argparse.ArgumentParser(description='SlowMovie Settings')
parser.add_argument('-d', '--delay',  default = 600, 
    help="Delay between screen updates, in seconds")
parser.add_argument('-s', '--search',  default = 30, 
    help="Delay time of searching results, in seconds")
parser.add_argument('-i', '--inc',  default = 2, 
    help="Number of frames skipped between screen updates")
parser.add_argument('-r', '--random', action="store_true", help="play pictures in a random order; otherwise play videos")

args = parser.parse_args()

# audio init
clap = 0
wait = 3
flag = 0

def waitForClaps(threadName):
    global clap
    global flag
    global dis_flag
    global wait
    global currentVideo
    global currentPosition

    print ("Waiting for more claps")
    sleep(wait)
    if clap == 2:
        print('Two !!!!')
        print('展示爬取内容')
        #os.system('python3 spider.py')
        generate_dates()
        display()
    elif clap == 3:
        print('Three !!!')
        print('切换展示模式')
        args.random = not args.random
    elif clap == 4 :
        print('Four !!!')
        print('切换展示电影')
        if not args.random: 
            thisVideo = movieList.index(currentVideo)
            if thisVideo < len(movieList)-1:
                currentVideo = movieList[thisVideo+1]
            else:
                currentVideo = movieList[0]
            log = open(logdir + '%s.progress'%currentVideo)
            for line in log:
                currentPosition = float(line)
            f = open('nowPlaying', 'w')
            f.write(currentVideo)
            f.close()
        else:
            print('相片模式下无法切换展示电影')
    print ("Claping Ended")
    clap = 0
    flag = 0

def run_clap(threadName):
    global clap
    global flag
    print('run_clap')
    while True:
        data = stream.read(chunk,exception_on_overflow = False)
        as_ints = array('h', data)
        max_value = max(as_ints)
        if max_value > threshold:
            clap += 1
            print ("Clapped")
        if clap == 1 and flag == 0:
            thread.start_new_thread( waitForClaps, ("waitThread",) )
            flag = 1

# initial audio
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
threshold = 10000
max_value = 0
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS, 
                rate=RATE, 
                input=True,
                output=True,
                input_device_index=3,
                frames_per_buffer=chunk)

frameDelay = int(args.delay)
print("Frame Delay = %d seconds" %frameDelay )

searchDispaly = int(args.search)
print("Search Results Display = %d seconds" %searchDispaly )

increment = float(args.inc)
print("Increment = %f frames" %increment )

if args.random:
    print('In random pictures mode')
else:
    print ("In video mode")

# Scan through video folder until you find an .mp4 file 
currentVideo = ""
videoTry = 0 
while not (currentVideo.endswith('.mp4')):
    currentVideo = os.listdir(viddir)[videoTry]
    videoTry = videoTry + 1 

# the nowPlaying file stores the current video file 
# if it exists and has a valid video, switch to that 
try: 
    f = open('nowPlaying')
    for line in f:
        currentVideo = line.strip()
    f.close()
except: 
    f = open('nowPlaying', 'w')
    f.write(currentVideo)
    f.close()    

videoExists = 0 
for file in os.listdir(viddir):
    if file == currentVideo: 
        videoExists = 1

if videoExists > 0:  
    if not args.random:
        print("The current video is %s" %currentVideo)
elif videoExists == 0: 
    print('error')
    currentVideo = os.listdir(viddir)[0]
    f = open('nowPlaying', 'w')
    f.write(currentVideo)
    f.close() 
    if not args.random:
        print("The current video is %s" %currentVideo)

movieList = []

# log files store the current progress for all the videos available 
for file in os.listdir(viddir):
    if not file.startswith('.'):
        movieList.append(file)
        try: 
            log = open(logdir +'%s.progress'%file)
            log.close()
        except: 
            log = open(logdir + '%s.progress' %file, "w")
            log.write("0")
            log.close()

currentPosition = 0

# Open the log file and update the current position 
log = open(logdir + '%s.progress'%currentVideo)
for line in log:
    currentPosition = float(line)

inputVid = viddir + currentVideo

# Check how many frames are in the movie 
frameCount = int(ffmpeg.probe(inputVid)['streams'][0]['nb_frames'])
if not args.random:    
    print("there are %d frames in this video" %frameCount)

def display():
    image = Image.open("frame.bmp")
    frame = ImageTk.PhotoImage(image) 
    label.configure(image=frame)
    label.image = frame
    root.after(searchDispaly *1000, update)

def update():
    global currentPosition
    global currentVideo

    inputVid = viddir + currentVideo    
    frame = currentPosition
    msTimecode = "%dms"%(frame*41.666666)
        
    if args.random:
        pil_im = Image.open(random_pic(picdir))
        pil_im = pil_im.resize((648,480))
        print('Diplaying random picture')
    else:
        # Use ffmpeg to extract a frame from the movie, crop it, letterbox it and save it as grab.jpg 
        generate_frame(inputVid, 'grab.jpg', msTimecode, 648, 480)
        pil_im = Image.open('grab.jpg')
        print('Diplaying frame %d of %s' %(frame,currentVideo))

    # display the image 
    pyt = ImageTk.PhotoImage(pil_im)
    label.configure(image=pyt)
    label.image = pyt

    if not args.random:
        currentPosition = currentPosition + increment 
        if currentPosition >= frameCount:
            currentPosition = 0
            log = open(logdir + '%s.progress'%currentVideo, 'w')
            log.write(str(currentPosition))
            log.close() 
        
            thisVideo = movieList.index(currentVideo)
            if thisVideo < len(movieList)-1:
                currentVideo = movieList[thisVideo+1]
            else:
                currentVideo = movieList[0]
        log = open(logdir + '%s.progress'%currentVideo, 'w')
        log.write(str(currentPosition))
        log.close() 
        f = open('nowPlaying', 'w')
        f.write(currentVideo)
        f.close() 

    root.after(frameDelay*1000 , update)  

thread.start_new_thread( run_clap, ("run_clap",) )

root = Tk()
root.title("相框")
root.geometry('648x480')
image = Image.open("grab.jpg")
pyt = ImageTk.PhotoImage(image)
label = Label(root, image=pyt)
label.pack()
update() 
root.mainloop()
