%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
# Define o título que aparece na aba do navegador, o ícone e o layout da página
st.set_page_config(
    page_title="Análise de Dengue no Brasil (2023)",
    page_icon="🦟",
    layout="wide"
)

# --- FUNÇÃO DE CARREGAMENTO E CACHE DOS DADOS ---
# Esta função carrega e limpa os dados. O @st.cache_data faz com que ela rode apenas uma vez,
# tornando o app muito mais rápido quando o usuário interage com os filtros.
@st.cache_data
def carregar_dados():
    try:
        # Caminho para o arquivo DENTRO do Google Drive
        caminho_do_arquivo = '/content/drive/MyDrive/mini-projeto/DENGBR23.csv'

        # Lista das colunas que realmente vamos usar
        colunas_para_usar = [
            'ID_MUNICIP', 'SG_UF_NOT', 'CS_SEXO',
            'DT_NOTIFIC', 'NU_IDADE_N', 'CLASSI_FIN', 'CRITERIO'
        ]

        # Lê apenas as colunas necessárias diretamente do seu Drive
        df_dengue = pd.read_csv(
            caminho_do_arquivo, sep=',', encoding='latin-1',
            usecols=colunas_para_usar, on_bad_lines='skip'
        )

        # Processa a coluna de idade para extrair a idade em anos
        df_limpo = df_dengue.copy()
        df_limpo['NU_IDADE_N'] = pd.to_numeric(df_limpo['NU_IDADE_N'], errors='coerce')
        df_limpo.dropna(subset=['NU_IDADE_N'], inplace=True)
        df_limpo = df_limpo[df_limpo['NU_IDADE_N'] >= 4000]
        df_limpo['IDADE'] = df_limpo['NU_IDADE_N'] - 4000
        return df_limpo

    except FileNotFoundError:
        st.error("ERRO: Arquivo 'DENGBR23.csv' não encontrado no Google Drive. Verifique o caminho e as permissões.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
        return None

# --- INTERFACE PRINCIPAL DA APLICAÇÃO ---
st.title("🦟 Dashboard de Análise de Dengue no Brasil - 2023")
st.markdown("Análise interativa dos dados de notificação de Dengue do SINAN, obtidos do Portal Brasileiro de Dados Abertos.")

# Carrega os dados usando a função que criamos
df_analise = carregar_dados()

# Só exibe o conteúdo se os dados foram carregados com sucesso
if df_analise is not None:
    st.header("Distribuição de Casos Notificados por Estado")

    casos_por_estado = df_analise['SG_UF_NOT'].value_counts().reset_index()
    casos_por_estado.columns = ['Estado_Codigo', 'Numero_de_Casos']
    mapa_uf = {
        11:'RO', 12:'AC', 13:'AM', 14:'RR', 15:'PA', 16:'AP', 17:'TO', 21:'MA', 22:'PI',
        23:'CE', 24:'RN', 25:'PB', 26:'PE', 27:'AL', 28:'SE', 29:'BA', 31:'MG', 32:'ES',
        33:'RJ', 35:'SP', 41:'PR', 42:'SC', 43:'RS', 50:'MS', 51:'MT', 52:'GO', 53:'DF'
    }
    casos_por_estado['Estado'] = casos_por_estado['Estado_Codigo'].map(mapa_uf)

    fig = px.bar(
        casos_por_estado.sort_values('Numero_de_Casos', ascending=False),
        x='Estado', y='Numero_de_Casos', title='Casos de Dengue por Estado',
        labels={'Estado': 'Estado', 'Numero_de_Casos': 'Total de Notificações'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cria duas colunas para os gráficos menores
    st.header("Análises Adicionais")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribuição por Sexo")
        casos_sexo = df_analise['CS_SEXO'].value_counts()
        st.bar_chart(casos_sexo)

    with col2:
        st.subheader("Critério de Confirmação")
        casos_criterio = df_analise['CRITERIO'].value_counts()
        st.bar_chart(casos_criterio)

    # Opção para mostrar a tabela de dados
    if st.checkbox("Mostrar tabela de dados limpos"):
        st.dataframe(df_analise)
else:
    st.warning("A aplicação não pode iniciar pois os dados não foram carregados.")
