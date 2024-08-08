import cv2
import tkinter as tk
from tkinter import filedialog as fd
from PIL import Image, ImageTk
from widgets import create_widgets
from video_processing import process_video_frame
from utils import crop_image, remove_bg, is_parking_spot_occupied, calculate_histogram, equalize_histogram, resize_frame, convert_to_relative, convert_to_absolute
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Marcação de Vagas")
        self.master.state("zoomed")
        self.create_widgets()
        self.current_video_frame = None
        self.video_reproducing = False
        self.video_reproducing_job = None
        self.next_frame_btn_pressed = False
        self.points = []
        self.markings = []
        self.img_tk_ref = None
        self.original_size = None
        self.resized_size = (640, 480)  # Define o tamanho padronizado para os frames
        self.histWidgets = []
        self.panels_curr_images = []

    def create_widgets(self):
        create_widgets(self)

    def click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            cv2.circle(self.referenced_frame, (x, y), 5, (0, 255, 0), -1)
            if len(self.points) > 1:
                cv2.line(self.referenced_frame, self.points[-2], self.points[-1], (255, 0, 0), 2)
            if len(self.points) == 4:
                cv2.line(self.referenced_frame, self.points[-1], self.points[0], (255, 0, 0), 2)
                relative_points = convert_to_relative(self.points, self.resized_size)
                self.markings.append(relative_points)
                self.points.clear()
            cv2.imshow('Frame selecionado', self.referenced_frame)

    def update_ref_image(self):
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
        cv2.imshow('Frame selecionado', self.referenced_frame)

    def finish_markings(self):
        self.btn_selecionar_demarcacoes["text"] = "Selecionar Demarcações"
        self.btn_selecionar_demarcacoes["command"] = self.select_markings

    def plt_histogram(self, reference_histogram, current_hist):
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.plot(reference_histogram, color='blue', label='Referência')
        ax.plot(current_hist, color='black', label='Atual')
        ax.set_xlim([0, 256])
        ax.set_title('Histograma')
        ax.set_xlabel('Intensidade')
        ax.set_ylabel('Frequência')
        ax.legend()       
        return fig     

    # def update_current_cropped_image(self):
    #     ret, current_frame = self.cap.read()
    #     if not ret:
    #         return
    #     current_frame = resize_frame(current_frame, *self.resized_size)
    #     current_cropped_image = crop_image(current_frame, self.points)
    #     current_cropped_image_eq = equalize_histogram(current_cropped_image)
    #     current_img = cv2.cvtColor(current_cropped_image_eq, cv2.COLOR_BGR2RGBA)
    #     current_img = Image.fromarray(current_img)
    #     img_tk_current = ImageTk.PhotoImage(image=current_img)
    #     self.frame_curr_image.destroy()
    #     self.frame_curr_image = tk.Frame(self.frame_images_container)
    #     label_curr = tk.Label(self.frame_curr_image, text="Atual")
    #     label_curr.pack()
    #     panel_current = tk.Label(self.frame_curr_image, image=img_tk_current)
    #     panel_current.image = img_tk_current
    #     panel_current.pack(side=tk.LEFT, padx=5)
    #     self.frame_curr_image.pack(side=tk.RIGHT)
    #     self.update_current_status(current_cropped_image)

    def processing_video(self):
        if hasattr(self, 'frame_container'):
            self.frame_container.destroy()

        self.frame_container = tk.Frame(self.frame_left_side)
        self.frame_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_container)
        self.scrollbar = tk.Scrollbar(self.frame_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.reference_histograms = []
        for marking in self.markings:
            absolute_marking = convert_to_absolute(marking, self.resized_size)
            cropped_image = crop_image(self.to_processing_frame, absolute_marking)
            reference_hist = calculate_histogram(cropped_image)
            self.reference_histograms.append(reference_hist)

        for i, marking in enumerate(self.markings):
            absolute_marking = convert_to_absolute(marking, self.resized_size)
            cropped_image = crop_image(self.to_processing_frame, absolute_marking)
            cropped_image_without_bg = remove_bg(cropped_image)
            img_ref = cv2.cvtColor(cropped_image_without_bg, cv2.COLOR_BGR2RGBA)
            img_ref = Image.fromarray(img_ref)
            img_tk_ref = ImageTk.PhotoImage(image=img_ref)

            # ret, current_frame = self.cap.read()
            # if not ret:
            #     continue

            self.referenced_frame = resize_frame(self.referenced_frame, *self.resized_size)
            current_cropped_image = crop_image(self.referenced_frame, absolute_marking)
            current_cropped_image_eq = equalize_histogram(current_cropped_image)
            current_img = cv2.cvtColor(current_cropped_image_eq, cv2.COLOR_BGR2RGBA)
            current_img = Image.fromarray(current_img)
            img_tk_current = ImageTk.PhotoImage(image=current_img)

            frame_marking = tk.Frame(self.scrollable_frame, border=2, relief=tk.GROOVE)
            frame_marking.pack(side=tk.TOP, pady=10)
            
            self.frame_images_container = tk.Frame(frame_marking, pady=10)

            frame_ref_image = tk.Frame(self.frame_images_container)
            label_ref = tk.Label(frame_ref_image, text="Referência")
            label_ref.pack()
            panel_ref = tk.Label(frame_ref_image, image=img_tk_ref)
            panel_ref.image = img_tk_ref
            self.panels_curr_images.append(panel_ref)
            panel_ref.pack(padx=5)
            frame_ref_image.pack(side=tk.LEFT)
            
            self.frame_curr_image = tk.Frame(self.frame_images_container)
            label_curr = tk.Label(self.frame_curr_image, text="Atual")
            label_curr.pack()
            panel_current = tk.Label(self.frame_curr_image, image=img_tk_current)
            panel_current.image = img_tk_current

            panel_current.pack(side=tk.LEFT, padx=5)
            self.frame_curr_image.pack(side=tk.RIGHT)

            current_cropped_image = crop_image(self.current_video_frame, absolute_marking)
            current_cropped_image_eq = equalize_histogram(current_cropped_image)
            current_img = cv2.cvtColor(current_cropped_image_eq, cv2.COLOR_BGR2RGBA)
            current_img = Image.fromarray(current_img)
            img_tk_current = ImageTk.PhotoImage(image=current_img)
            self.frame_curr_image.destroy()
            self.frame_curr_image = tk.Frame(self.frame_images_container)
            label_curr = tk.Label(self.frame_curr_image, text="Atual")
            label_curr.pack()
            panel_current = tk.Label(self.frame_curr_image, image=img_tk_current)
            panel_current.image = img_tk_current
            panel_current.pack(side=tk.LEFT, padx=5)
            self.frame_curr_image.pack(side=tk.RIGHT)

            self.frame_images_container.pack(fill=tk.Y)

            current_hist = calculate_histogram(current_cropped_image)
            occupied = is_parking_spot_occupied(current_hist, self.reference_histograms[i], threshold=0.9)  # Ajuste o limiar conforme necessário
            status_text = "Ocupada" if occupied else "Livre"
            status_label = tk.Label(frame_marking, text=status_text, fg="red" if occupied else "green")
            status_label.pack(side=tk.LEFT, padx=5)

            fig = self.plt_histogram(self.reference_histograms[i], current_hist)
            # fig, ax = plt.subplots(figsize=(4, 2))
            # ax.plot(reference_histograms[i], color='blue', label='Referência')
            # ax.plot(current_hist, color='black', label='Atual')
            # ax.set_xlim([0, 256])
            # ax.set_title('Histograma')
            # ax.set_xlabel('Intensidade')
            # ax.set_ylabel('Frequência')
            # ax.legend()

            canvas_hist = FigureCanvasTkAgg(fig, master=frame_marking)
            canvas_hist.draw()
            hist_widget = canvas_hist.get_tk_widget()
            hist_widget.pack(side=tk.LEFT, padx=5)
            self.histWidgets.append(hist_widget)

            plt.close(fig)

    def select_reference_frame(self):
        current_frame_bckp = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_bckp)
        ret, self.referenced_frame = self.cap.read()
        if not ret:
            print("Erro ao ler o frame.")
            exit()
        self.original_size = (self.referenced_frame.shape[1], self.referenced_frame.shape[0])
        self.referenced_frame = resize_frame(self.referenced_frame, *self.resized_size)  # Redimensiona o frame de referência
        self.to_processing_frame = self.referenced_frame.copy()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_bckp)
        self.display_reference_frame()
        self.btn_selecionar_demarcacoes["state"] = tk.NORMAL

    def display_reference_frame(self):
        # print("Abrindo frame selecionado: ", self.referenced_frame)
        cv2.imshow("Frame selecionado", self.referenced_frame)
        cv2.setMouseCallback('Frame selecionado', self.click_event)
        while cv2.getWindowProperty("Frame selecionado", cv2.WND_PROP_VISIBLE) == 1:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyWindow("Frame selecionado")
                break
        self.points.clear()
        self.histWidgets.clear()
        self.processing_video()

    def open_video(self):
        video = fd.askopenfilename(filetypes=[("Arquivos de video", "*.mp4")])
        if not video:
            return
        self.video_path = video
        self.cap = cv2.VideoCapture(self.video_path)
        self.ret, self.current_video_frame = self.cap.read()
        if not self.ret:
            print("Erro ao ler o frame.")
            exit()
        self.original_size = (self.current_video_frame.shape[1], self.current_video_frame.shape[0])
        self.current_video_frame = resize_frame(self.current_video_frame, *self.resized_size)  # Redimensiona o frame atual
        self.config_video_interface()
        self.btn_processar["state"] = tk.NORMAL

    def config_video_interface(self):
        self.frame_referenced_video_frame.pack_forget()
        self.frame_right_side.pack_forget()
        self.frame_buttons_player.pack_forget()
        self.frame_menu.pack_forget()
        self.frame_menu.pack(side=tk.TOP)
        self.btn_selecionar_frame_referencia["state"] = tk.NORMAL
        self.btn_selecionar_video["state"] = tk.DISABLED
        self.btn_processar["state"] = tk.DISABLED
        # self.btn_selecionar_demarcacoes["state"] = tk.DISABLED
        self.btn_selecionar_frame_referencia["command"] = self.select_reference_frame
        # self.btn_selecionar_demarcacoes["command"] = self.select_markings
        self.btn_selecionar_video["command"] = self.open_video
        self.btn_processar["command"] = self.processing_video
        process_video_frame(self)

    def previous_frame_video(self):
        frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 2
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.ret, frame = self.cap.read()
        if self.ret:
            frame = resize_frame(frame, *self.resized_size)  # Redimensiona o frame anterior
            self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.img)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.panel.config(image=self.imgtk)
            self.panel.image = self.imgtk
            self.video_progress_bar.set(frame_number)

    def next_frame_video(self):
        self.video_progress_bar.configure(command=None)
        self.ret, frame = self.cap.read()
        if self.ret:
            frame = resize_frame(frame, *self.resized_size)  # Redimensiona o próximo frame
            self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.img)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.panel.config(image=self.imgtk)
            self.panel.image = self.imgtk
            self.video_progress_bar.set(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
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

    def update_current_cropped_image(self, frame):
        current_cropped_image = crop_image(frame, self.markings)
        current_cropped_image_eq = equalize_histogram(current_cropped_image)
        current_img = cv2.cvtColor(current_cropped_image_eq, cv2.COLOR_BGR2RGBA)
        current_img = Image.fromarray(current_img)
        img_tk_current = ImageTk.PhotoImage(image=current_img)
        self.frame_curr_image.destroy()
        self.frame_curr_image = tk.Frame(self.frame_images_container)
        label_curr = tk.Label(self.frame_curr_image, text="Atual")
        label_curr.pack()
        panel_current = tk.Label(self.frame_curr_image, image=img_tk_current)
        panel_current.image = img_tk_current
        panel_current.pack(side=tk.LEFT, padx=5)
        self.frame_curr_image.pack(side=tk.RIGHT)
        # self.update_current_status(current_cropped_image)

    def update_frame(self):
        self.ret, self.current_video_frame = self.cap.read()
        # print(self.histWidgets)
        # self.processing_video()
        if self.ret:
            self.current_video_frame = resize_frame(self.current_video_frame, *self.resized_size)  # Redimensiona o frame atual
            self.img = cv2.cvtColor(self.current_video_frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.img)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.panel.config(image=self.imgtk)
            self.panel.image = self.imgtk
            self.video_progress_bar.set(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
            self.video_reproducing_job = self.master.after(33, self.update_frame)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.play_video()

    def update_frame_from_progress(self, value):
        if not self.next_frame_btn_pressed:
            frame_number = int(value)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.ret, self.current_video_frame = self.cap.read()
            if self.ret:
                self.current_video_frame = resize_frame(self.current_video_frame, *self.resized_size)  # Redimensiona o frame atual do progresso
                self.img = cv2.cvtColor(self.current_video_frame, cv2.COLOR_BGR2RGB)
                self.img = Image.fromarray(self.img)
                self.imgtk = ImageTk.PhotoImage(image=self.img)
                self.panel.config(image=self.imgtk)
                self.panel.image = self.imgtk
