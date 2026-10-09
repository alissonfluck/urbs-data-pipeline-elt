import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

URBS_TOKEN = os.getenv("URBS_TOKEN")

def extrair_dados_urbs(endpoint, token):
    """
    Realiza requisições HTTP GET para a API da URBS
    """
    url_base = "https://transporteservico.urbs.curitiba.pr.gov.br/"

    # Monta URL (base + endpoint + .php?c= + token)
    url = f"{url_base}{endpoint}.php?c={URBS_TOKEN}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Falha na extração do endpoint {endpoint}: {e}")
        return None

if __name__ == "__main__":
    if not URBS_TOKEN:
        print("Variável do ambiente URBS_TOKEN não encontrada.")
        exit(1)
    print("Iniciando ingestão da Dimensão: Linhas...")

    dados_linhas = extrair_dados_urbs("getLinhas", URBS_TOKEN)
    if dados_linhas:
        df_linhas = pd.DataFrame(dados_linhas)

        # Validação visual
        print(df_linhas.head())
        print(f"\nTotal de linhas ativas extraídas: {len(df_linhas)}")

