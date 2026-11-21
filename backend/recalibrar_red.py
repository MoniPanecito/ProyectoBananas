"""
Recalibración amplia de la Red Neuronal (Modelo B: 4-12-6-1) usando la Lógica
Difusa (FAM 5x5) como "maestra".

Por qué: la red entrenada en Colab quedó demasiado sensible a x4 (textura/
varianza de brillo) — hasta una banana perfecta con algo de textura normal de
iluminación se predecía como "Sobremadura/Dañada". La lógica difusa, con sus
reglas explícitas, no tiene ese problema, así que generamos un conjunto amplio
de entradas (x1,x2,x3,x4) representativas, calculamos su salida "correcta" con
la lógica difusa, y reentrenamos la red (con las mismas fórmulas de
backpropagation de /actualizar) para que se comporte de forma más sensata en
todo el espacio de entradas, no solo en un punto a la vez.

Uso: python recalibrar_red.py
Guarda el resultado en pesos_modelo_B.npz (el original queda respaldado en
pesos_modelo_B_backup_original.npz).
"""
import numpy as np

# --- Cargar arquitectura/funciones iguales a las de servidor_bananas.py ---
datos = np.load('pesos_modelo_B.npz')
W1, b1 = datos['W1'].copy(), datos['b1'].copy()
W2, b2 = datos['W2'].copy(), datos['b2'].copy()
W3, b3 = datos['W3'].copy(), datos['b3'].copy()

def sigmoide(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

def forward_red(x_vec):
    a1 = np.tanh(np.dot(x_vec, W1) + b1)
    a2 = np.tanh(np.dot(a1, W2) + b2)
    a3 = sigmoide(np.dot(a2, W3) + b3)
    return float(a3[0, 0]), a1, a2, a3

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

# --- Generar dataset de calibración (entradas plausibles + su "maestro" difuso) ---
rng = np.random.RandomState(42)
muestras = []

# Rejilla estructurada: recorre sistemáticamente verde/amarillo/manchas/textura
for x2 in np.linspace(0, 1, 11):
    for x1 in np.linspace(0, 1 - x2, 4):
        for x3 in [0.0, 0.05, 0.15, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0]:
            for x4 in [0.0, 0.1, 0.2, 0.35, 0.5]:
                muestras.append((x1, x2, x3, x4))

# Puntos aleatorios adicionales para cubrir combinaciones no cuadriculadas
for _ in range(400):
    x2 = rng.uniform(0, 1)
    x1 = rng.uniform(0, 1 - x2)
    x3 = rng.uniform(0, 0.8)
    x4 = rng.uniform(0, 0.6)
    muestras.append((x1, x2, x3, x4))

# Casos extremos de fruta totalmente dañada/podrida: x1=x2≈0 (nada de verde ni
# amarillo sano) y x3 muy alto. Sin esto la red extrapola mal ese corte porque
# nunca vio ejemplos tan cercanos a x3=1 durante el entrenamiento.
for _ in range(150):
    x3 = rng.uniform(0.85, 1.0)
    x4 = rng.uniform(0.0, 0.6)
    x1 = rng.uniform(0, 0.03)
    x2 = rng.uniform(0, 0.03)
    muestras.append((x1, x2, x3, x4))

X = np.array(muestras)
Y = np.array([[inferencia_fam(*m)] for m in muestras])
print(f"Dataset de calibración: {len(X)} muestras")

# --- Entrenamiento (mismas fórmulas de backprop que /actualizar, por lotes) ---
lr = 0.1
epocas = 800
n = len(X)

for epoca in range(epocas):
    idx = rng.permutation(n)
    perdida_total = 0.0
    for i in idx:
        x_vec = X[i:i+1]
        y_real = Y[i:i+1]

        y_pred, a1, a2, A3 = forward_red(x_vec)
        perdida_total += (y_pred - y_real[0, 0]) ** 2

        dZ3 = (A3 - y_real) * (A3 * (1.0 - A3))
        dW3 = np.dot(a2.T, dZ3); db3 = dZ3
        dZ2 = np.dot(dZ3, W3.T) * (1.0 - a2 ** 2)
        dW2 = np.dot(a1.T, dZ2); db2 = dZ2
        dZ1 = np.dot(dZ2, W2.T) * (1.0 - a1 ** 2)
        dW1 = np.dot(x_vec.T, dZ1); db1 = dZ1

        W3 -= lr * dW3; b3 -= lr * db3
        W2 -= lr * dW2; b2 -= lr * db2
        W1 -= lr * dW1; b1 -= lr * db1

    if epoca % 100 == 0 or epoca == epocas - 1:
        print(f"  época {epoca:4d}  MSE={perdida_total/n:.5f}")

np.savez('pesos_modelo_B.npz', W1=W1, b1=b1, W2=W2, b2=b2, W3=W3, b3=b3)
print("Pesos recalibrados guardados en pesos_modelo_B.npz")

# --- Validación rápida contra casos conocidos ---
print("\nValidación tras recalibrar:")
casos = [
    (0, 1, 0, 0, 'banana 100% amarilla, perfecta'),
    (0, 1, 0, 0.18, 'banana amarilla + textura normal (antes fallaba)'),
    (0, 0.9397, 0.0103, 0.1812, 'CASO REAL REPORTADO POR EL USUARIO'),
    (1, 0, 0, 0, 'banana 100% verde, perfecta'),
    (0, 0, 1, 0, 'banana 100% manchas'),
    (0, 0, 0, 1, 'banana max textura'),
    (0.0, 0.0001, 0.9999, 0.3393, 'BANANA PODRIDA/NEGRA (caso real reportado)'),
]
for x1, x2, x3, x4, desc in casos:
    xv = np.array([[x1, x2, x3, x4]])
    y_red, _, _, _ = forward_red(xv)
    y_dif = inferencia_fam(x1, x2, x3, x4)
    print(f"  {desc:50s} RN: V={y_red*5:.3f}  |  Difusa: V={y_dif*5:.3f}")
