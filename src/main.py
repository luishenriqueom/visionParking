import cv2
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Função para capturar cliques do mouse
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(points)
        cv2.circle(initialFrame, (x, y), 5, (0, 255, 0), -1)
        if len(points) > 1:
            cv2.line(initialFrame, points[-2], points[-1], (255, 0, 0), 2)
        cv2.imshow('First Frame', initialFrame)
        if len(points) == 4:
            cv2.line(initialFrame, points[-1], points[0], (255, 0, 0), 2)
            cv2.imshow('First Frame', initialFrame)
            markings.append(points.copy())
            points.clear()
            cv2.destroyAllWindows()
            update_image()

# Função para adicionar uma marcação
def add_marking():
    # global frame
    # ret, frame = cap.read()
    if not ret:
        print("Erro ao ler o frame")
        return
    cv2.imshow('First Frame', initialFrame)
    cv2.setMouseCallback('First Frame', click_event)

# Função para desenhar as marcações no frame
def draw_markings(frame, markings):
    for marking in markings:
        for i in range(4):
            cv2.circle(frame, marking[i], 5, (0, 255, 0), -1)
            cv2.line(frame, marking[i], marking[(i + 1) % 4], (255, 0, 0), 2)
    return frame

# Função para calcular e plotar o histograma de uma região
def plot_histogram(region, ax):
    hist = cv2.calcHist([region], [0], None, [256], [1, 256])
    ax.clear()
    ax.plot(hist, color='k')
    ax.set_xlim([0, 256])
    ax.set_title('Histograma da Região')
    ax.set_xlabel('Intensidade de Pixel')
    ax.set_ylabel('Contagem')

# Função para calcular o histograma de cada marcação
def calculate_histograms(frame, markings, ax):
    for marking in markings:
        pts = np.array(marking, np.int32)
        print(pts)
        pts = pts.reshape((-1, 1, 2))
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        region = cv2.bitwise_and(frame, frame, mask=mask)
        region_gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        print(region_gray)
        plot_histogram(region_gray, ax)
    ax.figure.canvas.draw()

# Função para iniciar o processamento após as marcações
def start_processing():
    global cap, speed
    print("Iniciando processamento com as seguintes marcações:")
    for idx, marking in enumerate(markings):
        print(f"Marcação {idx + 1}: {marking}")
    # Aqui você pode adicionar a lógica para processar as marcações
    
    cap.release()
    cap = cv2.VideoCapture(video_path)

     # Criar figura do matplotlib para exibir os histogramas
    fig, ax = plt.subplots(figsize=(5, 4))
    canvas = FigureCanvasTkAgg(fig, master=histogram_frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    ax.set_title('Histograma da Região')
    ax.set_xlabel('Intensidade de Pixel')
    ax.set_ylabel('Contagem')

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        calculate_histograms(frame, markings, ax)
        frame = draw_markings(frame, markings)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
        root.update_idletasks()
        root.update()
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break
    
    # plt.ioff()  # Desabilitar modo interativo do matplotlib
    # plt.show()
    
    cap.release()
    cv2.destroyAllWindows()

# Função para atualizar a imagem no Tkinter
def update_image():
    # global frame
    img = cv2.cvtColor(initialFrame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    panel.imgtk = imgtk
    panel.config(image=imgtk)
    
# Função para ajustar a velocidade do vídeo
def adjust_speed(val):
    global speed
    speed = int(val)



# Inicializar a interface Tkinter
root = tk.Tk()
root.title("Sistema de Marcação de Vagas")

# Frame do vídeo
video_path = 'video/Parking.mp4'
cap = cv2.VideoCapture(video_path)

# Lista para armazenar as marcações e os pontos
markings = []
points = []

# Frame inicial
global initialFrame
ret, initialFrame = cap.read()
if not ret:
    print("Erro ao abrir o vídeo")
    cap.release()
    exit()

# Configurar a interface Tkinter
root.geometry("1200x600")

# Criar frames para organizar a interface
left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="both", expand=True)

right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True)

# Criar o painel para exibir a imagem
img = cv2.cvtColor(initialFrame, cv2.COLOR_BGR2RGB)
img = Image.fromarray(img)
imgtk = ImageTk.PhotoImage(image=img)
panel = tk.Label(root, image=imgtk)
panel.pack(side="top", fill="both", expand="yes")

# Frame para os botões
btn_frame = tk.Frame(right_frame)
btn_frame.pack(side="top", fill="both", expand=True)

# Botões para adicionar marcação e iniciar processamento
btn_add = tk.Button(root, text="Adicionar Marcação", command=add_marking)
btn_add.pack(side="left", padx=10, pady=10)

btn_start = tk.Button(root, text="Iniciar", command=start_processing)
btn_start.pack(side="right", padx=10, pady=10)

# Frame para exibir os histogramas
histogram_frame = tk.Frame(right_frame)
histogram_frame.pack(side="bottom", fill="both", expand=True)


# Adicionar barra de progresso do vídeo
global video_slider
video_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', label="Progresso do Vídeo", length=500)
video_slider.pack(side="bottom", fill="x", expand="no")

def setup_video_progress():
    global video_slider
    """ Configura a barra de progresso para o vídeo. """
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_slider.config(to=total_frames, tickinterval=int(total_frames / 10))

def update_video_progress():
    global video_slider
    """ Atualiza a posição da barra de progresso conforme o vídeo avança. """
    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    video_slider.set(current_frame)
    root.after(50, update_video_progress)

setup_video_progress()

update_video_progress()

# Adicionar controle deslizante para ajustar a velocidade
# speed = 30  # Valor padrão do delay (milissegundos)
# speed_slider = tk.Scale(right_frame, from_=0, to=1, orient=tk.HORIZONTAL, label="Velocidade do Vídeo", command=adjust_speed, resolution=1000)
# speed_slider.set(speed)
# speed_slider.pack(padx=10, pady=10)

# Iniciar o loop do Tkinter
root.mainloop()

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()
