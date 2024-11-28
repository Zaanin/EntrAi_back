import cv2
import face_recognition as fr
import os
import cvzone

nomes = []
encods = []
lista = os.listdir('pessoas')

# Carregar e codificar imagens no diretório 'pessoas'
import cv2
import face_recognition as fr
import os
import pickle
from multiprocessing import Pool

nomes = []
encods = []

# Função para carregar e codificar uma única imagem
def carregar_e_codificar(imagem):
    img = cv2.imread(f'pessoas/{imagem}')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encoding = fr.face_encodings(img)
    if encoding:
        return os.path.splitext(imagem)[0], encoding[0]
    return None

# Verifica se já existe um arquivo de cache com as codificações
if os.path.exists('codificacoes.pkl'):
    with open('codificacoes.pkl', 'rb') as f:
        nomes, encods = pickle.load(f)
else:
    lista = os.listdir('pessoas')
    
    # Carrega e codifica as imagens em paralelo
    with Pool() as pool:
        resultados = pool.map(carregar_e_codificar, lista)

    # Filtra resultados válidos e atualiza as listas de nomes e codificações
    for res in resultados:
        if res:
            nome, encoding = res
            nomes.append(nome)
            encods.append(encoding)

    # Salva as codificações em um arquivo
    with open('codificacoes.pkl', 'wb') as f:
        pickle.dump((nomes, encods), f)


def compararEnc(EncImg):
    for id, enc in enumerate(encods):
        comp = fr.compare_faces([EncImg], enc)
        if comp[0]:
            return True, nomes[id]
    return False, None

video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Erro: Não foi possível acessar a câmera.")
    exit()

while True:
    check, frame = video.read()

    if not check:
        print("Erro ao ler o quadro da câmera.")
        break

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faceloc = fr.face_locations(imgRGB)  # Detecta localização de rostos

    if faceloc:
        # Pega a localização do primeiro rosto detectado
        y1, x2, y2, x1 = faceloc[0]
        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(frame, (x1, y1, w, h), colorR=(255, 0, 0))

        # Codifica o rosto detectado para comparação
        encodeImg = fr.face_encodings(imgRGB, faceloc)
        
        if encodeImg:
            comp, nome = compararEnc(encodeImg[0])

            # Exibe o nome da pessoa ou "Desconhecido"
            texto = nome if comp else 'Desconhecido'
            cvzone.putTextRect(frame, texto, (x1, y1 - 10), 2, 2, colorB=(0, 255, 0) if comp else (0, 0, 255))
    else:
        # Exibe "Nenhuma face detectada" no canto da tela
        cvzone.putTextRect(frame, 'Nenhuma face detectada', (50, 50), 2, 2, colorB=(0, 0, 255))

    cv2.imshow('Video', frame)
    key = cv2.waitKey(1)
    if key == 27:  # Pressione ESC para sair
        break

video.release()
cv2.destroyAllWindows()