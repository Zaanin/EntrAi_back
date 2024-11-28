import cv2
import face_recognition as fr
import os
import cvzone
import numpy as np
import mediapipe as mp
import math
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates
import pickle
from skimage.feature import local_binary_pattern
import psycopg2

DB_CONFIG = {
    'dbname': 'scannia',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',  # Altere para o endereço do servidor, se necessário
    'port': 5432          # Porta padrão do PostgreSQL
}

try:
    # Conectar ao banco de dados
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
except Exception as e:
    print(f"Erro ao conectar com o banco: {e}")


# Configurações iniciais
limiar = 0.6  # Tolerância para reconhecimento facial
nomes = []
encods = []

# Carregar codificações salvas
if os.path.exists('codificacoes.pkl'):
    with open('codificacoes.pkl', 'rb') as f:
        nomes, encods = pickle.load(f)

# Função para comparar codificações
def compararEnc(EncImg):
    for id, enc in enumerate(encods):
        distancia = np.linalg.norm(enc - EncImg)
        if distancia < limiar:
            return True, nomes[id]
    return False, None

# Função de análise de textura usando LBP
def verificar_textura(img, raio=3, n_points=24):
    lbp = local_binary_pattern(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), n_points, raio, method="uniform")
    hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
    hist = hist.astype("float")
    hist /= hist.sum()
    return hist

# Verificar qualidade da imagem
def verificar_qualidade(img):
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    return laplacian_var > 100

# Inicialização do MediaPipe
mp_face_mesh = mp.solutions.face_mesh

# Configuração da captura de vídeo
cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FPS, 120)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Variáveis para detecção de piscada
openedEyes = 500
closedEyes = 0
blinkMap = 0
piscando = False
blinkCount = 0
calibrating = True
reconhecimento_pendente = False
piscadas_necessarias = 1  # Número de piscadas consecutivas para validar o reconhecimento

# Inicializar detecção facial
with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Erro ao capturar a imagem.")
            break

        # Preprocessamento da imagem
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Verificar landmarks faciais
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark

            # Obter coordenadas para cálculo da piscada
            cord1 = _normalized_to_pixel_coordinates(face_landmarks[159].x, face_landmarks[159].y, width, height)
            cord2 = _normalized_to_pixel_coordinates(face_landmarks[145].x, face_landmarks[145].y, width, height)
            cord3 = _normalized_to_pixel_coordinates(face_landmarks[33].x, face_landmarks[33].y, width, height)
            cord4 = _normalized_to_pixel_coordinates(face_landmarks[133].x, face_landmarks[133].y, width, height)

            if None not in [cord1, cord2, cord3, cord4]:
                # Cálculo das distâncias entre pálpebras
                dist = math.sqrt((cord1[0] - cord2[0])**2 + (cord1[1] - cord2[1])**2)
                dist2 = math.sqrt((cord4[0] - cord3[0])**2 + (cord4[1] - cord3[1])**2)
                ratio = dist2 / (dist + 0.001)

                # Lógica de calibração de piscada
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
                        piscando = True
                    if ratio >= blinkMap + 1 and piscando:
                        piscando = False
                        blinkCount += 1

                        # Habilita reconhecimento facial somente após múltiplas piscadas válidas
                        if blinkCount >= piscadas_necessarias:
                            reconhecimento_pendente = True

                # Mostrar contador de piscadas
                #font = cv2.FONT_HERSHEY_SIMPLEX
                #cv2.putText(image, f"Piscadas: {blinkCount}", (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Reconhecimento facial após validação completa
        if reconhecimento_pendente:
            # Verificar qualidade e textura da imagem
            if verificar_qualidade(image):
                face_locations = fr.face_locations(image)
                if face_locations:
                    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    face_encoding = fr.face_encodings(imgRGB, face_locations)
                    if face_encoding:
                        match, name = compararEnc(face_encoding[0])
                        cvzone.putTextRect(image, name if match else 'Desconhecido', (50, 100), 2, 2, colorB=(0, 255, 0) if match else (0, 0, 255))
                        if match:
                            cur.execute("""INSERT INTO logs values ('VALIDACAO','RECONHECIMENTO','TESTE','2024-08-12 13:12:00','USUARIO VALIDADO',));
                            """)
                            
                            # Confirmar as mudanças
                            conn.commit()
                            
            reconhecimento_pendente = False  # Resetar para aguardar próxima validação
            blinkCount = 0  # Resetar piscadas para novo ciclo

        # Exibir frame na tela
        cv2.imshow('Video', image)

        # Pressionar 'ESC' para sair
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
