import cv2
import face_recognition as fr
import os
import cvzone
import numpy as np
import mediapipe as mp
import math
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates
import pickle

# Definir o limiar de comparação para o reconhecimento facial
limiar = 0.6  # Ajuste conforme necessário

# Variáveis globais
nomes = []
encods = []

# Função para calcular distância entre dois pontos
def calcular_distancia(p1, p2):
    if p1 is None or p2 is None:
        return None
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Carregar codificações de arquivo
if os.path.exists('codificacoes.pkl'):
    with open('codificacoes.pkl', 'rb') as f:
        nomes, encods = pickle.load(f)

# Função para comparar codificação com banco de dados
def compararEnc(EncImg):
    for id, enc in enumerate(encods):
        distancia = np.linalg.norm(enc - EncImg)
        if distancia < limiar:
            return True, nomes[id]
    return False, None

# Inicialização do MediaPipe
mp_face_mesh = mp.solutions.face_mesh

# Configuração de captura de vídeo
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 120)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Variáveis de piscada
openedEyes = 500
closedEyes = 0
blinkMap = 0
piscando = False
blinkCount = 0
calibrating = True

# Controle do reconhecimento facial
reconhecer_face = False
reconhecido = None  # Última pessoa reconhecida

with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Erro ao capturar a imagem.")
            break

        # Processar imagem com MediaPipe
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Verificar landmarks faciais
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark

            # Coordenadas dos olhos
            cord1 = _normalized_to_pixel_coordinates(face_landmarks[159].x, face_landmarks[159].y, width, height)
            cord2 = _normalized_to_pixel_coordinates(face_landmarks[145].x, face_landmarks[145].y, width, height)
            cord3 = _normalized_to_pixel_coordinates(face_landmarks[33].x, face_landmarks[33].y, width, height)
            cord4 = _normalized_to_pixel_coordinates(face_landmarks[133].x, face_landmarks[133].y, width, height)

            # Calcular distâncias entre os olhos
            dist = calcular_distancia(cord1, cord2)
            dist2 = calcular_distancia(cord4, cord3)

            if dist is not None and dist2 is not None:
                ratio = dist2 / (dist + 0.001)

                # Lógica de piscada
                if calibrating:
                    if ratio < openedEyes and not piscando:
                        blinkCount += 1
                        openedEyes = ratio
                        piscando = True
                    if ratio >= closedEyes and piscando:
                        closedEyes = ratio
                        piscando = False
                    if blinkCount >= 5:
                        blinkMap = closedEyes + (openedEyes - closedEyes) / 2
                        calibrating = False
                        blinkCount = 0
                else:
                    if ratio < blinkMap and not piscando:
                        blinkCount += 1
                        piscando = True
                        reconhecer_face = True  # Ativar reconhecimento facial após piscada
                    if ratio >= blinkMap + 1 and piscando:
                        piscando = False

                # Exibir contador de piscadas
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(image, f"Piscadas: {blinkCount}", (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Reconhecimento facial apenas após piscada validada
        if reconhecer_face:
            imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = fr.face_locations(imgRGB)
            if face_locations:
                face_encodings = fr.face_encodings(imgRGB, face_locations)
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    match, name = compararEnc(face_encoding)
                    top, right, bottom, left = face_location
                    color = (0, 255, 0) if match else (0, 0, 255)
                    label = name if match else "Desconhecido"
                    reconhecido = label  # Salvar último reconhecido
                    cv2.rectangle(image, (left, top), (right, bottom), color, 2)
                    cvzone.putTextRect(image, label, (left, top - 10), scale=1, thickness=1, colorB=color)

            reconhecer_face = False  # Resetar flag após reconhecimento

        # Exibir última pessoa reconhecida
        if reconhecido:
            cv2.putText(image, f"Ultimo: {reconhecido}", (50, 100), font, 1, (0, 255, 255), 2, cv2.LINE_AA)

        # Exibir frame
        cv2.imshow('Video', image)

        # Pressione 'ESC' para sair
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
