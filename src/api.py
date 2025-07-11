import requests
import json

# Endpoint do Wikidata para consultas SPARQL
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

# Headers
HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "RodrigoNogueira/1.0"
}

def execute_sparql_query(query):
    
    try:
        response = requests.get(
            WIKIDATA_ENDPOINT,
            headers=HEADERS,
            params={"query": query}
        )
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao executar consulta SPARQL: {e}")
        raise Exception(f"Falha na consulta ao Wikidata: {str(e)}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        raise
