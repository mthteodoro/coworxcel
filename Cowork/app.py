# =========================
# LIMPEZA INTELIGENTE SEGURA
# =========================

df = df.dropna(how='all')
df.columns = df.columns.str.strip()

for col in df.columns:

    # limpar strings
    if df[col].dtype == 'object':
        df[col] = df[col].astype(str).str.strip()

        # tratar valores inválidos
        df[col] = df[col].replace(['', 'nan', 'None', '-', 'N/A'], None)

        # tentar converter para número (com padrão BR)
        try:
            temp = df[col].str.replace('.', '', regex=False)
            temp = temp.str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(temp)
        except:
            pass

    # tentar converter para data APENAS se ainda for texto
    if df[col].dtype == 'object':
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass
