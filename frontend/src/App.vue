<script setup>
import { ref, computed, onMounted } from 'vue'
import Chart from 'chart.js/auto'

const API_URL = 'http://192.168.100.6:8000'

// Trazos de iconos estilo Material (un solo color via currentColor)
const ICONOS = {
  camara: 'M20,4H16.83L15,2H9L7.17,4H4A2,2 0 0,0 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V6A2,2 0 0,0 20,4M20,18H4V6H8.05L9.88,4H14.12L15.95,6H20V18M12,7A5,5 0 0,0 7,12A5,5 0 0,0 12,17A5,5 0 0,0 17,12A5,5 0 0,0 12,7M12,15A3,3 0 0,1 9,12A3,3 0 0,1 12,9A3,3 0 0,1 15,12A3,3 0 0,1 12,15Z',
  imagen: 'M19,19H5V5H19M19,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M13.96,12.29L11.21,15.83L9.25,13.47L6.5,17H17.5L13.96,12.29Z',
  grafica: 'M16,11.78L20.24,4.45L21.97,5.45L16.74,14.5L10.23,10.75L5.46,19H22V21H2V3H4V17.54L9.5,8L16,11.78Z',
  ajustes: 'M8 13C6.14 13 4.59 14.28 4.14 16H2V18H4.14C4.59 19.72 6.14 21 8 21S11.41 19.72 11.86 18H22V16H11.86C11.41 14.28 9.86 13 8 13M8 19C6.9 19 6 18.1 6 17C6 15.9 6.9 15 8 15S10 15.9 10 17C10 18.1 9.1 19 8 19M19.86 6C19.41 4.28 17.86 3 16 3S12.59 4.28 12.14 6H2V8H12.14C12.59 9.72 14.14 11 16 11S19.41 9.72 19.86 8H22V6H19.86M16 9C14.9 9 14 8.1 14 7C14 5.9 14.9 5 16 5S18 5.9 18 7C18 8.1 17.1 9 16 9Z',
  red: 'M19.5 17C19.36 17 19.24 17 19.11 17.04L17.5 13.8C17.95 13.35 18.25 12.71 18.25 12C18.25 10.62 17.13 9.5 15.75 9.5C15.61 9.5 15.5 9.5 15.35 9.54L13.74 6.3C14.21 5.84 14.5 5.21 14.5 4.5C14.5 3.12 13.38 2 12 2S9.5 3.12 9.5 4.5C9.5 5.2 9.79 5.84 10.26 6.29L8.65 9.54C8.5 9.5 8.39 9.5 8.25 9.5C6.87 9.5 5.75 10.62 5.75 12C5.75 12.71 6.04 13.34 6.5 13.79L4.89 17.04C4.76 17 4.64 17 4.5 17C3.12 17 2 18.12 2 19.5C2 20.88 3.12 22 4.5 22S7 20.88 7 19.5C7 18.8 6.71 18.16 6.24 17.71L7.86 14.46C8 14.5 8.12 14.5 8.25 14.5C8.38 14.5 8.5 14.5 8.63 14.46L10.26 17.71C9.79 18.16 9.5 18.8 9.5 19.5C9.5 20.88 10.62 22 12 22S14.5 20.88 14.5 19.5C14.5 18.12 13.38 17 12 17C11.87 17 11.74 17 11.61 17.04L10 13.8C10.45 13.35 10.75 12.71 10.75 12C10.75 11.3 10.46 10.67 10 10.21L11.61 6.96C11.74 7 11.87 7 12 7C12.13 7 12.26 7 12.39 6.96L14 10.21C13.54 10.66 13.25 11.3 13.25 12C13.25 13.38 14.37 14.5 15.75 14.5C15.88 14.5 16 14.5 16.13 14.46L17.76 17.71C17.29 18.16 17 18.8 17 19.5C17 20.88 18.12 22 19.5 22S22 20.88 22 19.5C22 18.12 20.88 17 19.5 17M4.5 20.5C3.95 20.5 3.5 20.05 3.5 19.5S3.95 18.5 4.5 18.5 5.5 18.95 5.5 19.5 5.05 20.5 4.5 20.5M13 19.5C13 20.05 12.55 20.5 12 20.5S11 20.05 11 19.5 11.45 18.5 12 18.5 13 18.95 13 19.5M7.25 12C7.25 11.45 7.7 11 8.25 11S9.25 11.45 9.25 12 8.8 13 8.25 13 7.25 12.55 7.25 12M11 4.5C11 3.95 11.45 3.5 12 3.5S13 3.95 13 4.5 12.55 5.5 12 5.5 11 5.05 11 4.5M14.75 12C14.75 11.45 15.2 11 15.75 11S16.75 11.45 16.75 12 16.3 13 15.75 13 14.75 12.55 14.75 12M19.5 20.5C18.95 20.5 18.5 20.05 18.5 19.5S18.95 18.5 19.5 18.5 20.5 18.95 20.5 19.5 20.05 20.5 19.5 20.5Z',
  difusa: 'M14,8.5A1.5,1.5 0 0,0 12.5,10A1.5,1.5 0 0,0 14,11.5A1.5,1.5 0 0,0 15.5,10A1.5,1.5 0 0,0 14,8.5M14,12.5A1.5,1.5 0 0,0 12.5,14A1.5,1.5 0 0,0 14,15.5A1.5,1.5 0 0,0 15.5,14A1.5,1.5 0 0,0 14,12.5M10,17A1,1 0 0,0 9,18A1,1 0 0,0 10,19A1,1 0 0,0 11,18A1,1 0 0,0 10,17M10,8.5A1.5,1.5 0 0,0 8.5,10A1.5,1.5 0 0,0 10,11.5A1.5,1.5 0 0,0 11.5,10A1.5,1.5 0 0,0 10,8.5M18,5A1,1 0 0,0 17,6A1,1 0 0,0 18,7A1,1 0 0,0 19,6A1,1 0 0,0 18,5M18,9A1,1 0 0,0 17,10A1,1 0 0,0 18,11A1,1 0 0,0 19,10A1,1 0 0,0 18,9M18,17A1,1 0 0,0 17,18A1,1 0 0,0 18,19A1,1 0 0,0 19,18A1,1 0 0,0 18,17M18,13A1,1 0 0,0 17,14A1,1 0 0,0 18,15A1,1 0 0,0 19,14A1,1 0 0,0 18,13M10,12.5A1.5,1.5 0 0,0 8.5,14A1.5,1.5 0 0,0 10,15.5A1.5,1.5 0 0,0 11.5,14A1.5,1.5 0 0,0 10,12.5M10,7A1,1 0 0,0 11,6A1,1 0 0,0 10,5A1,1 0 0,0 9,6A1,1 0 0,0 10,7M6,5A1,1 0 0,0 5,6A1,1 0 0,0 6,7A1,1 0 0,0 7,6A1,1 0 0,0 6,5M6,9A1,1 0 0,0 5,10A1,1 0 0,0 6,11A1,1 0 0,0 7,10A1,1 0 0,0 6,9M6,17A1,1 0 0,0 5,18A1,1 0 0,0 6,19A1,1 0 0,0 7,18A1,1 0 0,0 6,17M6,13A1,1 0 0,0 5,14A1,1 0 0,0 6,15A1,1 0 0,0 7,14A1,1 0 0,0 6,13Z',
  check: 'M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M12 20C7.59 20 4 16.41 4 12S7.59 4 12 4 20 7.59 20 12 16.41 20 12 20M16.59 7.58L10 14.17L7.41 11.59L6 13L10 17L18 9L16.59 7.58Z',
  hoja: 'M17,8C8,10 5.9,16.17 3.82,21.34L5.71,22L6.66,19.7C7.14,19.87 7.64,20 8,20C19,20 22,3 22,3C21,5 14,5.25 9,6.25C4,7.25 2,11.5 2,13.5C2,15.5 3.75,17.25 3.75,17.25C7,8 17,8 17,8Z',
  alerta: 'M13,14H11V9H13M13,18H11V16H13M1,21H23L12,2L1,21Z'
}

const fotoPreview = ref(null)
const mascaraPreview = ref(null)
const cargando = ref(false)
const resultado = ref(null)
const voltajeObjetivo = ref(2.25)
const mensajeCalibracion = ref('')

const canvasEntradas = ref(null)
const canvasSalidas = ref(null)
let chartEntradas = null
let chartSalidas = null
const historialLabels = []

// Paleta clara y coherente con el resto de la interfaz
const COLOR_VERDE = '#22c55e'
const COLOR_AMARILLO = '#f5b400'
const COLOR_GRIS = '#94a3b8'
const COLOR_MORADO = '#8b5cf6'
const COLOR_TEXTO_SUAVE = '#6b7280'
const COLOR_REJILLA = '#eef0f6'

onMounted(() => {
  chartEntradas = new Chart(canvasEntradas.value, {
    type: 'line',
    data: {
      labels: historialLabels,
      datasets: [
        { label: 'Verde', data: [], borderColor: COLOR_VERDE, backgroundColor: COLOR_VERDE + '22', tension: 0.35, fill: true, pointRadius: 2, borderWidth: 2 },
        { label: 'Amarillo', data: [], borderColor: COLOR_AMARILLO, backgroundColor: COLOR_AMARILLO + '22', tension: 0.35, fill: true, pointRadius: 2, borderWidth: 2 },
        { label: 'Manchas', data: [], borderColor: COLOR_GRIS, backgroundColor: COLOR_GRIS + '15', tension: 0.35, fill: true, pointRadius: 2, borderWidth: 2 },
        { label: 'Textura', data: [], borderColor: COLOR_MORADO, backgroundColor: COLOR_MORADO + '15', tension: 0.35, fill: true, pointRadius: 2, borderWidth: 2 }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: { min: 0, max: 1, ticks: { color: COLOR_TEXTO_SUAVE }, grid: { color: COLOR_REJILLA } },
        x: { ticks: { color: COLOR_TEXTO_SUAVE }, grid: { display: false } }
      },
      plugins: { legend: { position: 'bottom', labels: { color: COLOR_TEXTO_SUAVE, boxWidth: 10, usePointStyle: true, padding: 14 } } }
    }
  })

  chartSalidas = new Chart(canvasSalidas.value, {
    type: 'line',
    data: {
      labels: historialLabels,
      datasets: [
        { label: 'Red neuronal', data: [], borderColor: COLOR_MORADO, backgroundColor: COLOR_MORADO + '20', borderWidth: 3, tension: 0.35, fill: true, pointRadius: 3 },
        { label: 'Lógica difusa', data: [], borderColor: COLOR_AMARILLO, backgroundColor: 'transparent', borderDash: [6, 4], borderWidth: 2, tension: 0.35, pointRadius: 3 }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: { min: 0, max: 5, ticks: { color: COLOR_TEXTO_SUAVE }, grid: { color: COLOR_REJILLA } },
        x: { ticks: { color: COLOR_TEXTO_SUAVE }, grid: { display: false } }
      },
      plugins: { legend: { position: 'bottom', labels: { color: COLOR_TEXTO_SUAVE, boxWidth: 10, usePointStyle: true, padding: 14 } } }
    }
  })
})

// Info de estado (texto y color) segun el voltaje, totalmente en espanol
const estadoInfo = (voltaje) => {
  if (voltaje < 1.35) return { texto: 'Inmadura', color: '#16a34a', fondo: '#ecfdf3' }
  if (voltaje < 2.65) return { texto: 'Óptima', color: '#ca8a04', fondo: '#fef9ec' }
  if (voltaje < 3.85) return { texto: 'Sobremadura', color: '#ea580c', fondo: '#fff3ec' }
  return { texto: 'Dañada', color: '#dc2626', fondo: '#fef0f0' }
}

const estadoRed = computed(() => resultado.value ? estadoInfo(resultado.value.red_neuronal.voltaje) : null)
const estadoDifusa = computed(() => resultado.value ? estadoInfo(resultado.value.logica_difusa.voltaje) : null)

const procesarFoto = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  fotoPreview.value = URL.createObjectURL(file)
  cargando.value = true
  mensajeCalibracion.value = ''

  const formData = new FormData()
  formData.append('file', file)

  // Evita que la UI se quede "colgada" para siempre si el backend no responde
  // (ej. firewall bloqueando el puerto, uvicorn caído o escuchando solo en localhost).
  const controlador = new AbortController()
  const timeoutId = setTimeout(() => controlador.abort(), 20000)

  try {
    const res = await fetch(`${API_URL}/analizar`, {
      method: 'POST',
      body: formData,
      signal: controlador.signal
    })

    if (!res.ok) {
      let detalle = `Error HTTP ${res.status}`
      try {
        const errData = await res.json()
        if (errData.detail) detalle = errData.detail
      } catch (_) { /* respuesta sin JSON válido */ }
      throw new Error(detalle)
    }

    const data = await res.json()
    resultado.value = data
    mascaraPreview.value = data.mascara_b64

    const hora = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    historialLabels.push(hora)

    chartEntradas.data.datasets[0].data.push(data.entradas.x1)
    chartEntradas.data.datasets[1].data.push(data.entradas.x2)
    chartEntradas.data.datasets[2].data.push(data.entradas.x3)
    chartEntradas.data.datasets[3].data.push(data.entradas.x4)
    chartEntradas.update()

    chartSalidas.data.datasets[0].data.push(data.red_neuronal.voltaje)
    chartSalidas.data.datasets[1].data.push(data.logica_difusa.voltaje)
    chartSalidas.update()
  } catch (err) {
    if (err.name === 'AbortError') {
      alert(`Tiempo de espera agotado (20s) conectando a ${API_URL}. Verifica que uvicorn esté corriendo con --host 0.0.0.0 y que el firewall de Windows permita el puerto 8000 en el perfil de red actual.`)
    } else if (err instanceof TypeError) {
      alert(`No se pudo conectar con ${API_URL}. Verifica que uvicorn siga corriendo, que el celular esté en la misma red Wi-Fi y que el firewall de Windows no bloquee el puerto 8000.`)
    } else {
      alert(`El servidor respondió con un error: ${err.message}`)
    }
  } finally {
    clearTimeout(timeoutId)
    cargando.value = false
  }
}

const recalibrarEnVivo = async () => {
  if (!resultado.value) return
  const form = new FormData()
  form.append('x1', resultado.value.entradas.x1)
  form.append('x2', resultado.value.entradas.x2)
  form.append('x3', resultado.value.entradas.x3)
  form.append('x4', resultado.value.entradas.x4)
  form.append('y_objetivo', voltajeObjetivo.value / 5.0)

  await fetch(`${API_URL}/actualizar`, { method: 'POST', body: form })
  mensajeCalibracion.value = `Pesos actualizados hacia ${voltajeObjetivo.value} V`
}
</script>

<template>
  <div class="app-container">
    <header class="app-bar">
      <div class="logo-badge">
        <svg viewBox="0 0 24 24" class="icono"><path :d="ICONOS.hoja" /></svg>
      </div>
      <div>
        <h1>BananaIA</h1>
        <p>Analizador de madurez por imagen</p>
      </div>
    </header>

    <div class="acciones-grid">
      <label class="accion-tile">
        <span class="accion-icono camara">
          <svg viewBox="0 0 24 24" class="icono"><path :d="ICONOS.camara" /></svg>
        </span>
        <span class="accion-texto">Tomar foto</span>
        <input type="file" accept="image/*" capture="environment" @change="procesarFoto" hidden />
      </label>

      <label class="accion-tile">
        <span class="accion-icono galeria">
          <svg viewBox="0 0 24 24" class="icono"><path :d="ICONOS.imagen" /></svg>
        </span>
        <span class="accion-texto">Subir foto</span>
        <input type="file" accept="image/*" @change="procesarFoto" hidden />
      </label>
    </div>

    <div v-if="cargando" class="status-card">
      <div class="barra-progreso-indet"><span></span></div>
      <p>Analizando imagen y calculando señales…</p>
    </div>

    <div v-if="fotoPreview" class="grid-imagenes">
      <div class="card-img">
        <span>Captura</span>
        <img :src="fotoPreview" />
      </div>
      <div class="card-img" v-if="mascaraPreview">
        <span>Silueta detectada</span>
        <img :src="mascaraPreview" />
      </div>
    </div>

    <div v-if="resultado" class="resultados-grid">
      <div class="metric-card rn">
        <div class="metric-top">
          <svg viewBox="0 0 24 24" class="icono"><path :d="ICONOS.red" /></svg>
          <span class="metric-badge" :style="{ color: estadoRed.color, background: estadoRed.fondo }">{{ estadoRed.texto }}</span>
        </div>
        <div class="voltaje">{{ resultado.red_neuronal.voltaje }} <small>V</small></div>
        <p class="metric-nombre">Red neuronal</p>
        <div class="gauge"><div class="gauge-relleno rn-fill" :style="{ width: Math.min(100, resultado.red_neuronal.voltaje / 5 * 100) + '%' }"></div></div>
      </div>
      <div class="metric-card difusa">
        <div class="metric-top">
          <svg viewBox="0 0 24 24" class="icono"><path :d="ICONOS.difusa" /></svg>
          <span class="metric-badge" :style="{ color: estadoDifusa.color, background: estadoDifusa.fondo }">{{ estadoDifusa.texto }}</span>
        </div>
        <div class="voltaje">{{ resultado.logica_difusa.voltaje }} <small>V</small></div>
        <p class="metric-nombre">Lógica difusa</p>
        <div class="gauge"><div class="gauge-relleno difusa-fill" :style="{ width: Math.min(100, resultado.logica_difusa.voltaje / 5 * 100) + '%' }"></div></div>
      </div>
    </div>

    <div v-if="resultado" class="entradas-card">
      <h4>Señales detectadas en la fruta</h4>
      <div class="entrada-linea">
        <div class="entrada-etiqueta"><span class="punto verde"></span>Verde</div>
        <div class="barra-fondo"><div class="barra-relleno verde" :style="{ width: resultado.entradas.x1 * 100 + '%' }"></div></div>
        <span class="entrada-valor">{{ Math.round(resultado.entradas.x1 * 100) }}%</span>
      </div>
      <div class="entrada-linea">
        <div class="entrada-etiqueta"><span class="punto amarillo"></span>Amarillo</div>
        <div class="barra-fondo"><div class="barra-relleno amarillo" :style="{ width: resultado.entradas.x2 * 100 + '%' }"></div></div>
        <span class="entrada-valor">{{ Math.round(resultado.entradas.x2 * 100) }}%</span>
      </div>
      <div class="entrada-linea">
        <div class="entrada-etiqueta"><span class="punto gris"></span>Manchas</div>
        <div class="barra-fondo"><div class="barra-relleno gris" :style="{ width: resultado.entradas.x3 * 100 + '%' }"></div></div>
        <span class="entrada-valor">{{ Math.round(resultado.entradas.x3 * 100) }}%</span>
      </div>
      <div class="entrada-linea">
        <div class="entrada-etiqueta"><span class="punto morado"></span>Textura</div>
        <div class="barra-fondo"><div class="barra-relleno morado" :style="{ width: resultado.entradas.x4 * 100 + '%' }"></div></div>
        <span class="entrada-valor">{{ Math.round(resultado.entradas.x4 * 100) }}%</span>
      </div>
    </div>

    <div class="chart-box">
      <h4><svg viewBox="0 0 24 24" class="icono chico"><path :d="ICONOS.grafica" /></svg>Historial de señales</h4>
      <canvas ref="canvasEntradas"></canvas>
    </div>

    <div class="chart-box">
      <h4><svg viewBox="0 0 24 24" class="icono chico"><path :d="ICONOS.grafica" /></svg>Historial de voltajes</h4>
      <canvas ref="canvasSalidas"></canvas>
    </div>

    <div v-if="resultado" class="panel-update">
      <h4><svg viewBox="0 0 24 24" class="icono chico"><path :d="ICONOS.ajustes" /></svg>Ajuste manual de la red</h4>
      <label>Voltaje objetivo: <strong>{{ voltajeObjetivo }} V</strong></label>
      <input type="range" min="0.5" max="4.75" step="0.05" v-model="voltajeObjetivo" />
      <button @click="recalibrarEnVivo">Actualizar con esta muestra</button>
      <p v-if="mensajeCalibracion" class="ok-msg">
        <svg viewBox="0 0 24 24" class="icono chico"><path :d="ICONOS.check" /></svg>
        {{ mensajeCalibracion }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 1.25rem 1.1rem 2.5rem;
  min-height: 100vh;
  background: linear-gradient(160deg, #fffaf0 0%, #f4f6fb 45%, #eef1fb 100%);
}

/* --- Encabezado --- */
.app-bar {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1.4rem;
}
.logo-badge {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: linear-gradient(135deg, #ffd54a 0%, #8bc34a 100%);
  box-shadow: 0 6px 16px rgba(245, 180, 0, 0.35);
}
.logo-badge .icono { width: 24px; height: 24px; color: #ffffff; }
.app-bar h1 {
  font-size: 1.35rem;
  color: #1f2430;
  font-weight: 800;
  letter-spacing: -0.3px;
}
.app-bar p {
  color: #8b8fa3;
  font-size: 0.82rem;
  margin-top: 0.1rem;
}

/* --- Iconos genéricos --- */
.icono { width: 22px; height: 22px; fill: currentColor; }
.icono.chico { width: 17px; height: 17px; margin-right: 0.4rem; vertical-align: -3px; }

/* --- Acciones (tomar / subir foto) --- */
.acciones-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
  margin-bottom: 1.1rem;
}
.accion-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  padding: 1.1rem 0.6rem;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 10px 25px rgba(31, 36, 48, 0.06);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.accion-tile:active {
  transform: scale(0.97);
}
.accion-icono {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}
.accion-icono .icono { width: 24px; height: 24px; }
.accion-icono.camara { background: linear-gradient(135deg, #ffb703, #ff7a3d); }
.accion-icono.galeria { background: linear-gradient(135deg, #22c55e, #0ea5a4); }
.accion-texto {
  font-weight: 600;
  font-size: 0.88rem;
  color: #343a46;
}

/* --- Estado de carga --- */
.status-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 1rem 1.1rem;
  margin-bottom: 1.1rem;
  box-shadow: 0 10px 25px rgba(31, 36, 48, 0.06);
  text-align: center;
}
.status-card p {
  color: #6b7280;
  font-size: 0.85rem;
  margin-top: 0.6rem;
}
.barra-progreso-indet {
  height: 6px;
  border-radius: 999px;
  background: #f0f1f6;
  overflow: hidden;
  position: relative;
}
.barra-progreso-indet span {
  position: absolute;
  inset: 0;
  width: 40%;
  border-radius: 999px;
  background: linear-gradient(90deg, #ffd54a, #8bc34a);
  animation: deslizar 1.1s ease-in-out infinite;
}
@keyframes deslizar {
  0% { left: -40%; }
  100% { left: 100%; }
}

/* --- Imágenes --- */
.grid-imagenes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1.1rem;
}
.card-img {
  background: #ffffff;
  padding: 0.6rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 10px 25px rgba(31, 36, 48, 0.06);
}
.card-img span {
  display: block;
  font-size: 0.72rem;
  font-weight: 600;
  color: #8b8fa3;
  margin-bottom: 0.45rem;
}
.card-img img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 10px;
  background: #f4f6fb;
}

/* --- Tarjetas de resultado --- */
.resultados-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
  margin-bottom: 1.1rem;
}
.metric-card {
  padding: 1rem;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 10px 25px rgba(31, 36, 48, 0.06);
}
.metric-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.6rem;
}
.metric-top .icono { color: #a1a6b8; width: 20px; height: 20px; }
.metric-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.22rem 0.55rem;
  border-radius: 999px;
}
.metric-card .voltaje {
  font-size: 1.6rem;
  font-weight: 800;
  color: #1f2430;
  line-height: 1;
}
.metric-card .voltaje small {
  font-size: 0.85rem;
  font-weight: 600;
  color: #8b8fa3;
}
.metric-nombre {
  color: #8b8fa3;
  font-size: 0.75rem;
  font-weight: 600;
  margin: 0.25rem 0 0.6rem;
}
.gauge {
  height: 6px;
  border-radius: 999px;
  background: #f0f1f6;
  overflow: hidden;
}
.gauge-relleno {
  height: 100%;
  border-radius: 999px;
}
.rn-fill { background: linear-gradient(90deg, #8b5cf6, #c084fc); }
.difusa-fill { background: linear-gradient(90deg, #f5b400, #ffd54a); }

/* --- Entradas analógicas --- */
.entradas-card {
  background: #ffffff;
  padding: 1rem 1.1rem;
  border-radius: 18px;
  margin-bottom: 1.1rem;
  box-shadow: 0 10px 25px rgba(31, 36, 48, 0.06);
}
.entradas-card h4 {
  font-size: 0.85rem;
  color: #1f2430;
  margin-bottom: 0.8rem;
  font-weight: 700;
}
.entrada-linea {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.65rem;
}
.entrada-linea:last-child { margin-bottom: 0; }
.entrada-etiqueta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: 86px;
  flex-shrink: 0;
  font-size: 0.78rem;
  color: #4b5160;
  font-weight: 600;
}
.punto {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}
.punto.verde { background: #22c55e; }
.punto.amarillo { background: #f5b400; }
.punto.gris { background: #94a3b8; }
.punto.morado { background: #8b5cf6; }
.barra-fondo {
  flex: 1;
  height: 8px;
  border-radius: 999px;
  background: #f0f1f6;
  overflow: hidden;
}
.barra-relleno {
  height: 100%;
  border-radius: 999px;
}
.barra-relleno.verde { background: #22c55e; }
.barra-relleno.amarillo { background: #f5b400; }
.barra-relleno.gris { background: #94a3b8; }
.barra-relleno.morado { background: #8b5cf6; }
.entrada-valor {
  width: 38px;
  text-align: right;
  font-size: 0.78rem;
  font-weight: 700;
  color: #1f2430;
  flex-shrink: 0;
}

/* --- Gráficas --- */
.chart-box {
  background: #ffffff;
  padding: 1rem 1.1rem;
  border-radius: 18px;
  margin-bottom: 1.1rem;
  box-shadow: 0 10px 25px rgba(31, 36, 48, 0.06);
}
.chart-box h4 {
  display: flex;
  align-items: center;
  margin-bottom: 0.7rem;
  font-size: 0.85rem;
  color: #1f2430;
  font-weight: 700;
}
.chart-box h4 .icono { color: #8b8fa3; }

/* --- Panel de ajuste manual --- */
.panel-update {
  background: #ffffff;
  padding: 1.1rem;
  border-radius: 18px;
  box-shadow: 0 10px 25px rgba(31, 36, 48, 0.06);
}
.panel-update h4 {
  display: flex;
  align-items: center;
  margin-bottom: 0.7rem;
  color: #1f2430;
  font-size: 0.88rem;
  font-weight: 700;
}
.panel-update h4 .icono { color: #8b8fa3; }
.panel-update label {
  font-size: 0.82rem;
  color: #6b7280;
}
.panel-update label strong { color: #1f2430; }
.panel-update input[type="range"] {
  width: 100%;
  margin: 0.7rem 0 0.9rem;
  accent-color: #f5b400;
}
.panel-update button {
  width: 100%;
  padding: 0.8rem;
  background: linear-gradient(135deg, #ffd54a, #ff9f43);
  color: #1f2430;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(255, 159, 67, 0.35);
}
.panel-update button:active { transform: scale(0.98); }
.ok-msg {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #16a34a;
  font-size: 0.82rem;
  font-weight: 600;
  margin-top: 0.7rem;
}
.ok-msg .icono { color: #16a34a; }
</style>