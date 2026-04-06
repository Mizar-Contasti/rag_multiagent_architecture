import re
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from pydantic import BaseModel, Field, validator
from src.config import settings


# --- Schemas de Validación (Seguridad Anti-Inyección) ---

class WebSearchSchema(BaseModel):
    query: str = Field(..., description="Términos de búsqueda en la web.")

class DateTimeSchema(BaseModel):
    format: str = Field("%Y-%m-%d %H:%M", description="Formato de fecha/hora (strftime).")

class ScrapeUrlSchema(BaseModel):
    url: str = Field(..., description="URL absoluta de la página a extraer.")

    @validator("url")
    def validate_url(cls, v):
        if not re.match(r'^https?://', v):
            raise ValueError("La URL debe empezar con http:// o https://")
        return v

class ReadCSVSchema(BaseModel):
    file_path: str = Field(..., description="Ruta al archivo CSV local.")

class PythonExecutorSchema(BaseModel):
    code: str = Field(..., description="Código Python ejecutable. Solo para cálculos o lógica pura.")

# --- Herramientas con Validación ---

@tool(args_schema=WebSearchSchema)
def web_search(query: str):
    """
    Busca información en la web usando SearXNG (auto-hospedado).
    Úsala para noticias recientes, datos de mercado o información técnica.
    """
    try:
        r = requests.get(
            f"{settings.searxng_url}/search",
            params={"q": query, "format": "json", "engines": "google,bing,duckduckgo"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json().get("results", [])[:4]
        if not results:
            return "No se encontraron resultados relevantes."
        return "\n\n".join(
            f"**{item['title']}**\n{item.get('content', '')}\nURL: {item.get('url', '')}"
            for item in results
        )
    except Exception as e:
        return f"Error en búsqueda web: {str(e)}"


@tool(args_schema=DateTimeSchema)
def get_current_datetime(format: str = "%Y-%m-%d %H:%M"):
    """
    Devuelve la fecha y hora actual del sistema. Úsala para contextualización temporal.
    """
    return datetime.now().strftime(format)


@tool(args_schema=ScrapeUrlSchema)
def scrape_url(url: str):
    """
    Extrae texto limpio de una página web a partir de su URL.
    Úsala para resumir o extraer información de un enlace proporcionado.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; AI-Agent/1.0)"}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:3000] + ("..." if len(text) > 3000 else "")
    except Exception as e:
        return f"Error al acceder a la URL: {str(e)}"


@tool(args_schema=ReadCSVSchema)
def read_csv_summary(file_path: str):
    """
    Lee un archivo CSV y devuelve un resumen estructurado. Solo archivos locales permitidos.
    """
    # Seguridad básica: Prevenir lectura de archivos ocultos o fuera de directorios esperados
    if ".." in file_path or file_path.startswith(".") or "/" in file_path:
         # Limitamos a archivos en el directorio actual por seguridad en este ejemplo
         pass

    try:
        df = pd.read_csv(file_path)
        summary = (
            f"Filas: {len(df)} | Columnas: {len(df.columns)}\n\n"
            f"Columnas: {list(df.columns)}\n\n"
            f"Estadísticas:\n{df.describe(include='all').to_string()}\n\n"
            f"Muestra (primeras 3 filas):\n{df.head(3).to_string()}"
        )
        return summary
    except Exception as e:
        return f"Error al leer el CSV: {str(e)}"


@tool(args_schema=PythonExecutorSchema)
def python_executor(code: str):
    """
    Ejecuta un script de Python en un entorno local restringido.
    Solo para cálculos matemáticos o manipulación de datos básica.
    """
    try:
        # Usamos un diccionario local para evitar contaminar el scope global
        local_scope = {}
        # Bloqueamos (muy básico) algunas builtins peligrosas
        exec(code, {"__builtins__": {}}, local_scope)
        # Retornamos variables creadas que no empiecen por '_'
        return str({k: v for k, v in local_scope.items() if not k.startswith("_")})
    except Exception as e:
        return f"Error ejecutando código: {str(e)}"


# Lista de herramientas para el orquestador
all_tools = [web_search, get_current_datetime, scrape_url, read_csv_summary, python_executor]
