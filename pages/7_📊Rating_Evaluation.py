import streamlit as st
import pandas as pd
from reportRating2PDF import UpdRepRatingPdf
import json
import os
import base64

import numpy as np

st.set_page_config(page_title="Rating Assessment", layout="wide")
st.title("📊 Rating Assessment")

with st.expander("🆘 Help"):
    st.markdown("""
    - **What to do here?**  
      This module gives you a first evaluation of rating comparing for each temperature preliminarly defined the allowable pressures of piping and component groups. 
      In the last two columns You can find the minimum rating and the corresponding group (Pipe or Cmp). 
                                           

    """)

#    === Controllo accesso ===
if 'prot' not in st.session_state:
    st.session_state.prot = False
    
if st.session_state.prot == False:
    st.info('unauthorized access')
    st.stop()

# === Lettura file CSV ===
sessionDir = "sessions"
fileTemperatures = os.path.join(sessionDir, f"Temperatures_{st.session_state.session_id}.csv")

df_temp = pd.read_csv(fileTemperatures, sep=";")
df_temp["TempF"] = pd.to_numeric(df_temp["TempF"].astype(str).str.replace(",", "."), errors="coerce")
#df_temp["TempF"] = df_temp["TempF"].astype(int)
df_temp["TempC"] = df_temp["TempC"].str.replace(",", ".").astype(float)

fileCmpGroups = os.path.join(sessionDir, f"comp_groups_{st.session_state.session_id}.csv")
df_groups = pd.read_csv(fileCmpGroups)
df_rating = pd.read_csv("files/Rating.csv", sep=";")

# === Inizializza tabella dei risultati con TempF e TempC ===
df_result = df_temp.copy()

# === Funzione di interpolazione e conversione ===
def interpolated_pressure(temp, id_, rating_col):
    df_r = df_rating[df_rating["id"] == id_][["TempF", rating_col]].dropna()
    df_r = df_r.sort_values("TempF")

    temps = df_r["TempF"].values
    pressures = df_r[rating_col].values

    if temp > temps.max():
        return np.nan  # Fuori intervallo massimo ⇒ valore escluso
    else:
        # Interpolazione lineare + conversione psi → bar
        interpolated = np.interp(temp, temps, pressures)
        return round(interpolated * 0.0689476, 2)

# === Calcolo pressioni per ciascun gruppo ===
for idx, row in df_groups.iterrows():
    comp_name = row["Comp_Group"]
    comp_id = row["id"]
    comp_rating = row["Rating"]
    rating_col = f"R_{comp_rating}"

    # Verifica che la colonna esista nel file Rating
    if rating_col not in df_rating.columns:
        st.warning(f"⚠️ Rating {rating_col} not found for {comp_name}")
        continue

    # Calcola le pressioni interpolando + convertendo in bar
    pressioni = df_temp["TempF"].apply(lambda T: interpolated_pressure(T, comp_id, rating_col))
    #df_result[f"Press {comp_name}"] = pressioni    # valori in bar
    df_result[comp_name] = pressioni    # valori in bar

# GRUPPI PIPING ------------------------------------------------------------------
# calcola MAWP per ogni gruppo piping per ogni temperatura del file Temperature

# Carica la tabella degli ammissibili

allowables_df = pd.read_csv("files/Piping_Allowables.csv", delimiter=";")
allowables_df.columns = allowables_df.columns.str.strip()
allowables_df["Pipe_description"] = allowables_df["Pipe_description"].str.strip()

#  Conversione da psi a MPa
allowables_df["AllowMPa"] = allowables_df["AllowPsi"] * 0.00689476



# Carica rating e variabili piping per ogni gruppo
filegroupRatingInfo = os.path.join(sessionDir, f"groupRatingInfo_{st.session_state.session_id}.json")
with open(filegroupRatingInfo, "r") as f:
    rating_data = json.load(f)

for group_name, values in rating_data.items():   
    
    # Recupera materiale
    material = values.get("Material", "").strip()
    if not material:
        st.warning(f"⚠️ Material not defined for {group_name}")
        continue

    # Filtra righe corrispondenti a questo materiale
    mat_df = allowables_df[allowables_df["Pipe_description"] == material]
    if mat_df.empty:
        st.warning(f"⚠️ Material '{material}' not found in Piping_Allowables.csv")
        continue

    # Serie per interpolazione: TempF → AllowMPa
    mat_df = mat_df.sort_values("TempF")
    series_interp = pd.Series(data=mat_df["AllowMPa"].values, index=mat_df["TempF"].values).interpolate()

    pressures = []
    for _, rowT in df_temp.iterrows():
        TempF = rowT["TempF"]

        min_temp = mat_df["TempF"].min()
        max_temp = mat_df["TempF"].max()

        if TempF < min_temp or TempF > max_temp:
            pressures.append(None)
            continue

        allow = np.interp(
            TempF,
            mat_df["TempF"].values,
            mat_df["AllowMPa"].values
        )

        thkCom = values["thkCom_rating"]
        CA = values["CA_rating"]
        c = values["c_rating"]
        TOL = values["TOL_rating"]
        code_toll = values["codeTol"]

        D_mm = float(values["OD"])
        E = values["E_rating"]
        W = values["W_rating"]
        A = allow
        Y = 0.4  # oppure prendi da values se disponibile


        # Calcolo t in base al tipo di tolleranza
        if code_toll <= 4:
            t = ((100-TOL)/100)*thkCom - CA - c     #TOL in % per codici toll <= 4
        else:
            t = thkCom - CA - c - TOL  # TOL in mm per codici toll > 4

        if t <= 0 or (D_mm - 2 * t * (TOL / 100 if code_toll <= 4 else 1)) <= 0:
            MAWP_bar = 0.0
        else:
            denom = D_mm - 2 * t * (TOL / 100 if code_toll <= 4 else 1)
            MAWP_bar = (2 * t * A * E * W) / denom *10  # conversione da MPa a bar: x10




        pressures.append(round(MAWP_bar, 2))


    # Aggiunge la colonna al risultato
    #df_result[group_name] = pressures
    df_result [f"Pipe_{group_name}"] = pressures
    #print("group:", group_name, Material, thkCom)

# Seleziona solo le colonne dei gruppi (escludi TempF e TempC)
group_columns = [col for col in df_result.columns if col not in ["TempF", "TempC"]]

# Colonna "Rating": minimo delle pressioni per ogni temperatura
df_result["Rating"] = df_result[group_columns].min(axis=1, skipna=True)

# Colonna "Gr": nome del gruppo che ha prodotto il valore minimo
# Se tutte le colonne in una riga sono NaN, metti np.nan anche per "Gr"
df_result["Gr"] = df_result[group_columns].apply(
    lambda row: row.idxmin(skipna=True) if row.notna().any() else np.nan, axis=1
)

# === Visualizzazione risultati ===
st.markdown("### Pressure Ratings by Temperature")  # Pressure in bar
st.dataframe(df_result, hide_index=True)

# === Salvataggio ===
# if st.button("💾 Save as CSV"):
filePressTemp = os.path.join(sessionDir, f"pressures_by_temperature_{st.session_state.session_id}.csv")
df_result.to_csv(filePressTemp, index=False)
st.success("✅ Calculation updated")


# Print Piping Group Report  - PDF
# Aggiungi pulsante di Genera Report 2.pdf
UpdRepRatingPdf()
#st.sidebar.info("Report created !")
# Aggiungi pulsante di download report1.pdf
pdfReport  = os.path.join(sessionDir, f"report2_{st.session_state.session_id}.pdf")

# st.title("📄 Anteprima del Report PDF")

# Inizializza lo stato se non esiste
if "show_pdf" not in st.session_state:
    st.session_state.show_pdf = False

def toggle_pdf():
    st.session_state.show_pdf = not st.session_state.show_pdf

# Separatore linea rossa
st.markdown(
    """
    <hr style="border: 0.5px solid red;">
    """,
    unsafe_allow_html=True
)
#st.markdown("---")

# Un solo pulsante con key e callback
label = "👁️ Preview Report" if not st.session_state.show_pdf else "❌ Close Preview"
st.button(label, on_click=toggle_pdf, key="toggle_pdf_btn")

# Visualizza PDF se attivo
if st.session_state.show_pdf:
    with open(pdfReport, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

# Separatore linea rossa
st.markdown(
    """
    <hr style="border: 1px solid red;">
    """,
    unsafe_allow_html=True
)
#st.markdown("---")

# Pulsante per scaricare il PDF
   
with open(pdfReport, "rb") as pdf_file:
    #pdf_data = pdf_file.read()

    st.sidebar.download_button(
        label="💾 Download Report Rating",
        data=pdf_file,
        file_name="ReportRating.pdf",
        mime="application/pdf",
        help= '***Save Report in your local drive***'
    )
    


