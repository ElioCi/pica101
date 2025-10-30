import streamlit as st   # pip install streamlit
import pandas as pd  # pip install pandas
import plotly.express as px 
import math 
from streamlit_option_menu import option_menu # pip intsall streamlit-option-menu
from matplotlib import pyplot as plt
from math import log
# from tkinter.filedialog import asksaveasfilename
# from tkinter.filedialog import askopenfilename
from modules import report
import csv

  
def app():
    #print("st.session_state.logged calcsheet", st.session_state.logged)
    st.markdown("---")
    st.markdown("<h3 style='text-align: Left;'>Input data </h3>", unsafe_allow_html=True)
    st.markdown('---')
    #if 'user' not in st.session_state:
    #        st.session_state.user = None
    #if st.session_state["user"]:
    #        username = st.session_state["username"]
    #        st.info(f'🔒 logged-in as {username}') 

    # Leggi file con diametri e genera lista diametri
    diaList = []
    with open('files/diametri.csv', newline='') as diameters:
        diameters_data = csv.reader(diameters)
        next(diameters_data) #salta la riga di testa

        for row in diameters_data:
            diaList.append(row[0])
            #print(diaList)

    with open('files/Dia_thk.csv') as file_thk:
        df = pd.read_csv(file_thk, delimiter = ";")   # lettura file e creazione dataFrame

    with open('files/ExtDia.csv') as file_extDia:
        dfDia = pd.read_csv(file_extDia, delimiter = ";", index_col= 1)   # lettura file e creazione dataFrame e indicizzazione secondo colonna 1 (DN)

    #leggi dati di input da temDati.csv
    with open('files/tempDati.csv') as file_input:
        dftemp = pd.read_csv(file_input)   # lettura file e creazione
        dftemp.drop(dftemp.columns[dftemp.columns.str.contains('unnamed', case= False)], axis=1, inplace= True)
            
    #st.dataframe(dftemp, hide_index= True)
    datiFreezati = "No"
    
    if 'checkbox_state' not in st.session_state:
        st.session_state.checkbox_state = False

    if 'button_pressed' not in st.session_state:
        st.session_state.button_pressed = False
       
    def diaSelected():
        
        return

    def thkSelected():

        return

    # nuovo foglio di calcolo o archivio?
    flag_ns = st.session_state['flag_ns']
       
            
    if flag_ns == "Saved Calculation":
        dv= False
        if st.session_state.checkbox_state == True: 
            st.session_state.checkbox_state = not st.session_state.checkbox_state
      
    else:
        dv= False
        
        
    
    
    # with st.form("Data Form", clear_on_submit=True, border=True):
    
    # extDia = col1.slider(":blue[Pipe nominal diameter (inches)]", min_value=0, max_value=100)
    # thk = col2.number_input(":blue[Pipe thickness (mm)]")
    # myList = ["1/8", "opt2", "opt3"]
    #if st.session_state.DN != "":
    #    indice= diaList.index(st.session_state.DN)
    
        
    # Funzione per gestire il cambiamento da pulsante della checkbox
    def toggle_checkbox():
        st.session_state.checkbox_state = not st.session_state.checkbox_state
        st.session_state.button_pressed = True
        

    # Funzione per gestire il cambiamento manuale della checkbox
    def update_checkbox():
        st.session_state.checkbox_state = st.sidebar.checkbox('Allow data changes', value=st.session_state.checkbox_state, disabled= dv)

    
    # Checkbox con stato gestito dalla sessione
    update_checkbox()

    #chkModifica = st.sidebar.checkbox("change data", key= 'checkbox_state', disabled= dv)
    if st.session_state.checkbox_state:
        flag_mod = "modificabile"
        st.session_state['modifica']= flag_mod 
    else:
        flag_mod = "non_modificabile"    
        st.session_state['modifica']= flag_mod
        

    if flag_mod != "modificabile":
        st.warning("⚠️ Warning: **changes not allowed!** ... To modify the following data, you have to check the checkbox '*Allow data changes*' in the sidebar")
    if flag_mod == "modificabile":
        st.success(":smile: **changes allowed!** ... You are allowed to modify input data")

    col1, col2 = st.columns(2)

    option_dia = col1.selectbox ("Pipe Nominal Diameter [inches]", options=(diaList), key= 'DN', on_change= diaSelected, disabled= dv)
    
    thkList = df[option_dia].dropna()
    option_thk = col2.selectbox("Thickness [mm]", options=(thkList), key= 'thksel', on_change= thkSelected, disabled = dv)
    externalDia = dfDia.loc[option_dia, 'Dia']
    # thk = float(option_thk)
    # intDia = extDia-2*thk
    thk = float(option_thk.replace(",","."))
    extDia = float(externalDia.replace(",","."))
    intDia = extDia-2*thk

    
    #st.session_state.DN = option_dia
    #st.session_state.thksel = option_thk
    st.session_state['extDia']= extDia
    st.session_state['thk'] = thk
    st.session_state['intDia']= intDia


    #"st.session_state = ", st.session_state

    #print(type(option_thk))
    #print("option_thk =", option_thk)
    #print("Thk =", thk)
    #print("intDia =", intDia)


    # col1.markdown("<br>", unsafe_allow_html=True)
    # col1.markdown("<h3 style='text-align: left;'> Thermal data </h3>", unsafe_allow_html=True) # Dati termici
    # col2.markdown("<br>", unsafe_allow_html=True)
    # col2.markdown("<h3><br></h3>", unsafe_allow_html=True)
    fluidTemp = col1.number_input("Fluid Temperature [°C]", value= 50, step= 1, key= 'fT', disabled= dv)
    extTemp = col2.number_input("External Temperature [°C]", value= 20, step= 1, key= 'eT', disabled = dv)
    flowRate = col1.number_input("Fluid flow rate [kg/h]", value = 50.1, step= 0.1, key= 'fR', disabled= dv)
    specHeat = col2.number_input("Specific heat [kcal/kg°C]", value=0.500, step= 0.005, format="%0.3f", key= 'sH', disabled= dv)

    condPipe = col1.number_input("Pipe thermal conductivity [W/m°K]", value= 52, key= 'cP', disabled= dv )   # valore tipico acciaio
    condInsul = col2.number_input("Insulation thermal conductivity [W/m°K]", value= 0.040, step= 0.005, format="%0.3f", key= 'cI', disabled = dv) # valore lana di roccia
    hi = col1.number_input("Internal surface coeff. hi [W/m^2°K]", value= 1000, step=50, key= 'hi', disabled=dv)
    he = col2.number_input("Enternal surface coeff. he [W/m^2°K]", value= 20, step=5, key= 'he', disabled= dv)
    insulThk = col1.number_input("Insulation Thk [mm]", value= 20, step= 5, key= 'iThk', disabled= dv)  # spessore isolante
    PipeLength = col2.number_input("Pipe Length [m]", value = 10, key= 'PLen', disabled= dv) # lunghezza piping

    # Custom CSS per allineare le opzioni su una riga
    st.markdown(
        """
        <style>
        .stRadio > div {
            flex-direction: row;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    numValves = col1.number_input("Valves number", value= 0, key= 'numValves', disabled= dv)
    eDvalve = col2.number_input("External Dia", value= 0.00, key= 'eDvalve', disabled= dv)
    insulated = col4.radio("Valves Insulated?", options=["Yes", "No"], index = 1)
    Lvalve = col3.number_input("Lenght of each valve (mm)", value= 0.00, key= 'Lvalve', disabled= dv)
    # memorizza dati di input in un dizionario -----

    data= {
        "DN": [st.session_state.DN],
        "thksel": [option_thk],
        "eDia": [extDia],
        "thk": [thk],
        "iDia": [intDia],
        "fT": [fluidTemp],
        "eT": [extTemp],
        "fR": [flowRate],
        "sH": [specHeat],
        "cP": [condPipe],
        "cI": [condInsul],
        "hi": [hi],
        "he": [he],
        "iThk": [insulThk],
        "PLen": [PipeLength],
        "numValves": [numValves],
        "eDvalve": [eDvalve],
        "Lvalve": [Lvalve],
        "insulated": [insulated]
    }

    # -------------------------------------
    dfData= pd.DataFrame(data)

    if dv== False:
        st.session_state


    #dfDati = pd.DataFrame.from_dict((st.session_state), orient= 'index' )

    #  --- calcoli dispersione condotta -------------------------------------------
    deltaT = fluidTemp-extTemp
    R1 = intDia/2000 # Raggio interno in m
    R2 = extDia/2000 # Raggio esterno in m
    R3 = R2+insulThk/1000 # Raggio superficie isolante
    L = PipeLength 
    Rcrit = condInsul/he*1000 # Raggio critico
    spcrit = Rcrit/1000-R2  # spessore critico

    invK = (1/hi+R1/condPipe*log(R2/R1)+R1/condInsul*log(R3/R2)+R1/R3*1/he)  # 1/K inverso del coefficiente di scambio termico
    Kw = 1/invK   # coeff. globale di scambio termico in W/m2°C
    Kc = Kw*0.859845  # coeff di scambio in kCal/h*m2°C

    # ---- calcoli dispersioni termiche valvole se non coibentate
    R2v = eDvalve/2000 # raggio esterno valvola in m
    R3v = R2v
    Ltotvalve = Lvalve*numValves
    invKv = 0
    Kv = 0
    if R2v != 0 and numValves != 0 :
        invKv = (1/hi+R1/condPipe*log(R2v/R1)+R1/condInsul*log(R3v/R2v)+R1/R3v*1/he)  # 1/K sole valvole
    elif R2v == 0 and numValves!= 0:
        st.warning("External dia of valve can not be 0. Please input a value.")

    if insulated == "No" and numValves !=0 :
        Kv = 1/invKv   # coeff. di scambio termico in W/m2°C
    elif insulated == "Yes":
        Kv = 0    
    
    Kvalvole = Kv*0.859845 # coeff di scambio valvole in kCal/h*m2°C
    # ---------------------------------------------------------------------

    Kcomb = Kc + Kvalvole*Ltotvalve/(1000*L)
    Qlineare = 2*math.pi*R1*Kw*deltaT   # Heat Flow in W/m
    ts = Qlineare/(math.pi*((extDia+2*insulThk)/1000)*he)+extTemp   # temperatura superficie isolante

    # calcolo temperatura a distanza L in m
    esponente = math.pi*extDia*0.001*Kcomb/(specHeat*flowRate)
    TdistL = extTemp+deltaT*math.exp(-esponente*L)   # temperatura a distanza L
    Tpersa = fluidTemp-TdistL 

    # dati per grafico
    pitch = L/20

    x=[]
    Tx = []
    i= 0.00
    while i <= 50:
        Ti = extTemp+deltaT*math.exp(-i*esponente) 
        x.append(i)
        Tx.append(Ti)
        i+= pitch


    # stampa risultati a video

    #btnRun = st.button("Run Analysis", disabled=dv)
    st.write("")
    
    if flag_mod == "modificabile":
        st.button("Freeze changes", on_click= toggle_checkbox)

        
    if st.session_state.button_pressed:
        dfData.to_csv("files/tempDati.csv")   # salva dati su tempDati    
        Tabdati= st.dataframe(dfData, hide_index=True)    # tabella dati
        flag_mod = "non_modificabile"
        datiFreezati = "Si"
        flag_ns = "new"
        st.session_state['flag_ns']= flag_ns

    chkShowResults = st.checkbox("Show Analysis Results", disabled= dv)
    if chkShowResults:
        flag_run = "eseguito"
        if st.session_state.checkbox_state == True: 
            st.session_state.checkbox_state = not st.session_state.checkbox_state
       
    
        #print(dfData) -------------------------
        st.session_state['run'] = flag_run
        st.markdown("---")

        st.markdown("<h3 style='text-align: Left;'>Results </h3>", unsafe_allow_html=True)
        st.markdown("---")
        st.write("Selected DN = ", option_dia, '"')
        st.write("External Dia =", extDia, "mm")
        st.write("Thikness =", option_thk, "mm")
        st.write("Internal Dia =", intDia, "mm")
        st.write("DT =", deltaT, "°C")
        st.write("")
        st.write("Number of valves along the path =", numValves)
        if insulated == "Yes" and numValves!= 0:
            st.write("Valves are insulated!")
        elif insulated == "No" and numValves!= 0:
            st.write("Valves are not insulated!")
            st.write("Valves external Dia =", eDvalve, "mm")
            st.write("Length of each valve =", Lvalve, "mm")

        Testo = "Temperature @ distance of " + str(L) + " m ="
        st.write(Testo, TdistL, "°C")
        st.write("Lost Temperature =", Tpersa, "°C")
        st.write("<br><br>", unsafe_allow_html=True)
          
        #"session_state:", st.session_state
        #fig = plt.plot(x, Tx)
        #plt.show()
        # st.pyplot(fig)
        # print("x, Tx", x, Tx)
        # fig= px.line(data_frame= [x, Tx], x= "distanza", y= "Temperatura")

        # Rappresentazione grafica perdita di temperatura
        dfg = pd.DataFrame({'dist (m)': x, 'T (°C)': Tx})
        chart_data = pd.DataFrame({'dist (m)': x, 'Temp (°C)': Tx})
        st.line_chart(
        chart_data, x= "dist (m)", y= "Temp (°C)", color=["#FF0000"]  # Optional
        )

        dfg_ni= st.dataframe(dfg, hide_index=True)    # tabella numerica
    # st.write(dfg_ni)

    #    print("Q/L e ts", Qlineare, ts)
    #    print("TdistL, Tlost", TdistL, Tpersa)

        btnSave = st.button(label= ":green-background[Save analysis]", disabled= False)
        
        st.markdown("---")
        
        # routine to save and download results in the file dataInput.csv
        if btnSave:
            st.write("button Save clicked!")
            #nuovofile = 'nuovoFile.csv'
            # datafile = st.file_uploader("Upload CSV",type=['csv'])

            # fileName = asksaveasfilename(defaultextension= 'csv')
            #st.write(fileName)
            #with open(fileName, 'w') as f:
            #if datafile is not None:
            #    file_details = {"FileName":datafile.name,"FileType":datafile.type}
                # df  = pd.read_csv(datafile)      
                #dfData
            @st.cache_data
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode("utf-8")

            daticsv = convert_df(dfData)
        
            st.download_button(
                label= "Download data as csv",
                data= daticsv,
                file_name= "dataInput.csv",
                mime= "text/csv"
                )


   

    # btnCalc = st.form_submit_button("run")
    #col1, col2, col3, col4 = st.columns(4)

    
    
        
        
    

