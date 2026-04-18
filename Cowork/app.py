import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AutoChart",
    layout="wide"
)

# =========================
# HEADER
# =========================
st.markdown("# AutoChart")
st.markdown("### Visualize dados de forma simples e rápida")
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
# MAIN
# =========================
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
        # LAYOUT DASHBOARD
        # =========================
        col1, col2 = st.columns([1, 2])

        # ===== CONFIG =====
        with col1:
            st.subheader("Configuração do gráfico")

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            all_cols = df.columns.tolist()

            if len(numeric_cols) == 0:
                st.error("Nenhuma coluna numérica encontrada")
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

                # download
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
    st.info("Envie uma planilha na barra lateral para começar")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("AutoChart • Ferramenta de visualização de dados")
