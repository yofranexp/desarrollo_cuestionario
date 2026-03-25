import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN EXACTA DE TU PROYECTO
# ─────────────────────────────────────────────
SERVICE_ACCOUNT_JSON = "/desarrollo.json"
GOOGLE_SHEET_KEY = "1XB5A222mk9a5olSPQTwn-Nm3uLjp62OvKMQu_KzrYo0"
WORKSHEET_NAME = "Respuestas"

st.title("🧪 Prueba Rápida de Sheets")
st.write("Usa esta página solo para confirmar que Easypanel puede escribir en tu Google Sheet.")
st.divider()

# 1. LA PREGUNTA DE PRUEBA
mensaje = st.text_input("Escribe un mensaje de prueba (ej. 'Hola desde Easypanel'):")

# 2. EL BOTÓN PARA HACER PUSH
if st.button("Enviar a Google Sheets 🚀", type="primary"):
    if not mensaje:
        st.warning("⚠️ Escribe algo en la caja de texto antes de enviar.")
    else:
        with st.spinner("Conectando con Google..."):
            try:
                # Intentar conectar con las credenciales
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
                creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_JSON, scopes=scopes)
                client = gspread.authorize(creds)
                
                # Buscar el documento y la pestaña
                sh = client.open_by_key(GOOGLE_SHEET_KEY)
                ws = sh.worksheet(WORKSHEET_NAME)
                
                # Crear la fila que vamos a guardar (Fecha + Mensaje)
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fila_nueva = [fecha_hora, mensaje]
                
                # Enviar los datos a la hoja
                ws.append_row(fila_nueva)
                
                # Mensaje de éxito
                st.success(f"✅ ¡Conexión perfecta! El mensaje '{mensaje}' ya debe estar en tu Google Sheet.")
                st.balloons()
                
            except FileNotFoundError:
                st.error("❌ Error: No se encuentra el archivo '/desarrollo.json' en el servidor.")
            except gspread.exceptions.SpreadsheetNotFound:
                st.error("❌ Error: El JSON funciona, pero el bot no tiene permiso para editar este Google Sheet. ¿Recordaste compartirle el documento al correo del bot?")
            except Exception as e:
                st.error(f"❌ Error inesperado: {e}")
