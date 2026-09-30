# cumulos12.py — Pandemic Risk Monitoring System

A Streamlit web application that collects geolocated questionnaire
responses about respiratory symptoms and sociodemographic risk factors,
estimates a spatial cluster within a 3 km radius, fits a first-degree
least-squares trend to daily case counts, and sends email alerts when a
configurable threshold is exceeded.

This README explains how to install, configure, and run cumulos12.py.

---

## 1. Requirements

- Python 3.9 or higher
- pip
- An OpenCage API key (free tier: https://opencagedata.com/users/sign_up)
- A Gmail account with an App Password (optional, only if you want email
  alerts to be sent)

---

## 2. Install

### Linux / macOS

    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install streamlit pandas numpy matplotlib scikit-learn geopy opencage

### Windows (PowerShell)

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install streamlit pandas numpy matplotlib scikit-learn geopy opencage

### requirements.txt (alternative)

Create a file named requirements.txt with:

    streamlit>=1.28
    pandas>=2.0
    numpy>=1.24
    matplotlib>=3.7
    scikit-learn>=1.3
    geopy>=2.4
    opencage>=1.4

Then install with:

    pip install -r requirements.txt

---

## 3. Configure

Open cumulos12.py in a text editor and set the following variables at
the top of the file.

### 3.1 OpenCage API key (mandatory)

Replace the placeholder with your own key:

    API_KEY = 'your_opencage_api_key_here'

### 3.2 Gmail credentials (optional, only for email alerts)

    REMITENTE = "your_email@gmail.com"
    PASSWORD  = "your_16_char_app_password"
    SMTP_SERVER = "smtp.gmail.com"
    PORT = 587

To generate an App Password:

1. Enable 2-Step Verification at https://myaccount.google.com/security
2. Go to https://myaccount.google.com/apppasswords
3. Generate a 16-character password for "Mail" / "Other device"
4. Paste it into PASSWORD (no spaces)

If you do not need email alerts, leave these values as they are and
simply do not enter an email address in the form.

### 3.3 Alert threshold (optional)

The default threshold is 10 cases per day. To change it:

    UMBRAL_REGISTROS = 10

### 3.4 Logo file (optional)

The app displays a logo at the top:

    st.image("escudo_COLOR.jpg", width=100)

If you do not have escudo_COLOR.jpg in the same folder, comment out that
line by adding a # at the beginning:

    # st.image("escudo_COLOR.jpg", width=100)

---

## 4. Run

From the folder that contains cumulos12.py:

    streamlit run cumulos12.py

Streamlit will print something like:

    You can now view your Streamlit app in your browser.
    Local URL: http://localhost:8501

Open that URL in your browser.

### Run on a different port

    streamlit run cumulos12.py --server.port 8080

### Run on a server without opening a browser

    streamlit run cumulos12.py --server.headless true --server.address 0.0.0.0 --server.port 8501

Then access it from another machine at http://<server-ip>:8501.

### Run on a mobile phone (same Wi-Fi network)

Find your computer's local IP (for example 192.168.1.42), then:

    streamlit run cumulos12.py --server.address 0.0.0.0 --server.port 8501

Open http://192.168.1.42:8501 on your phone.

---

## 5. Use

1. Open the app in a browser.
2. Answer the Symptom questions (7 checkboxes).
3. Answer the Risk Factor questions (4 checkboxes).
4. Enter your postal code and select your country.
5. (Optional) Enter your email to receive alerts.
6. Click "Procesar y Guardar".

The app will:

- Geolocate your postal code using OpenCage.
- Append the response to resultados.csv with a timestamp.
- Save your email to correos.csv if you provided one.
- Read resultados.csv and plot the daily case counts for the last 30 days.
- Fit a first-degree least-squares line to the daily counts.
- Draw the alert threshold line at UMBRAL_REGISTROS (default 10).
- If the maximum daily count exceeds the threshold, send an email alert.

---

## 6. Files created at runtime

These files are generated automatically in the working directory:

    resultados.csv     One row per questionnaire submission, with columns:
                       - the 11 boolean answers
                       - latitud, longitud (from OpenCage)
                       - fecha_hora (timestamp YYYY-MM-DD HH:MM)

    correos.csv        One email address per line (subscribed users).

    comparacion_casos_minimos_cuadrados.png
                       The most recent alert plot (only when an alert
                       is triggered).

To start from a clean state:

    rm -f resultados.csv correos.csv comparacion_casos_minimos_cuadrados.png

---

## 7. Troubleshooting

### ModuleNotFoundError: No module named 'streamlit'

You forgot to activate the virtual environment. Run:

    source .venv/bin/activate      (Linux / macOS)
    .venv\Scripts\Activate.ps1     (Windows PowerShell)

Then reinstall dependencies.

### opencage.exceptions.RateLimitExceededError

You exceeded the free OpenCage tier (2,500 requests per day). Wait 24
hours, cache postal-code lookups locally, or upgrade your OpenCage plan.

### smtplib.SMTPAuthenticationError (535)

Gmail rejected your credentials. Check:

- You are using an App Password, not your main password.
- 2-Step Verification is enabled on your Google account.
- The App Password has no spaces.
- SMTP_SERVER = "smtp.gmail.com" and PORT = 587.

### FileNotFoundError: resultados.csv

The file does not exist yet. It is created automatically the first time
you click "Procesar y Guardar". Submit at least one response first.

### UnicodeEncodeError when reading the CSV

Open the CSV with UTF-8 encoding. In Python:

    pd.read_csv('resultados.csv', encoding='utf-8')

### Streamlit does not reload after editing the file

Stop the server with Ctrl+C and restart it:

    streamlit run cumulos12.py

### The app opens on the wrong port

Kill any previous Streamlit instance:

    pkill -f streamlit

Then run again.

---

## 8. Quick-start summary

    git clone https://github.com/polancodf2024/EPI.git
    cd EPI
    python3 -m venv .venv
    source .venv/bin/activate
    pip install streamlit pandas numpy matplotlib scikit-learn geopy opencage
    # edit cumulos12.py and set API_KEY (and optionally Gmail credentials)
    streamlit run cumulos12.py

---

## 9. License

MIT License.

---

## 10. Contact

Carlos Polanco — cpolanco@unam.mx
Martha Rios Castro — martha.rios@cardiologia.org.mx
