# Author : sheeptank
# Version: 0.0.1

from threading import Thread
import dearpygui.dearpygui as dpg
import numpy as np
import argparse
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--servers", help="File containing RTSP URIs", required=True)
args = parser.parse_args()

rtspServers = open(args.servers,"r").read().strip().split("\n")
captures = {}
for url in rtspServers:
    try:
        if not url.startswith("#"):
            captures[len(captures)] = {"capture":cv2.VideoCapture(url),"url":url}
    except:
        pass

TEXTURE_WIDTH   = int(1920/2) if len(captures) > 1 else 1920
TEXTURE_HEIGHT  = int(1080/2) if len(captures) > 1 else 1080
VIEWPORT_WIDTH  = 1920 if len(captures) > 1 else int(1920/2)
if len(captures) == 1:
    VIEWPORT_HEIGHT = 1080+55
else:
    VIEWPORT_HEIGHT = 1080+55 if len(captures) > 2 else int(1080/2)+55

dpg.create_context()
dpg.create_viewport(title='RTSPViewer', width=1920, height=VIEWPORT_HEIGHT)
dpg.setup_dearpygui()

with dpg.texture_registry(show=False):
    for i, k in captures.items():
        dpg.add_raw_texture(width=TEXTURE_WIDTH, height=TEXTURE_HEIGHT, default_value=[], tag=f"frame{i}", format=dpg.mvFormat_Float_rgb)

totalGroups = int(len(captures)/2)
caps = len(captures)
c    = 0
with dpg.window(tag="mainWindow"):
    for groupId in range(0,totalGroups+1):
        with dpg.group(horizontal=True):
            for i in range(0,2):
                if c<caps:
                    dpg.add_image(f"frame{c}")
                    c+=1
                else:
                    break

dpg.set_primary_window("mainWindow", True)
dpg.show_viewport()

def processFrame(frame)->np.ndarray:
    colourShift  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resizedFrame = cv2.resize(colourShift, (TEXTURE_WIDTH,TEXTURE_HEIGHT))
    return np.array(resizedFrame, dtype=np.float32).ravel()/255

def streamHandler(capture, frameId, url):
    while True:
        try:
            _,frame = capture.read()
            dpg.set_value(f"frame{frameId}", processFrame(frame))
        except:
            capture = cv2.VideoCapture(url)

for i, k in captures.items():
    cap = k["capture"]
    url = k["url"]
    proc = Thread(target=streamHandler, args=(cap, i, url))
    proc.start()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

try: 
    for i in captures: i.release()
except: pass

dpg.destroy_context()