import streamlit as st
import pdfplumber
import pandas as pd
import io

# Dicionário de correspondência entre CNPJ e nome fantasia
cnpj_para_fantasia = {
    "09.442.132/0004-90": "MAXI LUIZOTE",
    "09.442.132/0005-71": "MAXI CIDADE JARDIM",
    "09.442.132/0007-33": "MAXI MARTINS",
    "09.442.132/0012-09": "MAXI JARAGUA",
    "09.442.132/0001-48": "MAXI CANAA",
    "09.442.132/0002-29": "MAXI PLANALTO",
    "09.442.132/0015-43": "MAXI MANSOUR",
    "09.442.132/0018-96": "MAXI ST INÁCIO",
    "09.442.132/0017-05": "MAXI JD PATRICIA",
    "09.442.132/0022-72": "MAXI PEQUIS",
    "09.442.132/0027-87": "MAXI TUBALINA",
    "09.442.132/0034-06": "MAXI TOCANTINS",
    "09.442.132/0029-49": "MAXI SARAIVA",
    "09.442.132/0011-10": "MAXI SÃO JORGE",
    "09.442.132/0019-77": "MAXI SHOPING PARK",
    "09.442.132/0028-68": "MAXI PAINEIRAS",
    "09.442.132/0033-25": "MAXI SANTA MONICA",
    "09.442.132/0023-53": "MAXI GRANADA",
    "09.442.132/0014-62": "MAXI MORUMBI",
    "09.442.132/0021-91": "MAXI UMUARAMA",
    "09.442.132/0024-34": "MAXI JD BRASILIA",
    "09.442.132/0030-82": "MAXI ROOSEVELT",
    "09.442.132/0008-14": "MAXI APARECIDA",
    "09.442.132/0035-97": "MAXI GRAND VILLE",
    "09.442.132/0031-63": "MAXI CENTRO",
    "09.442.132/0025-15": "MAXI SEGISMUNDO",
    "09.442.132/0003-00": "MAXI CD"
}

ordem_lojas = [
    "MAXI LUIZOTE",
    "MAXI CIDADE JARDIM",
    "MAXI MARTINS",
    "MAXI JARAGUA",
    "MAXI CANAA",
    "MAXI PLANALTO",
    "MAXI MANSOUR",
    "MAXI ST INÁCIO",
    "MAXI JD PATRICIA",
    "MAXI PEQUIS",
    "MAXI TUBALINA",
    "MAXI TOCANTINS",
    "MAXI SARAIVA",
    "MAXI SÃO JORGE",
    "MAXI SHOPING PARK",
    "MAXI PAINEIRAS",
    "MAXI SANTA MONICA",
    "MAXI GRANADA",
    "MAXI MORUMBI",
    "MAXI UMUARAMA",
    "MAXI JD BRASILIA",
    "MAXI ROOSEVELT",
    "MAXI APARECIDA",
    "MAXI GRAND VILLE",
    "MAXI CENTRO",
    "MAXI SEGISMUNDO",
    "MAXI CD"
]

st.title("Extrator de Pedidos SuperMaxi")

uploaded_files = st.file_uploader("Envie um ou mais arquivos PDF", type="pdf", accept_multiple_files=True)

def extrair_tabelas(pdf_file):
    data_rows = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if any("Banana" in (cell or "") for cell in row):
                        data_rows.append(row)
    return data_rows

def processar_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        first_page = pdf.pages[0]
        texto = first_page.extract_text()
        data_entrega = None
        cnpj = None
        if texto:
            for linha in texto.split('\n'):
                if "Dt. Entrega:" in linha:
                    data_entrega = linha.split("Dt. Entrega:")[1].split(",")[0].strip()
                if "CNPJ:" in linha:
                    cnpj = linha.split("CNPJ:")[1].split(",")[0].strip()
        tabela = extrair_tabelas(pdf_file)
        return data_entrega, cnpj, tabela

def formatar_quantidade(valor):
    try:
        if valor is None or valor == "":
            return ""
        return f"{int(float(str(valor).replace(',', '.')))}"
    except:
        return valor

def formatar_bruto(valor):
    try:
        if valor is None or valor == "":
            return ""
        return f"{float(str(valor).replace(',', '.')):.2f}"
    except:
        return valor

def extrair_dados_bananas(tabela):
    tipos = [
        ("Banana Maca", "maçã"),
        ("Banana Prata", "prata"),
        ("Banana Nanica", "nanica"),
        ("Banana Terra", "terra"),
        ("Banana Marmelo", "marmelo"),
    ]
    resultado = {}
    for desc, nome in tipos:
        for row in tabela:
            if desc in (row[3] if len(row) > 3 else ""):
                qtd = row[6] if len(row) > 6 else ""
                unit_bruto = row[9] if len(row) > 9 else ""
                resultado[nome] = (qtd, unit_bruto)
    return resultado

tabela_final = []

if uploaded_files:
    lojas_processadas = {}
    for pdf_file in uploaded_files:
        data_entrega, cnpj, tabela = processar_pdf(pdf_file)
        nome_fantasia = cnpj_para_fantasia.get(cnpj, cnpj or "")
        dados = extrair_dados_bananas(tabela)
        lojas_processadas[nome_fantasia] = {
            "Data de entrega": data_entrega,
            "Loja": nome_fantasia,
            "Qtd Maçã": formatar_quantidade(dados.get("maçã", ("", ""))[0]),
            "Valor Maçã": formatar_bruto(dados.get("maçã", ("", ""))[1]),
            "Qtd Prata": formatar_quantidade(dados.get("prata", ("", ""))[0]),
            "Valor Prata": formatar_bruto(dados.get("prata", ("", ""))[1]),
            "Qtd Nanica": formatar_quantidade(dados.get("nanica", ("", ""))[0]),
            "Valor Nanica": formatar_bruto(dados.get("nanica", ("", ""))[1]),
            "Qtd Terra": formatar_quantidade(dados.get("terra", ("", ""))[0]),
            "Valor Terra": formatar_bruto(dados.get("terra", ("", ""))[1]),
            "Qtd Marmelo": formatar_quantidade(dados.get("marmelo", ("", ""))[0]),
            "Valor Marmelo": formatar_bruto(dados.get("marmelo", ("", ""))[1]),
        }
    # Garante que todas as lojas apareçam na ordem correta
    for loja in ordem_lojas:
        if loja in lojas_processadas:
            tabela_final.append(lojas_processadas[loja])
        else:
            tabela_final.append({
                "Data de entrega": "",
                "Loja": loja,
                "Qtd Maçã": "",
                "Valor Maçã": "",
                "Qtd Prata": "",
                "Valor Prata": "",
                "Qtd Nanica": "",
                "Valor Nanica": "",
                "Qtd Terra": "",
                "Valor Terra": "",
                "Qtd Marmelo": "",
                "Valor Marmelo": "",
            })

    df = pd.DataFrame(tabela_final)

    st.write("Tabela extraída:")
    st.dataframe(df)

    # Download da tabela em Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tabela')
    st.download_button("Baixar tabela em Excel", output.getvalue(), file_name="tabela_bananas.xlsx")
else:
    st.info("Faça upload de um ou mais PDFs para começar.")