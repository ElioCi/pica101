import streamlit as st
import pandas as pd
from LoadFileData import loadData
import json

st.set_page_config(
    page_title= "PiCa - Piping Calculation",
    page_icon= "⭕"
)


# Legge il valore dal file temporaneo
sessionDir = "sessions"
fileProt = f"{sessionDir}/prot_status_{st.session_state.session_id}.json"
try:
    with open(fileProt, "r") as file:
        data = json.load(file)
        st.session_state.prot = data.get("prot", False)
except FileNotFoundError:
    st.session_state.prot = False

   
# Funzione per svuotare il contenuto dei file mantenendo solo la prima riga
def reset_files(general_data_path, piping_data_path, comp_data_path, new_values=None):
    # Carica i dati da entrambi i file
    df_general = pd.read_csv(general_data_path)
    st.session_state.df = pd.read_csv(piping_data_path)
    st.session_state.dfComp = pd.read_csv(comp_data_path)

    # Mantieni solo la prima riga per entrambi i file
    df_general = df_general.iloc[:1, :]
    st.session_state.df = st.session_state.df.iloc[:0, :]
    st.session_state.dfComp = st.session_state.dfComp.iloc[:0, :]

    # Converti le colonne in stringhe prima di assegnare i valori
    df_general['JAccount'] = df_general['JAccount'].astype(str)
    df_general['Project'] = df_general['Project'].astype(str)
    df_general['Location'] = df_general['Location'].astype(str)
    df_general['Spec'] = df_general['Spec'].astype(str)
    df_general['Service'] = df_general['Service'].astype(str)

    # Sostituisci i campi specifici nel file GeneralData.csv
    if new_values:
        df_general.loc[0, 'JAccount'] = new_values.get('JAccount', '')
        df_general.loc[0, 'Project'] = new_values.get('Project', '')
        df_general.loc[0, 'Location'] = new_values.get('Location', '')
        df_general.loc[0, 'Spec'] = new_values.get('Spec', '')
        df_general.loc[0, 'Service'] = new_values.get('Service', '')


    # Salva i file aggiornati
    df_general.to_csv(general_data_path, index=False)
    st.session_state.df.to_csv(piping_data_path, index=False)
    st.session_state.dfComp.to_csv(comp_data_path, index=False)

    st.success("Calculation files successfully initialized.")

if 'statoPulsante1' not in st.session_state:
    st.session_state.statoPulsante1 = 'noclick'
if 'statoPulsante2' not in st.session_state:
    st.session_state.statoPulsante2 = 'noclick'
if 'statoPulsanteNo' not in st.session_state:
    st.session_state.statoPulsanteNo = 'noclick'  
if 'preset' not in st.session_state:
    st.session_state.preset = 0    

if 'DatiCaricati' not in st.session_state:
    st.session_state.DatiCaricati = False

st.info(
        ":smile: Hi --- This Application allows you to elaborate piping class"
        )
    
st.markdown("---")

st.markdown("<h1 style='text-align: center;'>⭕ PiCa - Piping Calculations </h1>", unsafe_allow_html=True)
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.page_link("https://enginapps.it", label="www.enginapps.it", icon="🏠")

sceltaNew = col3.radio("Select an option", options= ('New Project', 'Stored Project'))

if 'newFlag' not in st.session_state:
    st.session_state.newFlag = 'none'

# Se cambio da New Project a Stored Project, resetto tutto ciò che riguarda New Project
if sceltaNew == 'Stored Project' and st.session_state.newFlag == 'new':
    st.session_state.statoPulsante1 = 'noclick'
    st.session_state.newFlag = 'stored'
    st.rerun()

if sceltaNew == 'New Project' and st.session_state.newFlag == 'stored':
    st.session_state.statoPulsante2 = 'noclick'
    st.session_state.newFlag = 'new'
    st.rerun()

posPulsante = st.empty()

if sceltaNew == 'New Project':
    st.session_state.newFlag = 'new'
    if posPulsante.button('🎬 Start !'):
        #st.session_state.newFlag = 'new'
        st.sidebar.info(st.session_state.newFlag)
        
        st.session_state.statoPulsante1 = 'clicked'
        col1, col2, col3 = st.columns([5, 0.6, 1])
        col1.warning('**Warning**: if you continue, all data will be initialized. Are you sure?')
        

#print(st.session_state.newFlag, st.session_state.statoPulsante1, st.session_state.statoPulsante2)
if (st.session_state.statoPulsante1 == 'clicked'):
    if col2.button('Yes'):
        
        new_values = {
            'JAccount': 'job code',  # Sostituisci con valore vuoto
            'Project': 'project title',   # Sostituisci con valore vuoto
            'Location': 'location',  # Sostituisci con valore vuoto o specifico
            'Spec': 'spec',    # Sostituisci con valore vuoto o specifico
            'Service': 'service'
        }

        file1 = f"{sessionDir}/DatiGenerali_{st.session_state.session_id}.csv"
        file2 = f"{sessionDir}/piping_groups_{st.session_state.session_id}.csv"
        file3 = f"{sessionDir}/comp_groups_{st.session_state.session_id}.csv"
        
        reset_files(file1, file2, file3, new_values=new_values)
        st.session_state['data'] = []
        st.session_state[''] = []
        st.session_state.statoPulsante1 = 'noclick'
        
        st.session_state.export_results = []   # azzera risultati precedenti
        
        pagina = 'pages/1_📝General_Data.py'
        st.switch_page(pagina)

   
    if col3.button('No'):
        st.session_state.statoPulsante1 = 'noclick'
        st.rerun()


    
if sceltaNew == 'Stored Project':

    st.session_state.newFlag = 'stored'
    st.sidebar.info(st.session_state.newFlag )
    st.session_state.statoPulsante2 = 'clicked'
    st.session_state.statoPulsante1 = 'noclick'
    
    col1, col2, col3 = st.columns([5, 0.6, 1])
    col1.warning('**Warning**: if you continue, all data will be replaced with those in the archive.')
    loadData()
    if st.session_state.DatiCaricati == True:
        st.session_state.statoPulsante2 = 'noclick'
        if st.button('🎬 Start !'):  
            pagina = 'pages/1_📝General_Data.py'
            st.switch_page(pagina)

                 
        

#flag_ns = col2.radio("Select one option", ["New Calculation", "Saved Calculation"])
st.markdown("")
st.info("-- ©️ App developed by ing. Pasquale Aurelio Cirillo - Release 1.0 2025 --")


#st.page_link("pages/page_1.py", label="New Calculation", icon="1️⃣")
#col1.markdown("")
#col1.markdown("")
# col1.page_link("pages/new_calculation.py", label="Calculation Sheet", icon="📝")
# st.page_link("pages/saved_calculation.py", label="Saved Calculation", icon="📂", disabled=False)
#st.page_link("http://www.google.com", label="Google", icon="🌎")

#st.session_state['flag_ns'] = flag_ns
#if flag_ns== "Saved Calculation":
#    st.page_link("pages/calculationSheet.py", label="Archived file data", icon="📂")
#    st.markdown("click the button to open a saved calculation sheet")
    
#else:
#    st.page_link("pages/calculationSheet.py", label="New Calculation Sheet", icon="📝")
#    st.markdown("click the button to open a new calculation sheet")

