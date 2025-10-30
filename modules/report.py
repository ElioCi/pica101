import streamlit as st
import math
import pandas as pd
from math import log

"session_state:", st.session_state
def app():

    flag_run = st.session_state['run']
    print("flag_run", flag_run)
    if flag_run == "eseguito":

        DN = st.session_state['DN']
        extDia = st.session_state['extDia']
        thk = st.session_state['thk']
        intDia = st.session_state['intDia']
        fluidTemp = st.session_state['fT']
        extTemp = st.session_state['eT']
        flowRate = st.session_state['fR']
        specHeat = st.session_state['sH']
        condPipe = st.session_state['cP']
        condInsul = st.session_state['cI']
        hi = st.session_state['hi']
        he = st.session_state['he']
        insulThk = st.session_state['iThk']
        PipeLength = st.session_state['PLen']
    
        #"st.session_state :", st.session_state


        st.sidebar.success("Calculation performed !")
        

        st.markdown("<h6 style='text-align: center;'>🌈 Pipe heat loss analysis </h6>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("<h3 style='text-align: Left;'>📃  Calculation Report </h3>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### ***--- Data ---***")
        st.write("")
        st.write("Selected DN = ", DN, '"')
        
        st.write(f'Thickness = {thk:,.2f} mm')
        

        st.write(f'Fluid Temp. = {fluidTemp:,.2f} °C')
        st.write(f'Ext. Temp. = {extTemp:,.2f} °C')
        st.write(f'Flow Rate = {flowRate:,.3f} kg/h')
        st.write(f'Specific heat = {specHeat:,.3f} kcal/kg°C')
        st.write(f'Pipe thermal conductivity = {condPipe:,.3f} W/m°K')
        
        st.write(f'Insulation thickness = {insulThk:,.2f} mm')
        st.write(f'Insulation thermal conductivity = {condInsul:,.3f} W/m°K')
        st.write(f'Internal surface coeff. = {hi:,.3f} W/m^2°K')
        st.write(f'External surface coeff. = {he:,.3f} W/m^2°K')
        st.write(f'Pipe Length = {PipeLength:,.2f} mm')
        st.markdown("")

        #  --- calcoli -------------------------------------------
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
        Kcomb = Kc  # +Kvalvole
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
        st.markdown("#### ***--- Results ---*** ")
        st.write("")
        st.write(f'External Dia = {extDia:,.2f} mm')
        st.write(f'Inetrnal Dia = {intDia:,.2f} mm')                        
        st.write(f'dT = {deltaT:,.2f} °C')
        Testo = "Temperature @ distance of " + str(L) + " m ="
        st.write(Testo, format(TdistL,".2f"), "°C")
        st.write("Lost Temperature =", format(Tpersa,".2f"), "°C")
        st.write("<br><br>", unsafe_allow_html=True)


        # Rappresentazione grafica perdita di temperatura
        dfg = pd.DataFrame({'dist (m)': x, 'T (°C)': Tx})
        chart_data = pd.DataFrame({'dist (m)': x, 'Temp (°C)': Tx})
        st.line_chart(
        chart_data, x= "dist (m)", y= "Temp (°C)", color=["#FF0000"]  # Optional
        )

        dfg_ni= st.dataframe(dfg, hide_index=True)    # tabella numerica
        flag_report = True
    
           
        
    