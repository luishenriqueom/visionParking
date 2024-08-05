import cv2
import numpy as np

def calculate_histogram(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [1, 256])
    return cv2.normalize(hist, hist).flatten()

def is_parking_spot_occupied(current_hist, reference_hist, threshold=0.3):
    correlation = cv2.compareHist(reference_hist, current_hist, cv2.HISTCMP_CORREL)
    return correlation < threshold  # Se a correlação for menor que o limiar, consideramos a vaga ocupada

def crop_image(img, points):
    points = np.array(points)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    cropped_img = cv2.bitwise_and(img, img, mask=mask)
    x, y, w, h = cv2.boundingRect(points)
    return cropped_img[y:y + h, x:x + w]

def remove_bg(img):
    alpha = np.sum(img, axis=-1) > 0
    alpha = np.uint8(alpha * 255)
    return np.dstack((img, alpha))
