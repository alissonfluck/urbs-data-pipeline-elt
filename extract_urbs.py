import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

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

def carregar_dados_postgres(df, nome_tabela, modo_insercao):
    """
    Carrega o DF para o PostgreSQL
    """
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    port = os.getenv("DB_PORT")

    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@localhost:{port}/urbs_analytics")

    try: 
        df.to_sql(nome_tabela, con=engine, if_exists=modo_insercao, index=False)
    except Exception as e:
        print(f"Falha ao carregar {nome_tabela}: {e}")

if __name__ == "__main__":
    if not URBS_TOKEN:
        print("Variável do ambiente URBS_TOKEN não encontrada.")
        exit(1)
    print("Iniciando ingestão da tabela Dimensão: Linhas...")

    dados_linhas = extrair_dados_urbs("getLinhas", URBS_TOKEN)
    if dados_linhas:
        df_linhas = pd.DataFrame(dados_linhas)
        carregar_dados_postgres(df_linhas, "dim_linha", "replace")

    print("\nIniciando ingestão da tabela Fato: Veículos...")
    dados_veiculos = extrair_dados_urbs("getVeiculos", URBS_TOKEN)

    if dados_veiculos:
        lista_veiculos = list(dados_veiculos.values())
        df_veiculos = pd.DataFrame(lista_veiculos)

        # Transform
        df_veiculos['LAT'] = df_veiculos['LAT'].astype(float)
        df_veiculos['LON'] = df_veiculos['LON'].astype(float)

        #DQ Anomalias GPS
        filtro_lat = (df_veiculos['LAT'] >= -25.7) & (df_veiculos['LAT'] <= -25.3)
        filtro_lon = (df_veiculos['LON'] >= -49.5) & (df_veiculos['LON'] <= -49.0)

        df_veiculos = df_veiculos[filtro_lat & filtro_lon]
        
        print(f"Total de veículos operando agora: {len(df_veiculos)}")
        carregar_dados_postgres(df_veiculos, "fato_posicao_veiculo", "append")