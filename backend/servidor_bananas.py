from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64

app = FastAPI()

# Permitir peticiones desde el proyecto de Vue en la red local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Cargar pesos de tu Red Neuronal (Modelo B: 4-12-6-1)
datos = np.load('pesos_modelo_B.npz')
W1, b1 = datos['W1'], datos['b1']
W2, b2 = datos['W2'], datos['b2']
W3, b3 = datos['W3'], datos['b3']

def sigmoide(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

def forward_red(x_vec):
    a1 = np.tanh(np.dot(x_vec, W1) + b1)
    a2 = np.tanh(np.dot(a1, W2) + b2)
    a3 = sigmoide(np.dot(a2, W3) + b3)
    return float(a3[0, 0]), a1, a2, a3

# 2. Lógica Difusa Mamdani (Matriz FAM 5x5)
def mf_trap(x, a, b, c, d):
    return float(np.maximum(0.0, np.minimum(np.minimum((x - a)/(b - a + 1e-9), 1.0), (d - x)/(d - c + 1e-9))))

def mf_tri(x, a, b, c):
    return float(np.maximum(0.0, np.minimum((x - a)/(b - a + 1e-9), (c - x)/(c - b + 1e-9))))

U_SALIDA = np.linspace(0.0, 1.0, 150)
CONJUNTOS_SALIDA = {
    'IN': np.array([mf_trap(u, 0.05, 0.08, 0.15, 0.25) for u in U_SALIDA]),
    'OP': np.array([mf_tri(u,  0.20, 0.38, 0.52)       for u in U_SALIDA]),
    'SM': np.array([mf_tri(u,  0.46, 0.64, 0.78)       for u in U_SALIDA]),
    'DA': np.array([mf_tri(u,  0.72, 0.82, 0.90)       for u in U_SALIDA]),
    'CR': np.array([mf_trap(u, 0.85, 0.91, 0.98, 1.00) for u in U_SALIDA])
}
TABLA_FAM = [
    ['IN', 'IN', 'SM', 'DA', 'CR'],
    ['IN', 'OP', 'SM', 'DA', 'CR'],
    ['OP', 'OP', 'SM', 'DA', 'CR'],
    ['OP', 'OP', 'SM', 'DA', 'CR'],
    ['OP', 'SM', 'SM', 'DA', 'CR']
]

def inferencia_fam(x1, x2, x3, x4):
    mc = x2 / (x1 + x2 + 1e-6)
    dt = float(np.clip(0.50 * x3 + 0.50 * x4, 0.0, 1.0))
    mu_mc = [mf_trap(mc,0,0,0.15,0.35), mf_tri(mc,0.2,0.4,0.6), mf_tri(mc,0.45,0.65,0.82), mf_tri(mc,0.7,0.85,0.96), mf_trap(mc,0.88,0.95,1,1)]
    mu_dt = [mf_trap(dt,0,0,0.08,0.16), mf_tri(dt,0.12,0.20,0.27), mf_tri(dt,0.22,0.28,0.34), mf_tri(dt,0.29,0.36,0.44), mf_trap(dt,0.38,0.48,1,1)]
    
    sil = np.zeros_like(U_SALIDA)
    for i in range(5):
        for j in range(5):
            w = min(mu_mc[i], mu_dt[j])
            if w > 0:
                sil = np.maximum(sil, np.minimum(w, CONJUNTOS_SALIDA[TABLA_FAM[i][j]]))
    suma = np.sum(sil)
    return float(np.sum(U_SALIDA * sil) / suma) if suma > 0 else 0.50

def segmentar_fruto(img):
    """
    Separa la fruta del fondo con GrabCut inicializado con un rectángulo central
    de margen moderado (~12%).

    OJO: intentamos antes "adivinar" el color del fondo muestreando el borde de
    la foto y usar esa estimación para sembrar la máscara de GrabCut. Eso falla
    en fondos de madera/café reales, porque su matiz y saturación pueden ser
    casi idénticos a los de la banana (solo cambia el brillo) y además el fondo
    no es uniforme (madera clara arriba, oscura abajo). Ahí la "adivinanza" de
    color termina marcando el fondo como si fuera la fruta.

    GrabCut puro (sin esa adivinanza) funciona mejor aquí porque modela el color
    de cada región con una mezcla de gaussianas sobre los 3 canales (no un solo
    umbral) y además usa los bordes/contraste reales de la imagen para decidir
    dónde cortar, así que distingue la fruta incluso cuando el color medio del
    fondo se parece mucho al de la banana.
    """
    h, w = img.shape[:2]
    # 12% de margen (no 5%): con margen chico, GrabCut a veces "se come" medio
    # fondo de madera oscura junto con la banana (fondo y fruta demasiado parecidos
    # en color). Con más margen le damos más muestra de fondo seguro y el corte
    # sale limpio; validado contra fotos reales que antes fallaban.
    mx, my = max(4, int(w * 0.12)), max(4, int(h * 0.12))
    rect = (mx, my, w - 2 * mx, h - 2 * my)

    mask_fruto = None
    try:
        mask_gc = np.zeros((h, w), np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask_gc, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        resultado = np.where((mask_gc == cv2.GC_FGD) | (mask_gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        area_resultado = cv2.countNonZero(resultado)
        # Si GrabCut termina marcando casi nada o casi todo, algo salió mal
        if 0.01 * h * w < area_resultado < 0.97 * h * w:
            mask_fruto = resultado
    except cv2.error:
        mask_fruto = None

    if mask_fruto is None:
        # Red de seguridad: si GrabCut no converge, usamos el umbral de saturación clásico
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _, s, _ = cv2.split(hsv)
        _, mask_fruto = cv2.threshold(s, 50, 255, cv2.THRESH_BINARY)

    mask_fruto = cv2.morphologyEx(mask_fruto, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    mask_fruto = cv2.morphologyEx(mask_fruto, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    contornos, _ = cv2.findContours(mask_fruto, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_limpia = np.zeros_like(mask_fruto)
    if contornos:
        c_max = max(contornos, key=cv2.contourArea)
        cv2.drawContours(mask_limpia, [c_max], -1, 255, thickness=cv2.FILLED)
    return mask_limpia

@app.post("/analizar")
async def analizar_imagen(file: UploadFile = File(...)):
    contenido = await file.read()
    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo recibido está vacío.")

    arr = np.frombuffer(contenido, np.uint8)
    img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        # Ocurre con formatos que OpenCV no decodifica (p. ej. HEIC/HEIF de iPhone)
        raise HTTPException(
            status_code=400,
            detail="No se pudo decodificar la imagen. Usa JPG o PNG (en iPhone, desactiva 'Formato alta eficiencia' o exporta como JPG)."
        )
    img = cv2.resize(img_bgr, (256, 256))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    _, s, v = cv2.split(hsv)

    mask_limpia = segmentar_fruto(img)

    area = max(float(cv2.countNonZero(mask_limpia)), 1.0)
    x1 = float(np.clip(cv2.countNonZero(cv2.bitwise_and(cv2.inRange(hsv, np.array([35,45,40]), np.array([85,255,255])), mask_limpia)) / area, 0, 1))
    x2 = float(np.clip(cv2.countNonZero(cv2.bitwise_and(cv2.inRange(hsv, np.array([18,60,80]), np.array([34,255,255])), mask_limpia)) / area, 0, 1))
    m_cafe = cv2.inRange(hsv, np.array([5,30,15]), np.array([17,255,135]))

    # Señal 1: "mancha" oscura LOCAL, relativa al brillo propio de la banana
    # (para no confundir sombra direccional sobre una banana sana con daño real).
    pix_v_banana = v[mask_limpia == 255]
    v_mediana = float(np.median(pix_v_banana)) if len(pix_v_banana) > 0 else 128.0
    umbral_negro = max(25.0, v_mediana * 0.45)
    m_negro = cv2.inRange(v, 0, umbral_negro)
    x3_manchas_locales = float(np.clip(cv2.countNonZero(cv2.bitwise_and(cv2.bitwise_or(m_cafe, m_negro), mask_limpia)) / area, 0, 1))

    # Señal 2: qué fracción de la fruta NO se ve ni verde ni amarilla sana.
    # La señal 1 sola falla cuando la banana está COMPLETAMENTE ennegrecida/podrida:
    # al no haber ninguna zona "normal" de referencia, todo se ve oscuro por igual
    # y el umbral relativo no dispara. Esta señal 2 cubre justo ese caso (si casi
    # nada del área es verde/amarillo, es casi seguro que está dañada/podrida).
    x3_sin_color_sano = float(np.clip(1.0 - (x1 + x2), 0.0, 1.0))

    x3 = max(x3_manchas_locales, x3_sin_color_sano)
    pix_v = pix_v_banana
    x4 = float(np.clip((np.std(pix_v) / 128.0) if len(pix_v) > 0 else 0.0, 0, 1))

    y_red, _, _, _ = forward_red(np.array([[x1, x2, x3, x4]]))
    y_dif = inferencia_fam(x1, x2, x3, x4)

    _, buffer_mask = cv2.imencode('.png', mask_limpia)
    mask_b64 = base64.b64encode(buffer_mask).decode('utf-8')

    return {
        "entradas": {"x1": round(x1, 4), "x2": round(x2, 4), "x3": round(x3, 4), "x4": round(x4, 4)},
        "red_neuronal": {"y": round(y_red, 4), "voltaje": round(y_red * 5.0, 3)},
        "logica_difusa": {"y": round(y_dif, 4), "voltaje": round(y_dif * 5.0, 3)},
        "mascara_b64": f"data:image/png;base64,{mask_b64}"
    }

@app.post("/actualizar")
async def actualizar_pesos(x1: float = Form(...), x2: float = Form(...), x3: float = Form(...), x4: float = Form(...), y_objetivo: float = Form(...)):
    global W1, b1, W2, b2, W3, b3
    x_vec = np.array([[x1, x2, x3, x4]])
    Y_real = np.array([[y_objetivo]])
    for _ in range(40):
        y_pred, a1, a2, _ = forward_red(x_vec)
        A3 = np.array([[y_pred]])
        dZ3 = (A3 - Y_real) * (A3 * (1.0 - A3))
        dW3 = np.dot(a2.T, dZ3); db3 = dZ3
        dZ2 = np.dot(dZ3, W3.T) * (1.0 - a2 ** 2)
        dW2 = np.dot(a1.T, dZ2); db2 = dZ2
        dZ1 = np.dot(dZ2, W2.T) * (1.0 - a1 ** 2)
        dW1 = np.dot(x_vec.T, dZ1); db1 = dZ1
        W3 -= 0.15 * dW3; b3 -= 0.15 * db3
        W2 -= 0.15 * dW2; b2 -= 0.15 * db2
        W1 -= 0.15 * dW1; b1 -= 0.15 * db1
    np.savez('pesos_modelo_B.npz', W1=W1, b1=b1, W2=W2, b2=b2, W3=W3, b3=b3)
    return {"status": "Pesos actualizados en vivo"}

# IMPORTANTE: host="0.0.0.0" hace que el servidor escuche en TODAS las interfaces
# de red (no solo 127.0.0.1), para que el celular pueda alcanzarlo en la red local.
# Si usas "uvicorn servidor_bananas:app --reload" en vez de "python servidor_bananas.py",
# agrega manualmente "--host 0.0.0.0 --port 8000" o el celular nunca podrá conectarse.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)