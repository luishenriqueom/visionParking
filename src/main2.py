import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog as fd

class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Marcação de Vagas")
        # self.master.geometry("400x300")
        self.create_widgets()
        self.video_reproducing = False
        self.video_reproducing_job = None
        self.next_frame_btn_pressed = False

    def create_widgets(self):
        self.frame_left_side = tk.Frame(self.master)
        self.frame_right_side = tk.Frame(self.master)

        self.video_progress_bar = tk.Scale(self.frame_right_side, from_=0, to=100, orient=tk.HORIZONTAL, command=self.update_frame_from_progress)
        self.frame_buttons_player = tk.Frame(self.frame_right_side)

        self.frame_referenced_video_frame = tk.Frame(self.master)
        self.frame_referenced_video_frame.config(background="red")
        
        self.frame_left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.frame_menu = tk.Frame(self.frame_left_side)
        self.frame_menu["pady"] = 20
        self.frame_menu["padx"] = 20
        self.frame_menu.pack(side=tk.TOP, expand=True, fill=tk.Y)
        
        # self.label_right_side = tk.Label(self.frame_right_side, text="Right Side")
        # self.label_right_side.pack()
        
        self.btn_selecionar_video = tk.Button(self.frame_menu, text="Selecionar Vídeo", command=self.open_video)
        self.btn_selecionar_video.pack(fill=tk.X)

        self.btn_selecionar_frame_referencia = tk.Button(self.frame_menu, text="Selecionar Frame de Referência", command=self.select_reference_frame, state=tk.DISABLED)
        self.btn_selecionar_frame_referencia.pack(fill=tk.X)
        
        self.btn_selecionar_demarcacoes = tk.Button(self.frame_menu, text="Selecionar Demarcações", state=tk.DISABLED)
        self.btn_selecionar_demarcacoes.pack(fill=tk.X)

        self.btn_processar = tk.Button(self.frame_menu, text="Processar", state=tk.DISABLED)
        self.btn_processar.pack(fill=tk.X)

    def select_reference_frame(self):
        current_frame_bckp = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        print("current_frame_bckp:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_bckp)
        ret, self.referenced_frame = self.cap.read()
        print("new_current_frame:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_bckp)
        print("restored_frame:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))

        self.display_reference_frame()

    def display_reference_frame(self):
        for widget in self.frame_referenced_video_frame.winfo_children():
            widget.destroy()

        img = cv2.cvtColor(self.referenced_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.imgTk_ref = ImageTk.PhotoImage(image=img)
        panel = tk.Label(self.frame_referenced_video_frame, image=self.imgTk_ref)
        panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        test_label = tk.Label(self.frame_referenced_video_frame, text="Referenced Frame")
        test_label.pack(side=tk.TOP)
        self.frame_referenced_video_frame.pack(before=self.frame_right_side, side=tk.RIGHT, fill=tk.Y, expand=True)

    def open_video(self):
        video = fd.askopenfilename(filetypes=[("Arquivos de video", "*.mp4")])
        print(video)
        self.video_path = video

        self.cap = cv2.VideoCapture(self.video_path)
        self.ret, self.initial_frame = self.cap.read()
        if not self.ret:
            print("Erro ao ler o frame.")
            exit()
        self.config_video_interface()
        
    def config_video_interface(self):
        self.frame_right_side.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.img = cv2.cvtColor(self.initial_frame, cv2.COLOR_BGR2RGB)
        self.img = Image.fromarray(self.img)
        self.imgtk = ImageTk.PhotoImage(image=self.img)
        self.panel = tk.Label(self.frame_right_side, image=self.imgtk)
        self.panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.video_progress_bar.config(to=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        self.video_progress_bar.pack(fill=tk.X) 

        self.btn_next_frame = tk.Button(self.frame_buttons_player, text="⏭", command=self.next_frame_video)
        self.btn_next_frame.pack(side=tk.RIGHT)
        self.btn_play_video = tk.Button(self.frame_buttons_player, text="▷", command=self.play_video)
        self.btn_play_video.pack(side=tk.RIGHT)
        self.btn_previous_frame = tk.Button(self.frame_buttons_player, text="⏮", command=self.previous_frame_video)
        self.btn_previous_frame.pack(side=tk.RIGHT)
        self.frame_buttons_player.pack(fill=tk.X)

        self.btn_selecionar_frame_referencia["state"] = tk.NORMAL

    def previous_frame_video(self):
        frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 2
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.ret, frame = self.cap.read()
        print("current frame:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        if self.ret:
            self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.img)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.panel.config(image=self.imgtk)
            self.panel.image = self.imgtk
            self.video_progress_bar.set(frame_number)

    def next_frame_video(self):
        self.video_progress_bar.configure(command=None)
        print("next current frame:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        self.ret, frame = self.cap.read()
        print("next updated frame:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        if self.ret:
            self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.img)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.panel.config(image=self.imgtk)
            self.panel.image = self.imgtk
            self.video_progress_bar.set(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reinicia o vídeo se chegar ao final
        
        self.video_progress_bar.configure(command=self.update_frame_from_progress)

    def play_video(self):
        if self.video_reproducing:
            self.master.after_cancel(self.video_reproducing_job)
            self.video_reproducing = False
            self.btn_play_video["text"] = "▷"
        else:
            self.video_reproducing = True
            self.btn_play_video["text"] = "⏸"
            self.update_frame()

    def update_frame(self):
        self.ret, frame = self.cap.read()
        if self.ret:
            self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.img)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.panel.config(image=self.imgtk)
            self.panel.image = self.imgtk
            self.video_progress_bar.set(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
            self.video_reproducing_job = self.master.after(33, self.update_frame)  # Atualiza a cada ~33ms (aproximadamente 30fps)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reinicia o vídeo se chegar ao final
            self.play_video()

    def update_frame_from_progress(self, value):
        if not self.next_frame_btn_pressed:
            frame_number = int(value)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.ret, frame = self.cap.read()
            if self.ret:
                self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.img = Image.fromarray(self.img)
                self.imgtk = ImageTk.PhotoImage(image=self.img)
                self.panel.config(image=self.imgtk)
                self.panel.image = self.imgtk

root = tk.Tk()
Application(root)
root.mainloop()