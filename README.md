# Explorador de Filmes via Wikidata

Este projeto implementa um explorador interativo de filmes baseado em consultas SPARQL à Wikidata, com uma interface construída em Streamlit.

O projeto foi publicado pelo proprio streamlit e a url para acesso sem necessidade de download dos arquivos é: https://exploradorfilmeswikidata.streamlit.app/

## Estrutura do Projeto

```
proj-web-sem/
├── src/
│   ├── app.py          # Interface Streamlit com lógica principal
│   ├── api.py          # Módulo para chamadas à API da Wikidata
│   └── queries.py      # Módulo com as consultas SPARQL
└── static/
    └── images/        
        └── default-image.png  # Imagem padrão para filmes sem poster
```

## Requisitos

- Python 3.7+
- Streamlit
- Pandas
- Requests

## Instalação

1. Clone este repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

Para iniciar a aplicação, execute:

```bash
streamlit run src/app.py
```

## Funcionalidades

- Busca de filmes por título usando consultas SPARQL à Wikidata
- Exibição detalhada de informações dos filmes (título, diretor, ano, gêneros, atores)
- Navegação por diretores e atores relacionados para explorar mais filmes
- Estatísticas de uso com gráficos e métricas das buscas realizadas
- Sistema de histórico e navegação por breadcrumbs

## Arquivos Principais

### app.py

Contém a interface principal do Streamlit com todas as funcionalidades do aplicativo:
- Seções de busca e exibição de resultados
- Funções para manipulação de dados
- Exibição de estatísticas e métricas
- Layout responsivo para exibição de informações dos filmes

### api.py

Implementa a comunicação com o endpoint SPARQL da Wikidata, incluindo:
- Função para execução de consultas SPARQL
- Tratamento de erros e timeouts

### queries.py

Contém os templates de consultas SPARQL utilizados pelo aplicativo:
- Busca de filmes por título
- Busca de filmes por ator
- Busca de filmes por diretor
