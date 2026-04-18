import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Coworxcel", layout="wide")

# =========================
# HEADER
# =========================
st.markdown("# Coworxcel")
st.markdown("### Transforme planilhas em gráficos automaticamente")
st.markdown("---")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Configuração")

uploaded_file = st.sidebar.file_uploader(
    "Envie sua planilha Excel",
    type=["xlsx"]
)

# =========================
# APP
# =========================
if uploaded_file:
    try:
        # LEITURA
        excel = pd.ExcelFile(uploaded_file)
        sheet = st.sidebar.selectbox("Escolha a aba", excel.sheet_names)
        df = excel.parse(sheet)

        # =========================
        # LIMPEZA
        # =========================
        df = df.dropna(how='all')

        # 🔥 CORREÇÃO DE COLUNAS "UNNAMED"
        new_columns = []
        for i, col in enumerate(df.columns):
            col_str = str(col).strip()

            if col_str == "" or "Unnamed" in col_str:
                new_columns.append(f"Coluna_{i+1}")
            else:
                new_columns.append(col_str)

        df.columns = new_columns

        # =========================
        # TRATAMENTO DE DADOS
        # =========================
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(['', 'nan', 'None', '-', 'N/A'], None)

                # tentar converter padrão BR
                try:
                    temp = df[col].str.replace('.', '', regex=False)
                    temp = temp.str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(temp)
                except:
                    pass

            # tentar converter para data
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

        # =========================
        # LAYOUT
        # =========================
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Configuração")

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            all_cols = df.columns.tolist()

            # =========================
            # MODO TEXTO
            # =========================
            if len(numeric_cols) == 0:
                st.warning("Nenhuma coluna numérica encontrada. Modo análise de texto ativado.")

                col_text = st.selectbox("Escolha uma coluna para análise", all_cols)
                gerar_texto = st.button("Analisar dados")

            # =========================
            # MODO NUMÉRICO
            # =========================
            else:
                x = st.selectbox("Coluna base (eixo X)", all_cols)
                y = st.selectbox("Coluna de valores (eixo Y)", numeric_cols)

                tipo = st.selectbox(
                    "Tipo de gráfico",
                    ["Linha", "Barra", "Dispersão", "Pizza"]
                )

                gerar = st.button("Gerar gráfico")

        # =========================
        # RESULTADO
        # =========================
        with col2:
            st.subheader("Visualização")
            st.dataframe(df.head())

            # ===== MODO TEXTO =====
            if len(numeric_cols) == 0:
                if 'gerar_texto' in locals() and gerar_texto:
                    contagem = df[col_text].value_counts().reset_index()
                    contagem.columns = [col_text, "Quantidade"]

                    st.dataframe(contagem)

                    fig = px.bar(contagem, x=col_text, y="Quantidade")

                    fig.update_layout(
                        template="plotly_dark",
                        title=f"Distribuição de {col_text}"
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # ===== MODO NUMÉRICO =====
            else:
                if 'gerar' in locals() and gerar:
                    df_plot = df.dropna(subset=[x, y])

                    if tipo == "Linha":
                        fig = px.line(df_plot, x=x, y=y)

                    elif tipo == "Barra":
                        fig = px.bar(df_plot, x=x, y=y)

                    elif tipo == "Dispersão":
                        fig = px.scatter(df_plot, x=x, y=y)

                    elif tipo == "Pizza":
                        data = df_plot.groupby(x)[y].sum().reset_index()
                        fig = px.pie(data, names=x, values=y)

                    fig.update_layout(
                        template="plotly_dark",
                        title=f"{y} por {x}"
                    )

                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

else:
    st.info("Envie uma planilha na barra lateral para começar")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Coworxcel • Dashboard inteligente de planilhas")
