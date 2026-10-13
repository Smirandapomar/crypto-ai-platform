import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Configuración de márgenes estándar
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Estilos de fuente base
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)
font.color.rgb = RGBColor(0x33, 0x33, 0x33)

# Título Principal
title = doc.add_heading(level=1)
run_title = title.add_run("ANEXO TÉCNICO COMPLETO: DESARROLLO DEL PROTOTIPO (MVP), ARQUITECTURA WEB3 Y VALIDACIÓN CUANTITATIVA")
run_title.font.name = 'Calibri'
run_title.font.size = Pt(15)
run_title.font.bold = True
run_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

p_meta = doc.add_paragraph()
p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_meta = p_meta.add_run("Proyecto: Plataforma de Inversión en Criptomonedas Asistida por Inteligencia Artificial\nAutor: Samuel David Miranda Pomar | UNINPAHU | Ingeniería de Software")
r_meta.font.size = Pt(9.5)
r_meta.font.italic = True
r_meta.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

doc.add_paragraph().paragraph_format.space_after = Pt(4)

# Introducción
p_intro = doc.add_paragraph(
    "El presente informe consolida los avances técnicos y metodológicos alcanzados en la fase de prototipado funcional (MVP). "
    "Se detalla la implementación integral del pipeline de datos de mercado, la ingeniería de características predictivas, el "
    "entrenamiento y calibración del modelo de Machine Learning, el motor de simulación cuantitativa con mitigación de riesgos, "
    "la ingesta de sentimiento de mercado y la arquitectura de interfaz institucional con conectividad Web3."
)
p_intro.paragraph_format.line_spacing = 1.15
p_intro.paragraph_format.space_after = Pt(8)

def add_custom_heading(text):
    h = doc.add_heading(text, level=2)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    for r in h.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x03, 0x7D, 0xD6)
    return h

def add_bullet(bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(3)
    r_bold = p.add_run(bold_prefix)
    r_bold.bold = True
    r_bold.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    p.add_run(text)

# 1. Pipeline de Datos
add_custom_heading("1. Ingesta y Estructuración de Datos Financieros")
add_bullet("Conexión con Exchange (CCXT): ", "Integración del protocolo CCXT para la ingesta directa de datos de mercado desde la API pública de Binance, garantizando trazabilidad y transparencia operativa.")
add_bullet("Corpus Histórico de Entrenamiento: ", "Descarga y estructuración de 2.160 registros horarios (90 días) para el par ETH/USDT, estructurados bajo el estándar internacional OHLCV (Open, High, Low, Close, Volume).")
add_bullet("Feed en Tiempo Real (/api/candles): ", "Construcción de un canal de datos dedicado para consultar las últimas 100 velas horarias y alimentar el renderizado dinámico del gráfico de precios.")

# 2. Feature Engineering
add_custom_heading("2. Ingeniería de Variables Cuantitativas (Feature Engineering)")
add_bullet("Indicadores de Impulso y Tendencia: ", "Implementación del Índice de Fuerza Relativa (RSI 14), Convergencia/Divergencia de Medias Móviles (MACD) y Cruce Exponencial de Medias (EMA 9 vs EMA 21).")
add_bullet("Volatilidad y Liquidez: ", "Cálculo del Average True Range (ATR 14) normalizado respecto al precio de cierre y Volume Surge (volumen relativo frente a su media de 20 periodos) para aislar movimientos con volumen real.")
add_bullet("Etiqueta Supervisada (Target): ", "Definición de una variable objetivo binaria con horizonte de 6 periodos que identifica apreciaciones sostenidas superiores al 1.2%, absorbiendo los costos operativos.")

# 3. Modelamiento y Calibración
add_custom_heading("3. Modelamiento Predictivo y Calibración Fuera de Muestra")
add_bullet("Algoritmo de Clasificación: ", "Selección de Random Forest Classifier (200 estimadores, profundidad máxima 5) por su resistencia al sobreajuste frente a series temporales con alta dispersión.")
add_bullet("Validación Cronológica Estricta: ", "Partición temporal (80% entrenamiento cronológico, 20% evaluación fuera de muestra) para erradicar el sesgo de anticipación (look-ahead bias) y la fuga de datos.")
add_bullet("Ponderación de Variables: ", "Submuestreo balanceado (balanced_subsample) para resolver la asimetría de señales. Importancia relativa obtenida: RSI (21.86%), ATR/Volatilidad (20.85%), Cruce EMA (18.56%), MACD Diff (15.46%) y Volume Surge (9.33%).")

# 4. Motor de Backtesting
add_custom_heading("4. Simulación Cuantitativa y Mitigación de Riesgos (Paper Trading)")
add_bullet("Fricción Financiera Real: ", "Deducción paramétrica de una comisión del 0.1% por operación de compra y venta (estándar Binance Spot).")
add_bullet("Gestión de Riesgo Dinámica por ATR: ", "Stop-Loss adaptativo fijado a 1.5x ATR y Take-Profit a 3.0x ATR, garantizando una relación matemática Beneficio/Riesgo de 2:1.")
add_bullet("Resultados de Rendimiento: ", "La estrategia alcanzó un Win Rate del 57.14% y un retorno neto del +8.24% en el conjunto de prueba, reduciendo drásticamente el tiempo de exposición al riesgo frente al Buy & Hold pasivo.")

# 5. Sentimiento de Mercado
add_custom_heading("5. Integración de Sentimiento y Psicología Colectiva (Fear & Greed)")
add_bullet("API de Sentimiento Global (/api/sentiment): ", "Conexión en caliente con el servicio de Alternative.me para consumir el Crypto Fear & Greed Index (0 a 100).")
add_bullet("Filtro Multifactorial: ", "Incorporación de la métrica de sentimiento como capa analítica para prevenir entradas impulsivas en estados de euforia o sobrecompra extrema.")

# 6. Despliegue Web e Integración Web3
add_custom_heading("6. Arquitectura Web3 y Dashboard Institucional")
add_bullet("Backend Asíncrono (FastAPI): ", "Microservicio de alto rendimiento con endpoints REST para inferencia predictiva (/api/live-signal), simulación de cartera (/api/simulate) y feed de velas.")
add_bullet("Gráfico Interactivo TradingView: ", "Integración de la librería Lightweight Charts de TradingView en el frontend, ofreciendo lectura técnica fluida y escalable con escala de volatilidad.")
add_bullet("Conectividad Web3 (MetaMask): ", "Módulo de autenticación descentralizada mediante detección del proveedor window.ethereum para sincronizar billeteras sin custodia.")
add_bullet("Diseño Institucional (MetaMask Portfolio Style): ", "Interfaz minimalista orientada a toma de decisiones financieras, con paleta sobria, tipografía corporativa y módulos formativos de mitigación de pérdidas.")

doc.save("Avance_Anteproyecto_IA_Crypto.docx")
print("-> Archivo 'Avance_Anteproyecto_IA_Crypto.docx' actualizado exitosamente con todos los modulos.")
