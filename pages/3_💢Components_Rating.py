import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Flange Rating Viewer")
st.title("💢 Components Pressure Rating")
st.subheader("acc. to ASME B16.34 and B16.5 - 2025 ")

#    === Controllo accesso ===
if 'prot' not in st.session_state:
    st.session_state.prot = False
    
if st.session_state.prot == False:
    st.info('unauthorized access')
    st.stop()
    

st.markdown(
    "<h6 style='color:red; font-weight:normal;'>=== Read-only access for viewing and querying ===</h6>",
    unsafe_allow_html=True
)

# --- STEP 1: Caricamento file dati statici ---
df_desc = pd.read_csv("files/Rating_Desc.csv", sep= ";")  # contiene colonne: id, Cmp_material
df_rating = pd.read_csv("files/Rating.csv", sep= ";")     # contiene colonne: id, TempF, R_150, ...

#st.write("Colonne presenti in Rating_Desc.csv:", df_desc.columns.tolist())

# Normalizza le intestazioni (rimuove spazi e uniforma maiuscole)
df_desc.columns = df_desc.columns.str.strip().str.lower()

# --- STEP 2: Selectbox per materiale ---

if "cmp_material" in df_desc.columns:
    materiali = df_desc["cmp_material"].dropna().unique()
    materiale_scelto = st.selectbox("Select material:", materiali)

    # Trova l'id corrispondente
    id_scelto = df_desc[df_desc["cmp_material"] == materiale_scelto]["id"].values[0]
else:
    st.error("❌ Colonna 'cmp_material' non trovata anche dopo pulizia intestazioni.")

# Trova l'id corrispondente
#id_scelto = df_desc[df_desc["cmp_material"] == materiale_scelto]["id"].values[0]

# --- STEP 3: Filtra i dati di pressione ---
df_filtrato = df_rating[df_rating["id"] == id_scelto].copy()

# Converti TempF → TempC
df_filtrato["Temp_°C"] = ((df_filtrato["TempF"] - 32) * 5/9).round(1)

# Elenco colonne da convertire (psi → MPa)
colonne_rating = ["R_150", "R_300", "R_400", "R_600", "R_900", "R_1500", "R_2500", "R_4500"]
psi_to_bar = 0.0689476

for col in colonne_rating:
    df_filtrato[col] = (df_filtrato[col] * psi_to_bar).round(2)

# Riorganizza le colonne
colonne_mostrata = ["Temp_°C"] + colonne_rating
df_finale = df_filtrato[colonne_mostrata].sort_values("Temp_°C")

# --- STEP 4: Visualizza la tabella ---
st.write(f"Pressure ratings for **{materiale_scelto}** (in bar):")
st.dataframe(df_finale, use_container_width=True, hide_index= True)


# --- Input temperatura da interpolare ---
temp_input = st.number_input(
    "🔢 Input temperature in °C for interpolation:",
    min_value=float(df_finale["Temp_°C"].min()),
    max_value=float(df_finale["Temp_°C"].max()),
    step=1.0
)

# --- Interpolazione lineare per ogni colonna ---
df_interp = df_finale.set_index("Temp_°C").sort_index()

# Funzione di interpolazione su tutta la colonna
def interp_col(colname):
    x = df_interp.index.values  # temperature in °C
    y = df_interp[colname].values
    return np.interp(temp_input, x, y)

# Applica interpolazione a tutte le colonne di rating
risultati = {
    col: round(interp_col(col), 2)
    for col in df_interp.columns
}


# --- Costruisci la tabella con una sola riga ---
df_riga_unica = pd.DataFrame([risultati])
df_riga_unica.insert(0, "Temp_°C", round(temp_input, 1))  # Inserisce la colonna temperatura all'inizio

# --- Mostra la tabella ---
st.markdown(f"### 📈 Interpolated Pressure Values (bar) at {temp_input:.1f} °C:")

st.dataframe(df_riga_unica, use_container_width=True, hide_index= True)
