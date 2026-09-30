import csv
import numpy as np
from geopy.geocoders import Nominatim
from sklearn.linear_model import LinearRegression
import pandas as pd
import streamlit as st
from collections import Counter
from opencage.geocoder import OpenCageGeocode
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import smtplib
import ssl
import io
import zipfile

# Clave de API de OpenCage
API_KEY = '83d69dc8ddf54be29e0dbe921396a26c'
geocoder = OpenCageGeocode(API_KEY)

# Lista de países de América Latina y Europa
paises_latam_europa = [
    "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Costa Rica", "Cuba", 
    "Ecuador", "El Salvador", "Guatemala", "Honduras", "Mexico", "Nicaragua", "Panamá", 
    "Paraguay", "Perú", "Uruguay", "Venezuela", "España", "Francia", "Italia", 
    "Alemania", "Reino Unido", "Portugal"
]

# Umbral para enviar el correo electrónico
UMBRAL_REGISTROS = 10

# Datos para el envío de correo
REMITENTE = "abcdf2024dfabc@gmail.com"
PASSWORD = "hjdd gqaw vvpj hbsy"  # Contraseña de aplicación
SMTP_SERVER = "smtp.gmail.com"
PORT = 587  # Puerto para usar TLS

# Archivos para almacenar datos
ARCHIVO_CORREOS = 'correos.csv'

# Función para enviar el correo electrónico con adjunto
def enviar_correo(destinatario, mensaje, asunto, archivo_adjunto_buffer, filename="alerta_grafico.png"):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.starttls(context=context)  # Iniciar una conexión segura
            server.login(REMITENTE, PASSWORD)  # Autenticarse en el servidor
            
            # Crear mensaje con adjunto
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            msg = MIMEMultipart()
            msg['From'] = REMITENTE
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            msg.attach(MIMEText(mensaje, 'plain'))

            # Adjuntar el archivo desde el buffer
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(archivo_adjunto_buffer.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)
            
            # Enviar el correo
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

# Función para guardar el correo electrónico en el archivo
def guardar_correo(correo):
    with open(ARCHIVO_CORREOS, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([correo])

# Función para obtener la lista de correos electrónicos almacenados
def obtener_correos():
    try:
        with open(ARCHIVO_CORREOS, mode='r') as file:
            reader = csv.reader(file)
            correos = [row[0] for row in reader]
        return correos
    except FileNotFoundError:
        return []

# Función para obtener latitud y longitud basadas en el código postal y país
def obtener_coordenadas_por_codigo_postal(codigo_postal, pais):
    query = f"{codigo_postal}, {pais}"
    results = geocoder.geocode(query)
    if results and len(results) > 0:
        return results[0]['geometry']['lat'], results[0]['geometry']['lng']
    else:
        return None, None

# Función para guardar resultados y ubicación en un archivo CSV con fecha y hora
def guardar_en_archivo(resultados, latitud, longitud):
    with open('resultados.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        fecha_hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
        writer.writerow([*resultados.values(), latitud, longitud, fecha_hora_actual])

# Interfaz con Streamlit
# Mostrar el logo arriba del cuestionario
st.image("escudo_COLOR.jpg", width=100)  # Ajustar el tamaño del logo
st.title("Mapa de Riesgo Pandémico")

# Sección: Preguntas sobre síntomas graves
st.header("Síntomas")
dificultad_respiratoria_grave = st.checkbox("¿Ha tenido dificultad respiratoria grave?")
perdida_olfato_gusto = st.checkbox("¿Ha experimentado pérdida repentina del olfato o del gusto?")
fatiga_extrema = st.checkbox("¿Ha tenido fatiga extrema de aparición repentina?")
escalofrios_intensos = st.checkbox("¿Ha sufrido escalofríos intensos acompañados de fiebre alta?")
tos_perruna = st.checkbox("¿Ha presentado tos seca y ronquera severa?")
apnea_bebes = st.checkbox("¿Ha tenido episodios de apnea o problemas respiratorios graves?")
neumonia_bronquiolitis = st.checkbox("¿Le han diagnosticado neumonía o bronquiolitis recientemente?")

# Sección: Preguntas adicionales (sobre condiciones y factores de riesgo)
st.header("Factores")
movilidad_poblacional = st.checkbox("¿Ha viajado o estado en contacto con muchas personas últimamente?")
hacinamiento = st.checkbox("¿Vive en un lugar con alta densidad de personas?")
acceso_servicios = st.checkbox("¿Tiene dificultades para acceder a servicios médicos de calidad?")
contaminacion_aire = st.checkbox("¿Vive en una zona con altos niveles de contaminación del aire?")

# Sección: Código Postal y País
st.header("Ubicación")
codigo_postal = st.text_input("Introduce el código postal de la ubicación desde donde respondes este cuestionario")
pais = st.selectbox("Selecciona el país desde el cual respondes este cuestionario", sorted(paises_latam_europa), index=sorted(paises_latam_europa).index("Mexico"))

# Pregunta sobre recibir alertas epidemiológicas
correo_usuario = st.text_input("Si desea recibir las alertas epidemiológicas en su correo electrónico, por favor ingréselo aquí (deje vacío si no desea recibirlas):")

# Botón para procesar y guardar los datos (incluyendo la obtención automática de coordenadas)
if st.button("Procesar y Guardar"):
    # Obtener coordenadas por código postal y país
    latitud, longitud = obtener_coordenadas_por_codigo_postal(codigo_postal, pais)
    
    if latitud and longitud:
        resultados = {
            'dificultad_respiratoria_grave': dificultad_respiratoria_grave,
            'perdida_olfato_gusto': perdida_olfato_gusto,
            'fatiga_extrema': fatiga_extrema,
            'escalofrios_intensos': escalofrios_intensos,
            'tos_perruna': tos_perruna,
            'apnea_bebes': apnea_bebes,
            'neumonia_bronquiolitis': neumonia_bronquiolitis,
            'movilidad_poblacional': movilidad_poblacional,
            'hacinamiento': hacinamiento,
            'acceso_servicios': acceso_servicios,
            'contaminacion_aire': contaminacion_aire
        }

        # Guardar los datos junto con la ubicación y fecha/hora
        guardar_en_archivo(resultados, latitud, longitud)
        st.success(f"Datos guardados con éxito. Ubicación: Latitud {latitud}, Longitud {longitud}")

        # Guardar el correo electrónico si se ingresó
        if correo_usuario:
            guardar_correo(correo_usuario)
            st.info(f"El correo {correo_usuario} ha sido guardado para recibir alertas.")

        try:
            # Leer el archivo CSV para generar el gráfico
            data = pd.read_csv('resultados.csv', names=[
                'dificultad_respiratoria_grave', 'perdida_olfato_gusto', 'fatiga_extrema',
                'escalofrios_intensos', 'tos_perruna', 'apnea_bebes', 'neumonia_bronquiolitis',
                'movilidad_poblacional', 'hacinamiento', 'acceso_servicios', 'contaminacion_aire',
                'latitud', 'longitud', 'fecha_hora'], parse_dates=['fecha_hora'])

            # Contar los registros diarios
            data_ultimos_30_dias = data[data['fecha_hora'] >= (datetime.now() - timedelta(days=30))]
            data_ultimos_30_dias['fecha_dia'] = data_ultimos_30_dias['fecha_hora'].dt.date
            registros_diarios = data_ultimos_30_dias.groupby('fecha_dia').size()

            # Comprobar si algún cúmulo excede el umbral
            if registros_diarios.max() > UMBRAL_REGISTROS:
                mensaje_alerta = f"Alerta: El cúmulo ha excedido el umbral de {UMBRAL_REGISTROS} registros."
                asunto = f"Alerta epidemiológica en {pais}"
                
                # Generar el gráfico
                plt.figure(figsize=(10, 6))
                plt.plot(registros_diarios.index, registros_diarios.values, marker='o', linestyle='-', label='Registros diarios')
                plt.axhline(y=UMBRAL_REGISTROS, color='red', linestyle='--', label='Umbral')
                plt.title(f'Registros en {pais} - Últimos 30 días')
                plt.xlabel('Fecha')
                plt.ylabel('Número de Registros')
                plt.legend()
                plt.grid()

                # Mostrar el gráfico en la pantalla
                st.pyplot(plt)

                # Guardar el gráfico en un buffer de memoria
                grafico_buffer = io.BytesIO()
                plt.savefig(grafico_buffer, format='png')
                grafico_buffer.seek(0)
                plt.close()
                
                # Enviar correo si el usuario ingresó "polanco@unam.mx"
                if correo_usuario == "polanco@unam.mx":
                    correos_a_enviar = obtener_correos()
                    for correo in correos_a_enviar:
                        enviar_correo(correo, mensaje_alerta, asunto, grafico_buffer)
                    st.warning(f"Se ha enviado una alerta a todos los correos registrados.")
                    
                    # Crear un archivo ZIP con ambos archivos
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zf:
                        # Agregar el gráfico al ZIP
                        zf.writestr('alerta_grafico.png', grafico_buffer.getvalue())
                        
                        # Generar el archivo de correos y agregar al ZIP
                        correos_buffer = io.StringIO()
                        with open(ARCHIVO_CORREOS, mode='r') as file:
                            correos_buffer.write(file.read())
                        correos_buffer.seek(0)
                        zf.writestr('correos.csv', correos_buffer.getvalue())
                    
                    zip_buffer.seek(0)
                    
                    # Descargar el archivo ZIP
                    st.download_button(
                        label="Descargar Archivos ZIP",
                        data=zip_buffer,
                        file_name="archivos.zip",
                        mime="application/zip"
                    )
                
                # Enviar correo solo si el usuario ingresó su correo electrónico
                elif correo_usuario:
                    enviar_correo(correo_usuario, mensaje_alerta, asunto, grafico_buffer)
                    st.warning(f"Se ha enviado una alerta a {correo_usuario}: {mensaje_alerta}")
                else:
                    st.info("No se enviará ninguna alerta ya que no se ingresó un correo electrónico.")

        except FileNotFoundError:
            st.error("No se encontró el archivo de resultados. Asegúrate de que se haya guardado algún registro.")
        
    else:
        st.error("No se pudo obtener la ubicación. Verifica el código postal y país.")

