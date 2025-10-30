import streamlit as st
import pandas as pd
import csv
import os

from generaFileUnito import SalvaDati

# Titolo dell'applicazione
st.set_page_config(page_title="Save_Project")
st.title('💾Save Project')

with st.expander("🆘 Help"):
    st.markdown("""
    - **What to do here?**  
      In this module you can choose a personal file name and download it in your local drive. 
      The file include all project data and you can recall it when you need by ticking the option "stored project" in the main module. 
                                               

    """)

#    === Controllo accesso ===
if 'prot' not in st.session_state:
    st.session_state.prot = False
    
if st.session_state.prot == False:
    st.info('unauthorized access')
    st.stop()


sessionDir = "sessions" 
fileDatiGenerali = os.path.join(sessionDir, f"DatiGenerali_{st.session_state.session_id}.csv")
filePipingGroups = os.path.join(sessionDir, f"piping_groups_{st.session_state.session_id}.csv")
fileComponentGroups = os.path.join(sessionDir, f"comp_groups_{st.session_state.session_id}.csv")
fileTemperatures = os.path.join(sessionDir, f"Temperatures_{st.session_state.session_id}.csv")


dati_generali = pd.read_csv(fileDatiGenerali)
dati_piping = pd.read_csv(filePipingGroups)
dati_components = pd.read_csv(fileComponentGroups)
dati_temperatures = pd.read_csv(fileTemperatures, sep=';')

dati_temperatures["TempC"] = pd.to_numeric(dati_temperatures["TempC"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
dati_temperatures["TempF"] = pd.to_numeric(dati_temperatures["TempF"].astype(str).str.replace(",", ".", regex=False), errors="coerce")


# Dizionario con i tuoi DataFrame
dati_dict = {
    "General Data": dati_generali,
    "Piping Data": dati_piping,
    "Components Data": dati_components,
    "Temperature Data": dati_temperatures
}

# Lista dei DataFrame vuoti
vuoti = [nome for nome, df in dati_dict.items() if df.empty]

# Controllo e messaggi
if vuoti:
    st.warning("⚠️ Some data files are empty!")
    for nome in vuoti:
        st.error(f"❌ {nome} is empty!")
else:
    #st.success("✅ All data files are complete!")
    
    # Mostra un'anteprima dei dati separati
    st.write("General Data:")
    st.dataframe(dati_generali)
    
    st.write("Piping Data:")
    st.dataframe(dati_piping)

    st.write("Components Data:")
    st.dataframe(dati_components)

    st.write("Temperatures Data:")
    st.dataframe(dati_temperatures)
     
    SalvaDati()






