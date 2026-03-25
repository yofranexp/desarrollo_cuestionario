import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import time
from datetime import datetime
import os

SERVICE_ACCOUNT_JSON = "desarrollo.json"

GOOGLE_SHEET_NAME = "1XB5A222mk9a5olSPQTwn-Nm3uLjp62OvKMQu_KzrYo0"          
WORKSHEET_NAME    = "Respuestas"


@st.cache_resource
def get_gsheet_client():
    """Conecta con Google Sheets usando la cuenta de servicio."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        # Aquí corregimos la forma en que carga las credenciales
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_JSON, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"❌ Error conectando con Google Sheets. Verifica que '{SERVICE_ACCOUNT_JSON}' exista. Detalle: {e}")
        return None
