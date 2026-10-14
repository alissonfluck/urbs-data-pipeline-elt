# URBS Analytics: Pipeline ELT de Transporte Público

## Visão Geral
Este projeto implementa um pipeline de dados de ponta a ponta focado em mobilidade urbana, consumindo dados da API da URBS (Curitiba). O objetivo é demonstrar a construção de uma arquitetura ELT moderna, isolamento de infraestrutura via contêiners e modelagem dimensional para análise de frota.

## Arquitetura de Dados (Ciclo de Vida)
O fluxo do projeto foi construído seguindo os princípios de Data Engineering (Reis & Housley):

1. **Ingestão (Extract e Load):** Script em Python (`extract_urbs.py`) realiza chamadas à API REST da URBS. Foi aplicado *Data Shaping* e *Schema Enforcement* em memória utilizando `pandas`para garantir a tipagem correta de coordenadas espaciais antes da carga.
2. **Armazenamento (Storage):** PostgreSQL provisionado em Docker. Os dados são persistidos diretamente no banco sem (I/O) intermediário no disco local.
3. **Transformação (Transform):** Utilização do paradigma *Pushdown de Computação*. As transformações de negócio ocorrem no motor relacional (Banco de Dados) via SQL, garantindo escalabilidade.
4. **Servimento (Serving):** Metabase provisionado em Docker, operando na mesma rede do banco de dados (DNS interno). Responsável pela renderização de relatórios e mapas.

## Modelagem Dimensional (Kimball)
O Data Warehouse foi estruturado num Esquema Estrela (Star Schema):
* **Tabela Fato (`fato_posicao_veiculo`):** Armazena a granularidade mais fina do evento geográfico (Latitude, Longitude e Timestamp da leitura do GPS).
* **Tabela Dimensão (`dim_linha`):** Armazena o contexto do negócio (Nome da linha, Categoria, Cor), conectando-se à tabela fato via chaves estrangeiras.

## Tecnologias Utilizadas
* **Linguagem:** Python (Requests, Pandas)
* **Banco de Dados:** PostgreSQL
* **Infraestrutura:** Docker e Docker Compose
* **Visualização:** Metabase
* **Ambiente:** WSL2 (Ubuntu)

## Resultados Visuais e Ressalvas Analíticas

### 1. Densidade de Frota por Categoria
![Gráfico de barras horizontais exibindo a volumetria de ônibus operando em Curitiba](/assets/densidade_frota.png)

### 2. Distribuição da Frota
![Mapa de região de Curitiba com pinos geográficos categorizados pelo nome das linhas de ônibus](/assets/pinmap.png)

**Nota:** O pipeline captura o estado operacional em quase tempo real. Variações drásticas no volume de dados renderizados nos mapas são esperadas, refletindo picos operacionais (horários comerciais) e recolhimento de frota noturna, além da latência inerente à emissão de sinais GPS dos veículos.

## Como Reproduzir o Projeto
1. Clone este repositório (https://github.com/alissonfluck/urbs-data-pipeline-elt)
2. Crie um arquivo `.env` na raiz com as credenciais do banco e o token da URBS.
3. Suba a infraestrutura `docker compose up -d`.
4. Instale as dependências `pip install -r requirements.txt`.
5. Execute a ingestão `extract_urbs.py`.
6. Acesse `http://localhost:3000` para configurar o Metabase.
