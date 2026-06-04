#--------------------------------
# API COMPASS - FastAPI
#--------------------------------

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests

from Compass import ejecutar_consulta

#--------------------------------
# APLICACIÓN
#--------------------------------

app = FastAPI(
    title="API Compass",
    description=(
        "API para ejecutar consultas SQL contra Infor Data Fabric Compass. "
        "Obtiene token OAuth, envía el job, espera el estado FINISHED y devuelve el resultado."
    ),
    version="1.0.0",
)

#--------------------------------
# ESQUEMAS
#--------------------------------


class QueryRequest(BaseModel):
    """Petición con la consulta SQL a ejecutar en Compass."""

    query: str = Field(
        ...,
        description="Consulta SQL en texto plano (mismo formato que se envía a /jobs/).",
        examples=["SELECT * FROM OEP65"],
        min_length=1,
    )


class QueryResponse(BaseModel):
    """Respuesta con el resultado JSON devuelto por Compass /jobs/{queryId}/result/."""

    query_id: str | None = Field(
        default=None,
        description="Identificador del job en Compass (si está disponible en el resultado).",
    )
    data: list[dict[str, Any]] | dict[str, Any] = Field(
        ...,
        description=(
            "Resultado de Compass: lista de filas (registros) o objeto JSON "
            "según el formato que devuelva /jobs/{queryId}/result/."
        ),
    )

#--------------------------------
# ENDPOINT
#--------------------------------


@app.post(
    "/query",
    response_model=QueryResponse,
    summary="Ejecutar consulta Compass",
    tags=["Compass"],
)
def ejecutar_query(body: QueryRequest) -> QueryResponse:
    """
    Recibe una consulta SQL y ejecuta el flujo completo de Compass:

    1. **OBTENER TOKEN** — autenticación OAuth2 (password grant).
    2. **PING COMPASS** — verificación de conectividad.
    3. **JOBS COMPASS** — envío de la consulta y obtención del `queryId`.
    4. **STATUS CONSULTA** — espera hasta estado `FINISHED` o error si `FAILED`.
    5. **RESULT COMPASS** — lectura del resultado (limit por defecto en Compass).

    Devuelve el JSON del paso 5.
    """

    try:
        resultado = ejecutar_consulta(body.query)
    except requests.HTTPError as exc:
        detail = str(exc)
        if exc.response is not None:
            detail = exc.response.text or detail
        raise HTTPException(
            status_code=exc.response.status_code if exc.response is not None else 502,
            detail=detail,
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    query_id = resultado.get("queryId") if isinstance(resultado, dict) else None

    return QueryResponse(query_id=query_id, data=resultado)
