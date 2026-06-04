import requests
import time
import os
#--------------------------------
# Parametros de conexión
#--------------------------------

TOKEN_URL = "https://mingle-sso.inforcloudsuite.com:443/SRXNDY9W53LA6625_TST/as/token.oauth2"

CLIENT_ID = "SRXNDY9W53LA6625_TST~cijMlXjHBCAZKnr8ByemTWUtGRIntivAyL_GTX5yjj0"
CLIENT_SECRET = "m3sGvNoi5Pseq6_g1HJb3iH6SYYeChavQOqILibAiZQr1HRRdPChsbrtqEZkLEZqGPcZO1AGkqjLNFn18ENNIA"
USERNAME = "SRXNDY9W53LA6625_TST#en_B9Dfu2gD6Cvvl2gyPNGNg5hfooHTrXaHJMwbqPzBpHPuh_Bn5FekgCx_BecNt70zo_G7dK7n-QMTgWCpenQ"
PASSWORD = "1JXCRsCGbZsVwQI7oNkXESJEF3cq64rhdl51roA18b7-tptFeqZJgiiacpno-7-w-NLErYW727FW-ysY2wDZhg"
URL_BASE = "https://mingle-ionapi.inforcloudsuite.com/SRXNDY9W53LA6625_TST/DATAFABRIC/compass/v2"

#--------------------------------
# OBTENER TOKEN
#--------------------------------

def get_token():

    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD
    }

    response = requests.post(
        TOKEN_URL,
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
        f"{URL_BASE}/ping",
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
        f"{URL_BASE}/jobs/?records=0",
        headers=headers,
        data=sql
    )
    #print("URL:", URL_BASE)
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
        f"{URL_BASE}/jobs/{queryid}/status/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()
#--------------------------------
# STATUS CONSULTA
#--------------------------------

def estado_consulta(token, queryid):

    while True:

        status = status_compass(
            token,
            queryid
        )

        current_status = status.get("status")

        print("Estado actual:", current_status)

        if current_status == "FINISHED":
            print("Consulta finalizada")
            break

        if current_status == "FAILED":
            raise Exception("La consulta falló")

        time.sleep(5)
        print(status)

# --------------------------------
# RESULT COMPASS
# --------------------------------

def result_compass(token,queryid):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{URL_BASE}/jobs/{queryid}/result/?limit=100",
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
    print("Token obtenido")

    ping_response = ping_compass(token)
    print("Status:", ping_response.status_code)
    print("Respuesta:", ping_response.text)

    queryid = job_query(token, sql)

    estado_consulta(token, queryid)

    return result_compass(token, queryid)


#--------------------------------
# MAIN
#--------------------------------

if __name__ == "__main__":

    ejecutar_consulta("SELECT * FROM OEP65")