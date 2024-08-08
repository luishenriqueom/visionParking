import cv2
from PIL import Image, ImageTk
import tkinter as tk
from utils import crop_image, remove_bg, is_parking_spot_occupied, calculate_histogram, resize_frame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def process_video_frame(app):
    app.frame_right_side.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    app.img = cv2.cvtColor(app.current_video_frame, cv2.COLOR_BGR2RGB)
    app.img = Image.fromarray(app.img)
    app.imgtk = ImageTk.PhotoImage(image=app.img)
    app.panel = tk.Label(app.frame_right_side, image=app.imgtk)
    app.panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    app.video_progress_bar.config(to=int(app.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    app.video_progress_bar.pack(fill=tk.X)
    app.btn_next_frame = tk.Button(app.frame_buttons_player, text="⏭", command=app.next_frame_video)
    app.btn_next_frame.pack(side=tk.RIGHT)
    app.btn_play_video = tk.Button(app.frame_buttons_player, text="▷", command=app.play_video)
    app.btn_play_video.pack(side=tk.RIGHT)
    app.btn_previous_frame = tk.Button(app.frame_buttons_player, text="⏮", command=app.previous_frame_video)
    app.btn_previous_frame.pack(side=tk.RIGHT)
    app.frame_buttons_player.pack(fill=tk.X)
    app.btn_selecionar_frame_referencia["state"] = tk.NORMAL
    app.btn_processar["state"] = tk.NORMAL

