#!/usr/bin/env python3
import argparse
import urllib.parse
import requests
import json
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from phonenumbers.phonenumberutil import number_type, PhoneNumberType

class C:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

LINE_TYPES = {
    PhoneNumberType.MOBILE: 'Móvil',
    PhoneNumberType.FIXED_LINE: 'Línea Fija',
    PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fija o Móvil',
    PhoneNumberType.TOLL_FREE: 'Toll-Free (Gratuito)',
    PhoneNumberType.PREMIUM_RATE: 'Tarifa Premium',
    PhoneNumberType.VOIP: 'VoIP (Virtual/Burner)',
    PhoneNumberType.UNKNOWN: 'Desconocido'
}

def print_banner():
    banner = f"""{C.CYAN}
 ┌───────────────────────────────────────┐
 │       PHONE ENUMERATOR PRO            │
 │       OSINT & Telecom Analysis        │
 └───────────────────────────────────────┘{C.RESET}"""
    print(banner)

def check_reputation(numero_e164):
    """Devuelve un string con el estado de reputación en lugar de solo imprimirlo"""
    print(f"\n{C.BLUE}[*] Consultando bases de datos de reputación (Tor Network)...{C.RESET}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.5'
    }
    
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    
    num_encoded = urllib.parse.quote(numero_e164)
    url = f"https://spamcalls.net/es/numero/{num_encoded}"
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        
        if response.status_code == 403:
             print(f"    {C.YELLOW}├─ WAF Detectado: El servidor bloqueó el nodo de salida Tor.{C.RESET}")
             return "WAF Block (Cloudflare)"
             
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texto_pagina = soup.get_text().lower()
            if "spam" in texto_pagina or "peligroso" in texto_pagina or "fraude" in texto_pagina:
                print(f"    {C.RED}├─ Reputación: ¡PELIGRO! Número listado en bases de datos de SPAM/Fraude.{C.RESET}")
                return "Peligro: SPAM/Fraude"
            else:
                 print(f"    {C.GREEN}├─ Reputación: Sin reportes graves detectados en la superficie.{C.RESET}")
                 return "Limpio (Superficie)"
                 
        elif response.status_code == 404:
            print(f"    {C.GREEN}├─ Reputación: Número limpio (No encontrado en la DB de spam).{C.RESET}")
            return "Limpio (No en DB)"
        else:
            print(f"    {C.YELLOW}├─ Estado HTTP Inesperado: {response.status_code}{C.RESET}")
            return f"Desconocido (HTTP {response.status_code})"

    except requests.exceptions.Timeout:
        print(f"    {C.YELLOW}├─ Error: Timeout en red Tor.{C.RESET}")
        return "Error: Timeout"
    except requests.exceptions.ConnectionError:
        print(f"    {C.RED}├─ Error Crítico: No se pudo conectar a Tor.{C.RESET}")
        return "Error: Falla conexión Tor"
    except requests.exceptions.RequestException as e:
        print(f"    {C.RED}├─ Error de red: {e}{C.RESET}")
        return "Error: Red"

def analizar_numero(numero_raw):
    """Procesa el número y devuelve un diccionario con los resultados para exportar"""
    try:
        if not numero_raw.startswith('+'):
            numero_raw = '+' + numero_raw

        numero = phonenumbers.parse(numero_raw)

        if not phonenumbers.is_valid_number(numero):
            print(f"{C.RED}[-] {numero_raw} : Número inválido.{C.RESET}")
            return None # Retorna nulo para no ensuciar el JSON final

        print(f"\n{C.GREEN}[+] Target: {numero_raw}{C.RESET}")
        
        region = geocoder.description_for_number(numero, 'es')
        operadora = carrier.name_for_number(numero, 'es')
        zonas_horarias = timezone.time_zones_for_number(numero)
        tipo_linea = number_type(numero)
        formato_int = phonenumbers.format_number(numero, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        tipo_str = LINE_TYPES.get(tipo_linea, 'Desconocido/Otro')
        tipo_color = C.YELLOW if tipo_linea == PhoneNumberType.VOIP else C.RESET

        print(f"    ├─ Ubicación:   {region if region else 'Desconocida'}")
        print(f"    ├─ Operadora:   {operadora if operadora else 'Desconocida'}")
        print(f"    ├─ Tipo:        {tipo_color}{tipo_str}{C.RESET}")
        print(f"    ├─ Timezone:    {', '.join(zonas_horarias)}")
        print(f"    └─ E.164:       {formato_int}")

        reputacion = check_reputation(formato_int)
        
        # Construcción de la estructura de datos (JSON)
        datos = {
            "target": numero_raw,
            "e164_format": formato_int,
            "location": region if region else "Desconocida",
            "carrier": operadora if operadora else "Desconocida",
            "line_type": tipo_str,
            "timezone": list(zonas_horarias),
            "reputation": reputacion
        }
        return datos

    except phonenumbers.NumberParseException:
        print(f"{C.RED}[-] Error: Formato inválido en {numero_raw}.{C.RESET}")
        return None
    except Exception as e:
        print(f"{C.RED}[-] Error inesperado: {e}{C.RESET}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Herramienta avanzada de OSINT telefónico.")
    
    # Grupo de argumentos para la entrada (Input)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--target", help="Número objetivo individual")
    group.add_argument("-l", "--list", help="Archivo .txt con múltiples números")
    
    # Argumento opcional para la salida (Output)
    parser.add_argument("-o", "--output", help="Ruta del archivo para guardar resultados en formato JSON")

    args = parser.parse_args()
    print_banner()

    resultados_export = [] # Lista maestra para el JSON

    if args.target:
        resultado = analizar_numero(args.target)
        if resultado:
            resultados_export.append(resultado)
            
    elif args.list:
        try:
            with open(args.list, 'r') as file:
                numeros = [line.strip() for line in file if line.strip()]
                for num in numeros:
                    resultado = analizar_numero(num)
                    if resultado:
                        resultados_export.append(resultado)
        except FileNotFoundError:
            print(f"{C.RED}[-] Archivo no encontrado: {args.list}{C.RESET}")

    # Lógica de volcado (Dump) a JSON al terminar el análisis
    if args.output and resultados_export:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                # ensure_ascii=False respeta los acentos (ej. "Móvil", "España")
                # indent=4 le da un formato legible y tabulado
                json.dump(resultados_export, f, ensure_ascii=False, indent=4)
            print(f"\n{C.GREEN}[+] Resultados exportados exitosamente a: {args.output}{C.RESET}")
        except Exception as e:
            print(f"\n{C.RED}[-] Error al guardar el archivo JSON: {e}{C.RESET}")

if __name__ == "__main__":
    main()
