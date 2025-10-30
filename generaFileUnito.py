import streamlit as st
import pandas as pd
import os
from datetime import datetime

def SalvaDati():
    # Carica i file CSV contenenti i dati
    sessionDir = "sessions" 
    fileDatiGenerali = os.path.join(sessionDir, f"DatiGenerali_{st.session_state.session_id}.csv")
    filePipingGroups = os.path.join(sessionDir, f"piping_groups_{st.session_state.session_id}.csv")
    fileComponentGroups = os.path.join(sessionDir, f"comp_groups_{st.session_state.session_id}.csv")
    fileTemperatures = os.path.join(sessionDir, f"Temperatures_{st.session_state.session_id}.csv")  

    dati_generali = pd.read_csv(fileDatiGenerali)
    dati_piping = pd.read_csv(filePipingGroups)
    dati_components = pd.read_csv(fileComponentGroups)
    dati_temperatures = pd.read_csv(fileTemperatures, sep=";")

    dati_temperatures["TempC"] = pd.to_numeric(dati_temperatures["TempC"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    dati_temperatures["TempF"] = pd.to_numeric(dati_temperatures["TempF"].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    # ✅ Conversione della colonna "rating" in interi
    if "rating" in dati_components.columns:
        dati_components["Rating"] = pd.to_numeric(dati_components["Rating"], errors="coerce").fillna(0).astype(int)


    # Crea una prima colonna vuota per info generali "colonna_app" e poi le colonne di seprazione
    
    colonna_app = pd.DataFrame({'': [None] * max(len(dati_generali), len(dati_piping), len(dati_components), len(dati_temperatures))})
  
    # Inserisci l'intestazione personalizzata nella colonna vuota
    colonna_app.columns = [f"PiCa1 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]

    colonna_vuota1 = pd.DataFrame({'': [None] * max(len(dati_generali), len(dati_piping), len(dati_components), len(dati_temperatures))})
    colonna_vuota2 = pd.DataFrame({'': [None] * max(len(dati_generali), len(dati_piping), len(dati_components), len(dati_temperatures))})
    colonna_vuota3 = pd.DataFrame({'': [None] * max(len(dati_generali), len(dati_piping), len(dati_components), len(dati_temperatures))})

    colonna_vuota1.columns = ["separator_1"]
    colonna_vuota2.columns = ["separator_2"]
    colonna_vuota3.columns = ["separator_3"]    


    # Allinea le righe dei due file in modo che abbiano la stessa lunghezza
    dati_generali = dati_generali.reindex(range(max(len(dati_generali), len(dati_piping), len(dati_components), len(dati_temperatures))))
    dati_piping = dati_piping.reindex(range(max(len(dati_generali), len(dati_piping),len(dati_components),len(dati_temperatures))))
    dati_components = dati_components.reindex(range(max(len(dati_generali), len(dati_piping),len(dati_components), len(dati_temperatures))))
    dati_temperatures = dati_temperatures.reindex(range(max(len(dati_generali), len(dati_piping),len(dati_components), len(dati_temperatures))))

    # Unisci i due DataFrame con la colonna vuota tra di loro
    dati_uniti = pd.concat([colonna_app, dati_generali, colonna_vuota1, dati_piping, colonna_vuota2, dati_components, colonna_vuota3, dati_temperatures], axis=1)


    # Permetti all'utente di scaricare il file

    csv = dati_uniti.to_csv(index=False)

    fileName = st.text_input("Insert file name (without extension):", value="MyProject")
    # Rimuove eventuali spazi e qualsiasi estensione già presente
    if fileName:
        base_name, _ = os.path.splitext(fileName.strip())
        fileName = base_name + ".csv"
        st.markdown(
            f"Data file name set to: <span style='color:blue;'>**{fileName}**</span>",
            unsafe_allow_html=True
        )
        st.download_button(label=f"💾 Download: {fileName}", data=csv, file_name=f"{fileName}", mime="text/csv", help= '***click here to save data in your personal drive***')


    else:
        st.warning("Please enter a valid file name.") 

    
    