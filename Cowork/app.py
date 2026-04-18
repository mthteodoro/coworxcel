import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AutoChart",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS CUSTOM (PREMIUM LOOK)
# =========================
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: #ffffff;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
    padding: 10px;
    font-weight: bold;
}
.stSelectbox label {
    color: #cccccc;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("AutoChart")
st.sidebar.markdown("Visualização de dados inteligente")

uploaded_file = st.sidebar.file_uploader(
    "Envie sua planilha",
    type=["xlsx"]
)

# =========================
# HEADER
# =========================
st.title("AutoChart")
st.markdown("### Transforme dados em decisões em segundos")

# =========================
# APP
# =========================
if uploaded_file:
    try:
        excel = pd.ExcelFile(uploaded_file)
        sheet = st.sidebar.selectbox("Escolha a aba", excel.sheet_names)
        df = excel.parse(sheet)

        # =========================
        # LIMPEZA
        # =========================
        df = df.dropna(how='all')
        df.columns = df.columns.str.strip()

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(['', 'nan', 'None', '-', 'N/A'], None)

            df[col] = pd.to_numeric(df[col], errors='ignore')

            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        # =========================
        # LAYOUT
        # =========================
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("## Configuração")

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
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

        with col2:
            st.markdown("## Visualização")

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
        st.error(f"Erro: {e}")

else:
    st.markdown("""
    ### Comece agora

    1. Envie sua planilha no menu lateral  
    2. Escolha os dados  
    3. Gere gráficos automaticamente  

    """)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("AutoChart • Data Visualization SaaS")
