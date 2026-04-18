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
st.markdown("# coworxcel")
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
        # =========================
        # LEITURA DO EXCEL
        # =========================
        excel = pd.ExcelFile(uploaded_file)
        sheet = st.sidebar.selectbox("Escolha a aba", excel.sheet_names)

        df = excel.parse(sheet)  # 🔥 df nasce aqui

        # =========================
        # LIMPEZA SEGURA
        # =========================
        df = df.dropna(how='all')
        df.columns = df.columns.astype(str).str.strip()

        for col in df.columns:

            # limpar strings
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(['', 'nan', 'None', '-', 'N/A'], None)

                # tentar converter para número (BR)
                try:
                    temp = df[col].str.replace('.', '', regex=False)
                    temp = temp.str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(temp)
                except:
                    pass

            # tentar converter para data apenas se ainda for texto
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

        # =========================
        # LAYOUT
        # =========================
        col1, col2 = st.columns([1, 2])

        # ===== CONFIG =====
        with col1:
            st.subheader("Configuração")

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            all_cols = df.columns.tolist()

            if len(numeric_cols) == 0:
                st.error("Nenhuma coluna numérica encontrada na planilha")
            else:
                x = st.selectbox("Coluna base (eixo X)", all_cols)
                y = st.selectbox("Coluna de valores (eixo Y)", numeric_cols)

                tipo = st.selectbox(
                    "Tipo de gráfico",
                    ["Linha", "Barra", "Dispersão", "Pizza"]
                )

                gerar = st.button("Gerar gráfico")

        # ===== RESULTADO =====
        with col2:
            st.subheader("Visualização")

            st.dataframe(df.head())

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
st.caption("coworxcel • dashboard de dados")
