# 📱 Phone Enumerator Pro

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![OSINT](https://img.shields.io/badge/Category-OSINT-success.svg)
![Tor](https://img.shields.io/badge/Network-Tor_Routing-purple.svg)
![License](https://img.shields.io/badge/License-GPL_3.0-lightgrey.svg)

**Phone Enumerator Pro** es una herramienta avanzada de inteligencia de fuentes abiertas (OSINT) diseñada para el perfilado pasivo y activo de números telefónicos. Construida pensando en la Seguridad Operacional (OPSEC), combina el análisis *offline* de bases de datos de telecomunicaciones con consultas *online* anonimizadas a través de la red Tor.

## 📑 Tabla de Contenidos
- [Características Principales](#-características-principales)
- [Aviso Legal](#-aviso-legal-disclaimer)
- [Demostración](#-demostración)
- [Instalación y Requisitos](#️-instalación-y-requisitos)
- [Uso y Sintaxis](#-uso-y-sintaxis)
- [Integración en Pipelines (jq)](#-integración-avanzada-ejemplo-con-jq)

---

## 🚀 Características Principales

*   **Análisis Pasivo (Offline):** Extracción instantánea de geolocalización, operadora original (ISP), husos horarios y formato E.164 sin emitir tráfico de red.
*   **Detección de Burners:** Identificación precisa del tipo de línea, destacando números VoIP, tarifas premium o toll-free.
*   **Módulo de Reputación Anonimizado:** Evasión de bloqueos e IPs mediante el enrutamiento de consultas *web scraping* a través de nodos Tor SOCKS5.
*   **WAF Evasion:** Falsificación de huellas dactilares (User-Agent, Headers) para evadir firewalls de aplicaciones web básicos (ej. Cloudflare).
*   **Ejecución Masiva:** Soporte para lectura de listas de objetivos desde archivos `.txt`.
*   **Integración de Pipeline:** Exportación limpia de resultados a formato JSON (`-o`) estructurado, ideal para ser procesado por `jq` o bases de datos NoSQL.

---

## ⚠️ Aviso Legal (Disclaimer)

Esta herramienta ha sido desarrollada estrictamente para **fines educativos y auditorías autorizadas**. El desarrollador no se hace responsable del mal uso de la información extraída. Asegúrate de cumplir con las leyes locales y regulaciones de privacidad antes de perfilar un objetivo.

---

## 🖥️ Demostración

```text
 ┌───────────────────────────────────────┐
 │       PHONE ENUMERATOR PRO            │
 │       OSINT & Telecom Analysis        │
 └───────────────────────────────────────┘

[+] Target: +34613814500
    ├─ Ubicación:   España
    ├─ Operadora:   Yoigo
    ├─ Tipo:        Móvil
    ├─ Timezone:    Atlantic/Canary, Europe/Madrid
    └─ E.164:       +34 613 81 45 00

[*] Consultando bases de datos de reputación (Tor Network)...
    ├─ Reputación: Sin reportes graves detectados en la superficie.

```

---

## ⚙️ Instalación y Requisitos

La fase online de la herramienta requiere que el demonio de **Tor** esté instalado y ejecutándose localmente en el puerto `9050`.

### 1. Requisitos del Sistema (Debian / Kali / Parrot)

```bash
sudo apt update
sudo apt install tor
sudo systemctl start tor

```

### 2. Configuración del Entorno Python

Se recomienda encarecidamente utilizar un entorno virtual (`venv`) para evitar conflictos de dependencias (PEP 668).

```bash
git clone [https://github.com/rodrigo47363/enum_phone.py.git](https://github.com/rodrigo47363/enum_phone.py.git)
cd enum_phone.py

# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install requests beautifulsoup4 phonenumbers pysocks

```

### 3. Instalación Global (Opcional - Recomendada)

Para poder ejecutar `enum_phone` desde cualquier parte de tu sistema sin tener que activar manualmente el entorno virtual, puedes crear un *wrapper* en tus binarios locales:

```bash
chmod +x enum_phone.py
mkdir -p ~/.local/bin

cat << 'EOF' > ~/.local/bin/enum_phone
#!/bin/bash
source /ruta/absoluta/a/tu/clon/enum_phone.py/.venv/bin/activate
python3 /ruta/absoluta/a/tu/clon/enum_phone.py/enum_phone.py "$@"
deactivate
EOF

chmod +x ~/.local/bin/enum_phone

```

*(Asegúrate de cambiar `/ruta/absoluta/a/tu/clon/` por la ruta real donde clonaste el repositorio).*

---

## 📖 Uso y Sintaxis

```text
Uso: enum_phone.py [-h] (-t TARGET | -l LIST) [-o OUTPUT]

Opciones:
  -h, --help            Muestra este mensaje de ayuda y sale.
  -t TARGET, --target TARGET
                        Número objetivo individual (Ej. +528441234567)
  -l LIST, --list LIST  Archivo .txt con múltiples números.
  -o OUTPUT, --output OUTPUT
                        Ruta del archivo para exportar resultados a JSON.

```

### Ejemplos Prácticos

**1. Análisis de un objetivo único:**

```bash
enum_phone -t +34613814500

```

**2. Escaneo masivo desde un archivo:**

```bash
enum_phone -l targets.txt

```

**3. Escaneo masivo con exportación para pipelines de inteligencia:**

```bash
enum_phone -l targets.txt -o inteligencia.json

```

---

## 🔗 Integración Avanzada (Ejemplo con `jq`)

El verdadero poder de la exportación JSON radica en la automatización. Si realizaste un escaneo de 1,000 números y deseas aislar únicamente aquellos que son teléfonos descartables (VoIP) y que además tienen reportes de fraude, puedes usar `jq`:

```bash
cat inteligencia.json | jq -r '.[] | select(.line_type == "VoIP (Virtual/Burner)" and .reputation == "Peligro: SPAM/Fraude") | .target'

```

---

*Desarrollado por **rodrigo47363** - Ciberseguridad & Red Team*

```

```
