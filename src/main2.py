import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog as fd

class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Marcação de Vagas")
        # self.master.geometry("400x300")
        self.create_widgets()
        self.current_video_frame = None
        self.video_reproducing = False
        self.video_reproducing_job = None
        self.next_frame_btn_pressed = False
        # self.points = [(175, 259), (191, 311), (221, 273), (201, 239)]
        self.points = []
        self.markings = []
        self.imgTk_ref = None

    def create_widgets(self):
        self.frame_left_side = tk.Frame(self.master)
        self.frame_right_side = tk.Frame(self.master)

        self.video_progress_bar = tk.Scale(self.frame_right_side, from_=0, to=100, orient=tk.HORIZONTAL, command=self.update_frame_from_progress)
        self.frame_buttons_player = tk.Frame(self.frame_right_side)

        self.frame_referenced_video_frame = tk.Frame(self.master)
        self.frame_referenced_video_frame.config()
        
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
        
        self.btn_selecionar_demarcacoes = tk.Button(self.frame_menu, text="Selecionar Demarcações", state=tk.DISABLED, command=self.select_markings)
        self.btn_selecionar_demarcacoes.pack(fill=tk.X)

        self.btn_processar = tk.Button(self.frame_menu, text="Processar", state=tk.DISABLED, command=self.processing_video)
        self.btn_processar.pack(fill=tk.X)

    def click_event(self, event):
        # print(event.x, event.y)
        # print(event.event)

        self.points.append((event.x, event.y))
        print(self.points)
        cv2.circle(self.referenced_frame, (event.x, event.y), 5, (0, 255, 0), -1)
        if len(self.points) > 1:
            cv2.line(self.referenced_frame, self.points[-2], self.points[-1], (255, 0, 0), 2)
        if len(self.points) == 4:
            cv2.line(self.referenced_frame, self.points[-1], self.points[0], (255, 0, 0), 2)
            self.markings.append(self.points.copy())
            self.points.clear()

        self.update_ref_image()

    def update_ref_image(self):
        # for widget in self.frame_referenced_video_frame.winfo_children():
        #     widget.destroy()
        img = cv2.cvtColor(self.referenced_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.img_tk_ref = ImageTk.PhotoImage(image=img)
        self.label_frame_ref.config(image=self.img_tk_ref)
        self.label_frame_ref.image = self.img_tk_ref
    
    def add_marking(self):
        self.label_frame_ref.bind("<Button-1>", self.click_event)

    def select_markings(self):
        self.btn_selecionar_demarcacoes["text"] = "Finalizar Demarcações"
        self.btn_selecionar_demarcacoes["command"] = self.finish_markings
        self.add_marking()

    def finish_markings(self):
        self.btn_selecionar_demarcacoes["text"] = "Selecionar Demarcações"
        self.btn_selecionar_demarcacoes["command"] = self.select_markings

    def crop_image(self, img, points):
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, [points], 255)
        cropped_img = cv2.bitwise_and(img, mask)
        x,y,w,h = cv2.boundingRect(points)
        final_img = cropped_img[y:y+h, x:x+w]
        return final_img

    def processing_video(self):
        frame_cropped_images = tk.Frame(self.frame_left_side, background="blue")
        frame_cropped_images.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        cropped_image = self.crop_image(self.to_processing_frame, np.array(self.markings))
        img = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        self.imgTk_cropped = ImageTk.PhotoImage(image=img)
        panel = tk.Label(frame_cropped_images, image=self.imgTk_cropped)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def draw_polygon(self, img, points):
        # Converte a lista de pontos para o formato de array de pontos do OpenCV
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        # Desenha o polígono na imagem
        cv2.fillPoly(img, [pts], (0, 255, 0))  # Você pode escolher a cor e o preenchimento como preferir
        return img

    def crop_polygon(self, img, points):
        mask = np.zeros_like(img)
        mask = self.draw_polygon(mask, points)
        masked_img = cv2.bitwise_and(img, mask)
        # Cria uma máscara binária
        gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        # Extraí a ROI usando a máscara
        return cv2.bitwise_and(img, img, mask=gray_mask)

    def select_reference_frame(self):
        current_frame_bckp = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        print("current_frame_bckp:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_bckp)
        ret, self.referenced_frame = self.cap.read()
        self.to_processing_frame = self.referenced_frame.copy()
        print("new_current_frame:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_bckp)
        print("restored_frame:"+str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))))
        
        self.display_reference_frame()
        
        self.btn_selecionar_demarcacoes["state"] = tk.NORMAL

    def display_reference_frame(self):
        print("executei")
        for widget in self.frame_referenced_video_frame.winfo_children():
            widget.destroy()

        img = cv2.cvtColor(self.referenced_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.imgTk_ref = ImageTk.PhotoImage(image=img)
        self.label_frame_ref = tk.Label(self.frame_referenced_video_frame, image=self.imgTk_ref)
        self.label_frame_ref.pack(side=tk.TOP)
        # test_label = tk.Label(self.frame_referenced_video_frame, text="Referenced Frame")
        # test_label.pack(side=tk.TOP)
        self.frame_referenced_video_frame.pack(before=self.frame_right_side, side=tk.RIGHT, fill=tk.Y, expand=True)

    def open_video(self):
        video = fd.askopenfilename(filetypes=[("Arquivos de video", "*.mp4")])
        print(video)
        self.video_path = video

        self.cap = cv2.VideoCapture(self.video_path)
        self.ret, self.current_video_frame = self.cap.read()
        if not self.ret:
            print("Erro ao ler o frame.")
            exit()
        self.config_video_interface()
        self.btn_processar["state"] = tk.NORMAL
        
    def config_video_interface(self):
        self.frame_right_side.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.img = cv2.cvtColor(self.current_video_frame, cv2.COLOR_BGR2RGB)
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
        self.ret, self.current_video_frame = self.cap.read()
        if self.ret:
            self.img = cv2.cvtColor(self.current_video_frame, cv2.COLOR_BGR2RGB)
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
            self.ret, self.current_video_frame = self.cap.read()
            if self.ret:
                self.img = cv2.cvtColor(self.current_video_frame, cv2.COLOR_BGR2RGB)
                self.img = Image.fromarray(self.img)
                self.imgtk = ImageTk.PhotoImage(image=self.img)
                self.panel.config(image=self.imgtk)
                self.panel.image = self.imgtk

root = tk.Tk()
Application(root)
root.mainloop()