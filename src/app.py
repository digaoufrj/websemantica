
# Importações de bibliotecas necessárias e configuração de caminhos.
# O código utiliza streamlit para interface, pandas para análise de dados e
# funções personalizadas de criação de queries e API para consultas SPARQL ao Wikidata.

import streamlit as st
import requests
import json
import re
import sys
import time
import pandas as pd
from datetime import datetime
from collections import Counter
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from src.api import execute_sparql_query
from src.queries import (
    get_film_by_title_query,
    get_films_by_actor_query,
    get_films_by_director_query
)



# Funções para manipulação dos dados que retornam da Wikidata.
# Extraem IDs, removem duplicatas e processam métricas para estatísticas.

def extract_entity_id(url):
    if not url:
        return ""
    
    parts = url.split("/")
    if parts:
        return parts[-1]

def remove_duplicate_films(film_results):
    if not film_results:
        return []
        
    unique_films = {}
    
    for film in film_results:
        if "film" in film and "value" in film["film"]:
            film_url = film["film"]["value"]
            film_qid = extract_entity_id(film_url)
            
            if film_qid not in unique_films:
                unique_films[film_qid] = film
    
    unique_film_list = list(unique_films.values())
    
    if hasattr(st.session_state, 'metrics'):
        for film in unique_film_list:
            process_film_metrics(film)
    
    try:
        unique_film_list.sort(
            key=lambda x: int(x.get("year", {}).get("value", "0")), 
            reverse=True
        )
    except Exception as e:
        print(f"Erro ao ordenar filmes por ano: {e}")
    
    return unique_film_list

def process_film_metrics(film):
    if "filmName" in film and "value" in film["filmName"]:
        st.session_state.metrics["filmes_encontrados"].append(film["filmName"]["value"])
    
    if "year" in film and "value" in film["year"]:
        st.session_state.metrics["anos_filmes"].append(film["year"]["value"])
    
    if "directorName" in film and "value" in film["directorName"]:
        st.session_state.metrics["diretores"].append(film["directorName"]["value"])
    
    if "genres" in film and "value" in film["genres"]:
        generos = film["genres"]["value"].split(", ")
        st.session_state.metrics["generos"].append(generos)
    
    if "actorTuples" in film and "value" in film["actorTuples"]:
        actor_tuples = film["actorTuples"]["value"].split(" | ")
        atores = []
        for actor_tuple in actor_tuples:
            match = re.match(r"\(([^,]+),.*\)", actor_tuple)
            if match:
                atores.append(match.group(1))
        st.session_state.metrics["atores"].append(atores)



#Funções para estilização da interface e exibição de estatísticas.
#Definem o visual dos cards de filmes e apresentam métricas de uso.

def apply_card_styling():
    st.markdown("""
    <style>
    .film-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    .film-title {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)


def exibir_estatisticas():
    st.markdown("""
    <style>
    .stats-container {
        background-color: #262730;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #4e5d6c;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stats-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="stats-container">
        <div class="stats-header">
            <h2>Estatísticas do Explorador de Filmes</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Métricas Gerais")
        st.metric("Total de Buscas", st.session_state.metrics["busca_count"])
        st.metric("Total de Filmes Encontrados", len(st.session_state.metrics["filmes_encontrados"]))
        
        if st.session_state.metrics["filmes_por_consulta"]:
            media_filmes = sum(st.session_state.metrics["filmes_por_consulta"]) / len(st.session_state.metrics["filmes_por_consulta"])
            st.metric("Média de Filmes por Consulta", f"{media_filmes:.1f}")
        
        st.metric("Cliques em Atores", st.session_state.metrics["cliques_atores"])
        st.metric("Cliques em Diretores", st.session_state.metrics["cliques_diretores"])
        
        duracao = datetime.now() - st.session_state.metrics["inicio_sessao"]
        minutos = duracao.seconds // 60
        segundos = duracao.seconds % 60
        st.metric("Duração da Sessão", f"{minutos} min {segundos} seg")
    
    with col2:
        if st.session_state.metrics["anos_filmes"]:
            st.subheader("Distribuição de Anos dos Filmes")
            anos = pd.Series(st.session_state.metrics["anos_filmes"]).astype(int)
            
            decadas = (anos // 10 * 10)
            contagem_decadas = Counter(decadas)
            
            decadas_ordenadas = sorted(contagem_decadas.keys())
            valores = [contagem_decadas[d] for d in decadas_ordenadas]
            
            df_decadas = pd.DataFrame({
                'Década': [str(d) for d in decadas_ordenadas],
                'Filmes': valores
            })
            st.bar_chart(df_decadas.set_index('Década'))
    
    if st.session_state.metrics["diretores"]:
        st.subheader("Diretores Mais Frequentes")
        diretores_counter = Counter(st.session_state.metrics["diretores"])
        top_diretores = diretores_counter.most_common(5)
        
        df_diretores = pd.DataFrame(top_diretores, columns=['Diretor', 'Aparições'])
        st.table(df_diretores)
        
    if st.session_state.metrics["atores"]:
        st.subheader("Atores Mais Frequentes")
        todos_atores = [a for sublist in st.session_state.metrics["atores"] for a in sublist if a]
        atores_counter = Counter(todos_atores)
        top_atores = atores_counter.most_common(5)
        
        df_atores = pd.DataFrame(top_atores, columns=['Ator', 'Aparições'])
        st.table(df_atores)
    
    if st.session_state.metrics["generos"]:
        st.subheader("Gêneros Mais Comuns")
        todos_generos = [g for sublist in st.session_state.metrics["generos"] for g in sublist if g]
        generos_counter = Counter(todos_generos)
        top_generos = generos_counter.most_common(5)
        
        df_generos = pd.DataFrame(top_generos, columns=['Gênero', 'Contagem'])
        st.bar_chart(df_generos.set_index('Gênero'))



#Função principal para exibição de informações de um filme.
#Cria um layout com título, ano, diretor, imagem, gêneros e atores,
#com botões interativos para exploração relacionada.

def display_film(film_data, show_divider=True, index=0):
    if show_divider:
        st.divider()
    
    film_name = film_data["filmName"]["value"] if "filmName" in film_data else "Desconhecido"
    film_url = film_data["film"]["value"] if "film" in film_data else ""
    film_id = extract_entity_id(film_url)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(film_name)
        
        if "year" in film_data:
            st.write(f"**Ano:** {film_data['year']['value']}")
        
        st.caption(f"ID Wikidata: {film_id}")
        
        if "director" in film_data and "directorName" in film_data:
            director_url = film_data["director"]["value"]
            director_name = film_data["directorName"]["value"]
            director_id = extract_entity_id(director_url)
            
            st.write("**Diretor:** (clique para explorar outros projetos do diretor)")
            director_button_key = f"director_{director_id}_{film_id}_{index}"
            
            if st.button(f"{director_name}", key=director_button_key, type="secondary"):
                st.session_state.recommendation_type = "director"
                st.session_state.entity_id = director_id
                st.session_state.entity_name = director_name
                
                st.session_state.metrics["cliques_diretores"] += 1
                
                st.session_state.search_history.append({
                    "type": "director",
                    "id": director_id,
                    "name": director_name,
                    "title": f"Explorando filmes de {director_name}"
                })
                st.rerun()
    
    with col2:
        if "displayImage" in film_data:
            st.image(film_data["displayImage"]["value"], width=150)
        else:
            st.image("static/images/default-image.png", width=150)
        
    if "genres" in film_data:
        st.write("**Gêneros:**")
        genres = film_data["genres"]["value"].split(", ")
        unique_genres = []
        for genre in genres:
            if genre not in unique_genres:
                unique_genres.append(genre)
        
        genre_cols = st.columns(min(len(unique_genres), 4))
        
        for i, genre in enumerate(unique_genres):
            col_idx = i % len(genre_cols)
            with genre_cols[col_idx]:
                st.write(genre)
    
    if "actorTuples" in film_data:
        st.write("**Actors:** (clique nos nomes para explorar a filmografia de cada ator)")
        actor_tuples = film_data["actorTuples"]["value"].split(" | ")
        
        actors_data = []
        
        num_actors = len(actor_tuples)
        num_rows = (num_actors + 3) // 4
        
        for row in range(num_rows):
            cols = st.columns(4)
            for col_idx in range(4):
                actor_idx = row * 4 + col_idx
                if actor_idx < num_actors:
                    actor_tuple = actor_tuples[actor_idx]
                    match = re.match(r'\(([^,]+), (Q\d+)\)', actor_tuple)
                    if match:
                        actor_name, actor_qid = match.groups()
                        with cols[col_idx]:
                            if st.button(f"{actor_name}", key=f"actor_{actor_qid}_{film_id}_{index}_{col_idx}", type="secondary"):
                                st.session_state.recommendation_type = "actor"
                                st.session_state.entity_id = actor_qid
                                st.session_state.entity_name = actor_name
                                
                                st.session_state.metrics["cliques_atores"] += 1
                                
                                st.session_state.search_history.append({
                                    "type": "actor",
                                    "id": actor_qid,
                                    "name": actor_name,
                                    "title": f"Explorando a filmografia de {actor_name}"
                                })
                                st.rerun()



#Configuração inicial da página e inicialização das variáveis de estado.
#Define as configurações da interface e inicializa o armazenamento de dados para a sessão do usuário.

st.set_page_config(
    page_title="Explorador de Filmes via Wikidata", 
    page_icon="🎥",
    layout="wide"
)

apply_card_styling()

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "exploration_type" not in st.session_state:
    st.session_state.exploration_type = None
    
if "recommendation_type" not in st.session_state:
    st.session_state.recommendation_type = None

if "entity_id" not in st.session_state:
    st.session_state.entity_id = None

if "entity_name" not in st.session_state:
    st.session_state.entity_name = None

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "busca_count": 0,
        "filmes_encontrados": [],
        "anos_filmes": [],
        "diretores": [],
        "atores": [],
        "generos": [],
        "inicio_sessao": datetime.now(),
        "cliques_atores": 0,
        "cliques_diretores": 0,
        "filmes_por_consulta": []
    }

if "show_stats_toggle" not in st.session_state:
    st.session_state.show_stats_toggle = False



def toggle_stats():
    st.session_state.show_stats_toggle = not st.session_state.show_stats_toggle



#Layout principal da interface com título e botão de estatísticas.
#Cria o cabeçalho do aplicativo e apresenta navegação quando necessário.

col_titulo, col_espacador, col_botao = st.columns([6, 1, 2])

with col_titulo:
    st.title("Explorador de Filmes via Wikidata")

with col_botao:
    st.button("📊 Estatísticas", key="stats_button", type="secondary", on_click=toggle_stats, use_container_width=True)

if st.session_state.get("show_stats_toggle", False):
    exibir_estatisticas()

if st.session_state.search_history:
    breadcrumb = "Início"
    for i, item in enumerate(st.session_state.search_history):
        breadcrumb += f" > {item['title']}"
    st.markdown(f"**Navegação:** {breadcrumb}")



#Seção de busca para encontrar filmes por título.
#Apresenta um campo de texto e botão para buscar filmes no Wikidata, processando e exibindo os resultados encontrados.

if not st.session_state.recommendation_type:
    st.markdown("<h3 style='color: white;'>Digite o nome de um filme que você já viu e explore informações como elenco, diretor, ano e gênero.</h3>", unsafe_allow_html=True)
    st.markdown("<span style='font-size: 0.9em; color: #EED202;'>Atenção: Digite o nome do filme em inglês, respeitando letras maiúsculas e pontuação.</span>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        film_title = st.text_input("Digite o título do filme", key="film_title", autocomplete="off")
        
        if st.button("Buscar", key="search_button", use_container_width=True) and film_title:
            with st.spinner('Buscando filmes...'):
                try:
                    query = get_film_by_title_query(film_title)
                    results = execute_sparql_query(query)
                    
                    if results and "results" in results and "bindings" in results["results"] and results["results"]["bindings"]:
                        st.session_state.metrics["busca_count"] += 1
                        
                        num_filmes = len(results["results"]["bindings"])
                        st.session_state.metrics["filmes_por_consulta"].append(num_filmes)
                        unique_films = remove_duplicate_films(results["results"]["bindings"])
                        st.session_state.search_results = unique_films
                        st.success(f"Encontrados {len(unique_films)} filmes para '{film_title}'")
                    else:
                        st.error(f"Nenhum filme encontrado com o título '{film_title}'")
                        st.session_state.search_results = []
                except Exception as e:
                    st.error(f"Erro ao buscar filmes: {str(e)}. Tempo limite excedido ou serviço indisponível.")
                    st.session_state.search_results = []



#Seção de exibição de recomendações baseadas em ator ou diretor.
#Busca e apresenta filmes relacionados à entidade selecionada, utilizando cache para melhorar a performance.

if st.session_state.recommendation_type and st.session_state.entity_name:
    current_item = st.session_state.search_history[-1] if st.session_state.search_history else None
    
    if current_item:
        st.subheader(current_item['title'])
    else:
        st.subheader(f"Explorando filmes com {st.session_state.entity_name}")
    
    if st.button("Retornar ao explorador de filmes", key="return_to_search", type="primary"):
        st.session_state.recommendation_type = None
        st.session_state.entity_id = None
        st.session_state.entity_name = None
        st.session_state.search_results = []
        st.session_state.search_history = []
        st.rerun()
    
    cache_key = f"{st.session_state.recommendation_type}_{st.session_state.entity_id}"
    
    if "query_cache" not in st.session_state:
        st.session_state.query_cache = {}
    
    if cache_key in st.session_state.query_cache and st.session_state.search_results:
        results = st.session_state.query_cache[cache_key]
        unique_films = st.session_state.search_results
    else:
        with st.spinner('Carregando filmes...'):
            try:
                if st.session_state.recommendation_type == "actor":
                    query = get_films_by_actor_query(st.session_state.entity_id)
                elif st.session_state.recommendation_type == "director":
                    query = get_films_by_director_query(st.session_state.entity_id)
                else:
                    query = None
                
                if query:
                    results = execute_sparql_query(query)
                    st.session_state.query_cache[cache_key] = results
                    
                    if results and "results" in results and "bindings" in results["results"] and results["results"]["bindings"]:
                        process_film_metrics(results["results"]["bindings"])
                        
                        unique_films = remove_duplicate_films(results["results"]["bindings"])
                        st.session_state.search_results = unique_films
                        
                        st.session_state.metrics["busca_count"] += 1
                        
                        num_filmes = len(unique_films)
                        st.session_state.metrics["filmes_por_consulta"].append(num_filmes)
                        
                        st.success(f"Encontrados {len(unique_films)} filmes")
                    else:
                        st.error(f"Nenhum filme encontrado com {st.session_state.entity_name}")
                        st.session_state.search_results = []
                else:
                    st.error("Tipo de exploração inválido")
                    st.session_state.search_results = []
            except Exception as e:
                st.error(f"Erro ao carregar dados: {str(e)}. Tempo limite excedido ou serviço indisponível.")
                st.session_state.recommendation_type = None
                st.session_state.entity_id = None
                st.session_state.entity_name = None
                st.session_state.search_results = []
                st.session_state.search_history = []



#Exibição dos resultados da busca ou recomendações.
#Percorre a lista de filmes e exibe cada um usando a função display_film.

if "search_results" in st.session_state and st.session_state.search_results:
    for i, film_data in enumerate(st.session_state.search_results):
        display_film(film_data, i > 0, i)
