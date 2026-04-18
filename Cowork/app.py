import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# CONFIG
st.set_page_config(
    page_title="Coworxcel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SIDEBAR (NAVEGAÇÃO)
# =========================
st.sidebar.title("Coworxcel")
pagina = st.sidebar.radio(
    "Navegação",
    ["Dashboard", "Sobre"]
)

# =========================
# PÁGINA: SOBRE (mini landing)
# =========================
if pagina == "Sobre":
    st.title("Coworxcel")
    st.subheader("Transforme dados em gráficos em segundos")

    st.markdown("""
    Coworxcel é uma ferramenta que permite gerar gráficos automaticamente a partir de planilhas Excel.

    Ideal para:
    - Analistas
    - Vendedores
    - Pequenos negócios
    - Pessoas que trabalham com dados

    Recursos:
    - Upload de Excel
    - Limpeza automática de dados
    - Geração de gráficos
    - Download em imagem
    """)

    st.markdown("---")
    st.caption("Versão inicial do produto")

# =========================
# PÁGINA: DASHBOARD (APP)
# =========================
if pagina == "Dashboard":

    st.title("Dashboard de Dados")
    st.markdown("Faça upload da sua planilha e gere gráficos automaticamente")

    uploaded_file = st.sidebar.file_uploader(
        "Envie sua planilha Excel",
        type=["xlsx"]
    )

    if uploaded_file:
        try:
            # leitura
            excel = pd.ExcelFile(uploaded_file)
            sheet = st.sidebar.selectbox("Escolha a aba", excel.sheet_names)
            df = excel.parse(sheet)

            # =========================
            # LIMPEZA INTELIGENTE
            # =========================
            df = df.dropna(how='all')
            df.columns = df.columns.str.strip()

            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace(
                        ['', 'nan', 'None', '-', 'N/A'], None
                    )

                df[col] = pd.to_numeric(df[col], errors='ignore')

                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            # =========================
            # LAYOUT
            # =========================
            col1, col2 = st.columns([1, 2])

            # CONFIGURAÇÃO
            with col1:
                st.subheader("Configuração")

                numeric_cols = df.select_dtypes(
                    include=['number']
                ).columns.tolist()
                all_cols = df.columns.tolist()

                if len(numeric_cols) == 0:
                    st.error("Nenhuma coluna numérica encontrada")
                else:
                    x = st.selectbox("Eixo X", all_cols)
                    y = st.selectbox("Eixo Y", numeric_cols)

                    tipo = st.selectbox(
                        "Tipo de gráfico",
                        ["Linha", "Barra", "Dispersão", "Pizza"]
                    )

                    gerar = st.button("Gerar gráfico")

            # RESULTADO
            with col2:
                st.subheader("Visualização")

                st.dataframe(df.head())

                if 'gerar' in locals() and gerar:
                    df_plot = df.dropna(subset=[x, y])

                    fig, ax = plt.subplots()

                    if tipo == "Linha":
                        ax.plot(df_plot[x], df_plot[y])
                    elif tipo == "Barra":
                        ax.bar(df_plot[x], df_plot[y])
                    elif tipo == "Dispersão":
                        ax.scatter(df_plot[x], df_plot[y])
                    elif tipo == "Pizza":
                        data = df_plot.groupby(x)[y].sum().head(10)
                        ax.pie(data, labels=data.index, autopct='%1.1f%%')

                    ax.set_title(f"{y} por {x}")

                    st.pyplot(fig)

                    buffer = BytesIO()
                    fig.savefig(buffer, format="png")
                    buffer.seek(0)

                    st.download_button(
                        label="Baixar gráfico",
                        data=buffer,
                        file_name="grafico.png",
                        mime="image/png"
                    )

        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

    else:
        st.info("Envie uma planilha para começar")

# FOOTER
st.markdown("---")
st.caption("AutoChart • SaaS de visualização de dados")