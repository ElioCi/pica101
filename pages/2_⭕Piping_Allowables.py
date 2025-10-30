import streamlit as st
import pandas as pd
import csv

# Titolo dell'applicazione
st.set_page_config(page_title="Piping_Allowables")
st.title('⭕Piping materials allowables')
st.subheader('acc. to ASME B31.3 - 2024')

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
# Carica il CSV con le colonne già in °C e MPa
df = pd.read_csv("files/Allowables.csv", sep=";")

df_Y = pd.read_csv("files/Table304_1_1.csv", sep=";")  # o sep="," se è separato da virgole

#st.write(df_Y.columns.tolist())

# --- STEP 1: Seleziona materiale ---
materiali = df["Pipe_description"].dropna().unique()
materiale_scelto = st.selectbox("Select material:", materiali)

# --- STEP 2: Estrai la riga corrispondente ---
riga = df[df["Pipe_description"] == materiale_scelto]

code_y = riga["Code_Y"].values[0]
code_toll = riga["codeTol"].values[0]

# Estrai solo le colonne con le temperature (quelle che iniziano con "T_")
col_temp = [col for col in riga.columns if col.startswith("T_")]

# Crea un dizionario {temperatura °C: valore ammissibile pressione}
dati_temp = {
    float(col.replace("T_", "").replace("°C", "").replace(",", ".")): riga[col].values[0]
    for col in col_temp
    if not pd.isna(riga[col].values[0])
}
# Ordina le temperature crescenti
dati_temp = dict(sorted(dati_temp.items()))


# Costruisci tabella base
df_dati = pd.DataFrame(dati_temp.items(), columns=["Temp_°C", "Allowable_MPa"])

# Aggiungi colonne 'Code_Y' e 'Code_Toll' 
df_dati["Code_Y"] = code_y
df_dati["codeTol"] = code_toll



# Assicurati che le colonne usate per il merge siano compatibili
df_dati["Temp_°C"] = df_dati["Temp_°C"].astype(float).round(1)
df_Y["TempC"] = df_Y["TempC"].astype(str).str.replace(",", ".").astype(float).round(1)
df_Y["Yvalue"] = df_Y["Yvalue"].astype(str).str.replace(",", ".").astype(float).round(1)

# Elimina colonna "TempF" dalla visualizzazione
if "TempF" in df_Y.columns:
    df_Y = df_Y.drop(columns=["TempF"])

# Fai il merge con il file dei coefficienti Y
df_completo = pd.merge(
    df_dati,
    df_Y.rename(columns={"TempC": "Temp_°C", "Yvalue": "Y"}),  # adatta nomi
    on=["Code_Y", "Temp_°C"],
    how="left"
)

# --- STEP 3: Mostra tabella dati disponibili ---
st.write("Allowables values (°C → MPa):")
st.dataframe(df_completo, hide_index= True)

# --- STEP 4: Input temperatura da interpolare ---
temp_input = st.number_input("🔢 Input Temperature in °C for interpolation", min_value=min(dati_temp), max_value=max(dati_temp), step=1.0)

# --- STEP 5: Interpolazione lineare (Allowable e Y) ---
temp_list = list(dati_temp.keys())
val_list = list(dati_temp.values())

# Estrai anche la lista dei valori di Y dal dataframe mergeato

# Crea dizionario Y pulito
y_dict = df_completo.set_index("Temp_°C")["Y"].dropna().to_dict()

# Ricostruisci lista dei valori di Y come float
y_list = [y_dict.get(t, None) for t in temp_list]


# Trova il segmento [T1, T2] che contiene temp_input
V_interp = None
Y_interp = None

for i in range(len(temp_list) - 1):
    T1, T2 = temp_list[i], temp_list[i + 1]
    if T1 <= temp_input <= T2:
        V1, V2 = val_list[i], val_list[i + 1]
        Y1, Y2 = y_list[i], y_list[i + 1]

        # Interpolazione lineare pressione
        V_interp = V1 + (V2 - V1) * (temp_input - T1) / (T2 - T1)

        # Interpolazione lineare Y (se entrambi i valori esistono)
        if Y1 is not None and Y2 is not None:
            Y_interp = Y1 + (Y2 - Y1) * (temp_input - T1) / (T2 - T1)
        break

# --- STEP 6: Mostra risultato ---
if V_interp is not None:
    st.success(f"Interpolated Allowable Pressure: **{V_interp:.2f} MPa** at {temp_input} °C")
    if Y_interp is not None:
        st.info(f"Interpolated Y value: **{Y_interp:.4f}** at {temp_input} °C")
    else:
        st.warning("Y value not available for interpolation at this temperature.")
else:
    st.error("Temperature out of range for this material.")







