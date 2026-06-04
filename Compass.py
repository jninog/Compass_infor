import requests
import time
import os
from dotenv import load_dotenv

#--------------------------------
# OBTENER TOKEN
#--------------------------------
load_dotenv()  # Carga las variables de entorno desde el archivo .env

def get_token():

    data = {
        "grant_type": "password",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "username": os.getenv("USER_NAME"),
        "password": os.getenv("PASSWORD")
    }
    print("TOKEN_URL:", os.getenv("TOKEN_URL"))
    print("CLIENT_ID:", os.getenv("CLIENT_ID"))
    print("USERNAME:", os.getenv("USER_NAME"))
    response = requests.post(
        os.getenv("TOKEN_URL"),
        data=data
    )

    response.raise_for_status()

    token = response.json()["access_token"]

    return token

#--------------------------------
# PING COMPASS
#--------------------------------

def ping_compass(token):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{os.getenv('URL_BASE')}/ping",
        headers=headers
    )

    return response

#--------------------------------
# JOBS COMPASS
#--------------------------------
#URL_BASE2 = "https://mingle-ionapi.inforcloudsuite.com/SRXNDY9W53LA6625_TST/DATAFABRIC/compass/v2/jobs/?records=0"
def job_query(token,sql):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "text/plain"
    }

    response = requests.post(
        f"{os.getenv('URL_BASE')}/jobs/?records=0",
        headers=headers,
        data=sql
    )
    #print("URL:", os.getenv('URL_BASE'))
    #print("HEADERS:", headers)
    #print("SQL:")
    #print(sql)
    print("Status Query:", response.status_code)
    print("Response:", response.text)
    queryid = response.json().get("queryId")
    print("Query ID:", queryid)
    response.raise_for_status()
    return queryid


#--------------------------------
# STATUS COMPASS
#--------------------------------

def status_compass(token,queryid):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{os.getenv('URL_BASE')}/jobs/{queryid}/status/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()
#--------------------------------
# wait_for_completion
#--------------------------------

def wait_for_completion(token, queryid, max_retries=60):
    """Espera a que la consulta finalice con un límite de intentos."""
    for attempt in range(max_retries):
        try:
            status_data = status_compass(token, queryid)
            current_status = status_data.get("status")
            print(f"Intento {attempt+1}: Estado actual -> {current_status}")

            if current_status == "FINISHED":
                return True
            elif current_status == "FAILED":
                raise Exception(f"La consulta falló: {status_data.get('error', 'Sin detalle')}")
            elif current_status == "CANCELED ":
                raise Exception(f"La consulta fue cancelada: {status_data.get('error', 'Sin detalle')}")
            
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Error consultando estado: {e}")
            time.sleep(5)
            
    raise TimeoutError("La consulta excedió el tiempo máximo de espera.")

# --------------------------------
# RESULT COMPASS
# --------------------------------

def result_compass(token,queryid):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{os.getenv('URL_BASE')}/jobs/{queryid}/result/?limit=100",
        headers=headers
    )
    response.raise_for_status()
    print(response.json())
    return response.json()


#--------------------------------
# EJECUTAR CONSULTA COMPLETA
#--------------------------------

def ejecutar_consulta(sql):
    """
    Ejecuta el flujo completo de Compass:
    obtiene token, envía la consulta, espera a que finalice y devuelve el resultado.
    """
    token = get_token()
    queryid = job_query(token, sql)
        
        # Solo procedemos si la espera fue exitosa
    if wait_for_completion(token, queryid):        
        return result_compass(token, queryid)   

    print(f"Error crítico en el flujo: {queryid} no finalizó correctamente.")
    return None


#--------------------------------
# MAIN
#--------------------------------

if __name__ == "__main__":

    ejecutar_consulta("SELECT * FROM OEP65")