import streamlit as st
from elasticsearch import Elasticsearch

# Configuração da página
st.set_page_config(
    page_title="Busca TREC-COVID (BM25)", 
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Sistema de Busca TREC-COVID Round 1")
st.subheader("Modelo BM25 com Elasticsearch")
st.write("Esta interface executa consultas sobre a coleção TREC-COVID utilizando o motor de busca Elasticsearch configurado com o modelo **BM25**.")

# Inicialização da conexão com o Elasticsearch + Streamlit
try:
    es = Elasticsearch(
        st.secrets["ELASTIC_ENDPOINT"],
        api_key=st.secrets["ELASTIC_API_KEY"]
    )
except Exception as e:
    st.error(f"Erro ao conectar ao Elasticsearch: {e}")

# Campo de texto para a consulta do utilizador
query_text = st.text_input("Digite a sua consulta em inglês (ex: 'coronavirus origin', 'covid-19 vaccine'):", value="coronavirus origin")

if st.button("Buscar") or query_text:
    if query_text.strip():
        # Consulta executando o algoritmo BM25 padrão nos campos de título e resumo
        search_query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["title^2", "abstract"],  # Ponderação maior para o título
                    "type": "best_fields"
                }
            }
        }
        
        try:
            response = es.search(index="trec-covid-bm25", body=search_query, size=10)
            hits = response["hits"]["hits"]
            
            st.markdown(f"### Resultados Encontrados ({len(hits)} apresentados)")
            
            for i, hit in enumerate(hits, 1):
                score = hit["_score"]
                doc_id = hit["_id"]
                source = hit["_source"]
                
                with st.expander(f"#{i} — {source.get('title', 'Sem título')} (Score BM25: {score:.4f})"):
                    st.write(f"**ID do Documento:** `{doc_id}`")
                    st.write(f"**Resumo (Abstract):** {source.get('abstract', 'Resumo indisponível.')}")
        except Exception as e:
            st.error(f"Erro ao realizar a busca no Elasticsearch: {e}")
