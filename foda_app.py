"""
FODA / SWOT Cuestionario Interactivo
- Recopila F, D, O, A del usuario
- Cruza F1xO1, F2xO2, F3xO3 con IA (Google Gemini API)
- Guarda todo en Google Sheets
"""

import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import time
from datetime import datetime
import os

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE LA PÁGINA (Debe ser el primer comando)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Diagnóstico FODA",
    page_icon="🔍",
    layout="centered"
)

# ─────────────────────────────────────────────
# CONSTANTES Y CREDENCIALES – Edita estos valores
# ─────────────────────────────────────────────
# ⚠️ Reemplaza "TU_API_KEY_AQUI" con tu token real de Google AI Studio
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 

GOOGLE_SHEET_NAME = "1XB5A222mk9a5olSPQTwn-Nm3uLjp62OvKMQu_KzrYo0"          
WORKSHEET_NAME    = "Respuestas"                                          
HEADERS = [
    "Timestamp",
    "Fortaleza 1", "Fortaleza 2", "Fortaleza 3",
    "Debilidad 1", "Debilidad 2", "Debilidad 3",
    "Oportunidad 1", "Oportunidad 2", "Oportunidad 3",
    "Amenaza 1", "Amenaza 2", "Amenaza 3",
    "Estrategia FO1 (F1xO1)", "Estrategia FO2 (F2xO2)", "Estrategia FO3 (F3xO3)",
    "Estrategia FA1 (F1xA1)", "Estrategia FA2 (F2xA2)", "Estrategia FA3 (F3xA3)",
]

# Configurar la API de Gemini globalmente
genai.configure(api_key=GEMINI_API_KEY)

# ─────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { max-width: 780px; }
    .stTextArea textarea { font-size: 15px; }
    .resultado-box {
        background: #e8f5e9;
        border-left: 5px solid #2e7d32;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-top: 0.8rem;
        color: #1b5e20; /* Color de texto oscuro para que se lea en Dark Mode */
    }
    h1 { color: #8c9eff; } /* Azul claro para contrastar con fondo oscuro */
    h3 { color: #8c9eff; } /* Azul claro para contrastar con fondo oscuro */
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────
@st.cache_resource
def get_gsheet_client():
    """Conecta con Google Sheets usando la cuenta de servicio."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        creds  = ServiceAccountCredentials.from_json_keyfile_name("desarrollo.json", scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"❌ Error conectando con Google Sheets. Verifica que '{SERVICE_ACCOUNT_JSON}' exista. Detalle: {e}")
        return None

def ensure_headers(worksheet):
    """Inserta fila de encabezados si la hoja está vacía."""
    existing = worksheet.row_values(1)
    if not existing:
        worksheet.append_row(HEADERS)

def guardar_en_sheets(datos: dict):
    """Escribe una fila en Google Sheets."""
    client = get_gsheet_client()
    if client is None:
        return False
    try:
        sh = client.open_by_key(GOOGLE_SHEET_NAME)
        ws = sh.worksheet(WORKSHEET_NAME)
        ensure_headers(ws)
        fila = [datos.get(col, "") for col in HEADERS]
        ws.append_row(fila)
        return True
    except Exception as e:
        st.error(f"❌ Error guardando en Google Sheets: {e}")
        return False

def cruzar_con_ia(fortaleza: str, contraparte: str, tipo: str) -> str:
    """Llama a la API de Google Gemini para generar la estrategia cruzada."""
    if tipo == "oportunidad":
        instruccion = (
            f"Eres un consultor estratégico experto en análisis FODA. "
            f"Genera una estrategia ofensiva (FO) concisa (máximo 3 oraciones) "
            f"que potencie la siguiente FORTALEZA aprovechando la OPORTUNIDAD dada.\n\n"
            f"FORTALEZA: {fortaleza}\n"
            f"OPORTUNIDAD: {contraparte}\n\n"
            f"Responde solo la estrategia, sin encabezados ni bullets."
        )
    else:
        instruccion = (
            f"Eres un consultor estratégico experto en análisis FODA. "
            f"Genera una estrategia defensiva (FA) concisa (máximo 3 oraciones) "
            f"que use la FORTALEZA para contrarrestar la AMENAZA dada.\n\n"
            f"FORTALEZA: {fortaleza}\n"
            f"AMENAZA: {contraparte}\n\n"
            f"Responde solo la estrategia, sin encabezados ni bullets."
        )
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(instruccion)
        return response.text.strip()
    except Exception as e:
        return f"[Error al generar estrategia: {e}]"

# ─────────────────────────────────────────────
# UI PRINCIPAL
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Información")
    st.info("El análisis impulsado por IA está activo y configurado automáticamente.")
    st.markdown("**📋 Modelo:** `gemini-2.5-flash`")

st.title("🔍 Diagnóstico FODA")
st.markdown("Completa las **3 entradas** de cada cuadrante. Al finalizar, la IA generará las estrategias de cruce y los resultados se guardarán automáticamente en Google Sheets.")
st.divider()

# ── Paso 1: FORTALEZAS ──────────────────────
st.markdown("### 💪 Fortalezas internas")
f1 = st.text_area("Fortaleza 1", placeholder="Ej. Equipo comprometido y con experiencia", key="f1", height=90)
f2 = st.text_area("Fortaleza 2", placeholder="Ej. Infraestructura propia y en buen estado", key="f2", height=90)
f3 = st.text_area("Fortaleza 3", placeholder="Ej. Red de alianzas con instituciones clave", key="f3", height=90)
st.divider()

# ── Paso 2: DEBILIDADES ─────────────────────
st.markdown("### ⚠️ Debilidades internas")
d1 = st.text_area("Debilidad 1", placeholder="Ej. Recursos financieros limitados", key="d1", height=90)
d2 = st.text_area("Debilidad 2", placeholder="Ej. Alta rotación de personal voluntario", key="d2", height=90)
d3 = st.text_area("Debilidad 3", placeholder="Ej. Poca presencia en redes sociales", key="d3", height=90)
st.divider()

# ── Paso 3: OPORTUNIDADES ───────────────────
st.markdown("### 🌱 Oportunidades externas")
o1 = st.text_area("Oportunidad 1", placeholder="Ej. Nuevos fondos gubernamentales", key="o1", height=90)
o2 = st.text_area("Oportunidad 2", placeholder="Ej. Creciente interés ciudadano en el sector", key="o2", height=90)
o3 = st.text_area("Oportunidad 3", placeholder="Ej. Plataformas digitales para ampliar alcance", key="o3", height=90)
st.divider()

# ── Paso 4: AMENAZAS ────────────────────────
st.markdown("### 🚨 Amenazas externas")
a1 = st.text_area("Amenaza 1", placeholder="Ej. Recortes en presupuesto público", key="a1", height=90)
a2 = st.text_area("Amenaza 2", placeholder="Ej. Competencia de otras organizaciones", key="a2", height=90)
a3 = st.text_area("Amenaza 3", placeholder="Ej. Cambios en la normativa legal", key="a3", height=90)
st.divider()

# ── Validación y Botón de envío ──────────────
campos = {
    "f": [f1, f2, f3], "d": [d1, d2, d3],
    "o": [o1, o2, o3], "a": [a1, a2, a3]
}
todos_llenos = all(v.strip() for grupo in campos.values() for v in grupo)

if not todos_llenos:
    st.info("📝 Completa todos los campos para habilitar el análisis.")

boton = st.button(
    "🚀 Generar análisis FODA y guardar",
    disabled=not todos_llenos,
    use_container_width=True,
    type="primary"
)

if boton:
    with st.spinner("⏳ Generando estrategias con IA..."):
        pares_fo = [(f1, o1), (f2, o2), (f3, o3)]
        pares_fa = [(f1, a1), (f2, a2), (f3, a3)]

        estrategias_fo = []
        estrategias_fa = []

        barra = st.progress(0, text="Analizando cruces...")
        
        for i, (f, o) in enumerate(pares_fo):
            estrategias_fo.append(cruzar_con_ia(f, o, "oportunidad"))
            barra.progress((i + 1) / 6, text=f"Cruce FO{i+1} listo…")
            time.sleep(0.3)

        for i, (f, a) in enumerate(pares_fa):
            estrategias_fa.append(cruzar_con_ia(f, a, "amenaza"))
            barra.progress((3 + i + 1) / 6, text=f"Cruce FA{i+1} listo…")
            time.sleep(0.3)

        barra.progress(1.0, text="✅ Análisis completo")

    # ── Mostrar resultados ───────────────────
    st.success("✅ Análisis completado")
    st.markdown("---")
    st.markdown("## 📊 Resultados de cruces estratégicos")

    # FO – Estrategias Ofensivas
    st.markdown("### 🟢 Estrategias Ofensivas (Fortaleza × Oportunidad)")
    for i, (f, o, est) in enumerate(zip([f1,f2,f3], [o1,o2,o3], estrategias_fo), 1):
        with st.expander(f"FO{i} — Fortaleza {i} × Oportunidad {i}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**💪 Fortaleza {i}**\n\n{f}")
            with col2:
                st.markdown(f"**🌱 Oportunidad {i}**\n\n{o}")
            st.markdown("**🤖 Estrategia generada:**")
            st.markdown(f'<div class="resultado-box">{est}</div>', unsafe_allow_html=True)

    # FA – Estrategias Defensivas
    st.markdown("### 🔴 Estrategias Defensivas (Fortaleza × Amenaza)")
    for i, (f, a, est) in enumerate(zip([f1,f2,f3], [a1,a2,a3], estrategias_fa), 1):
        with st.expander(f"FA{i} — Fortaleza {i} × Amenaza {i}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**💪 Fortaleza {i}**\n\n{f}")
            with col2:
                st.markdown(f"**🚨 Amenaza {i}**\n\n{a}")
            st.markdown("**🤖 Estrategia generada:**")
            st.markdown(f'<div class="resultado-box">{est}</div>', unsafe_allow_html=True)

    # ── Guardar en Google Sheets ─────────────
    datos = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Fortaleza 1": f1, "Fortaleza 2": f2, "Fortaleza 3": f3,
        "Debilidad 1": d1, "Debilidad 2": d2, "Debilidad 3": d3,
        "Oportunidad 1": o1, "Oportunidad 2": o2, "Oportunidad 3": o3,
        "Amenaza 1": a1, "Amenaza 2": a2, "Amenaza 3": a3,
        "Estrategia FO1 (F1xO1)": estrategias_fo[0],
        "Estrategia FO2 (F2xO2)": estrategias_fo[1],
        "Estrategia FO3 (F3xO3)": estrategias_fo[2],
        "Estrategia FA1 (F1xA1)": estrategias_fa[0],
        "Estrategia FA2 (F2xA2)": estrategias_fa[1],
        "Estrategia FA3 (F3xA3)": estrategias_fa[2],
    }

    with st.spinner("💾 Guardando en Google Sheets..."):
        ok = guardar_en_sheets(datos)

    if ok:
        st.success("✅ Respuestas guardadas con éxito en Google Sheets.")
    else:
        st.warning("⚠️ Los resultados se mostraron correctamente pero no se pudieron guardar en Google Sheets. Revisa la configuración de credenciales.")
