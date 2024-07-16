import cv2
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk

# Função para capturar cliques do mouse
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
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

# Função para iniciar o processamento após as marcações
def start_processing():
    print("Iniciando processamento com as seguintes marcações:")
    for idx, marking in enumerate(markings):
        print(f"Marcação {idx + 1}: {marking}")
    # Aqui você pode adicionar a lógica para processar as marcações

# Função para atualizar a imagem no Tkinter
def update_image():
    # global frame
    img = cv2.cvtColor(initialFrame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    panel.imgtk = imgtk
    panel.config(image=imgtk)

# Inicializar a interface Tkinter
root = tk.Tk()
root.title("Sistema de Marcação de Vagas")

# Frame do vídeo
video_path = 'C:\\Users\\Luis\\Documents\\ufpi\\7_periodo\\visao_computacional\\final_project\\video\\Parking.mp4'
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

# Criar o painel para exibir a imagem
img = cv2.cvtColor(initialFrame, cv2.COLOR_BGR2RGB)
img = Image.fromarray(img)
imgtk = ImageTk.PhotoImage(image=img)
panel = tk.Label(root, image=imgtk)
panel.pack(side="top", fill="both", expand="yes")

# Botões para adicionar marcação e iniciar processamento
btn_add = tk.Button(root, text="Adicionar Marcação", command=add_marking)
btn_add.pack(side="left", padx=10, pady=10)
btn_start = tk.Button(root, text="Iniciar", command=start_processing)
btn_start.pack(side="right", padx=10, pady=10)

# Iniciar o loop do Tkinter
root.mainloop()

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()