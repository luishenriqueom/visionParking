import cv2
import matplotlib.pyplot as plt

# Função para capturar cliques do mouse
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('First Frame', frame)
        if len(points) == 4:
            cv2.destroyAllWindows()

# Abrir o vídeo
video_path = 'C:\\Users\\Luis\\Documents\\ufpi\\7_periodo\\visao_computacional\\final_project\\video\\Parking.mp4'
cap = cv2.VideoCapture(video_path)

# Ler o primeiro frame
ret, frame = cap.read()
if not ret:
    print("Erro ao abrir o vídeo")
    cap.release()
    exit()

# Lista para armazenar os pontos
points = []

# Exibir o frame e capturar os pontos
cv2.imshow('First Frame', frame)
cv2.setMouseCallback('First Frame', click_event)
cv2.waitKey(0)

# Mostrar os pontos selecionados
print("Pontos selecionados: ", points)

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()

# Exibir a área selecionada usando matplotlib
if len(points) == 4:
    fig, ax = plt.subplots()
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    rect = plt.Polygon(points, closed=True, fill=None, edgecolor='r')
    ax.add_patch(rect)
    plt.show()
else:
    print("A seleção não foi concluída corretamente.")
