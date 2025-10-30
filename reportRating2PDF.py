import streamlit as st
import pandas as pd
import csv
from fpdf import FPDF
from create_table_fpdf2 import PDF
import re
import json
import os
from datetime import datetime

#from table_function import create_table

def UpdRepRatingPdf():
    # create FPDF object
    # layout ('P', 'L')
    # unit ('mm', 'cm', 'in')
    # format ('A3', 'A4 (default), 'A5', 'Letter', (100, 150))

    # Definizione dei parametri
    title = "Rating by Temperature Report"
    orientation = 'P'
    unit = 'mm'
    format = 'A4'
    
    # Creazione del PDF con parametri passati
    pdf = PDF(orientation=orientation, unit=unit, format=format, title=title)
    #pdf = PDF('L', 'mm', 'A3')

    #get total pages
    pdf.alias_nb_pages()

    # Add a page
    pdf.add_page()
    # specify font ('times', 'courier', 'helvetica', symbol', zpfdingbats')
    # 'B'(bold), 'U'(underlined), 'I'(italic), ''(regular), combination(i.e.,('BU'))
    #pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(0,0,0)

    # add text
    # w= width
    # h= height
    # txt = your text
    # ln (0 False; 1 True - move cursor down to next line)
    # border (0 False; 1 True - add border around cell)
    pdf.set_xy(10, 30)
    #pdf.cell(120, 100, 'Hello World', new_y= 'NEXT', border=True)
    pdf.set_font('times', '', 12)
    #text = 'Pipe heat loss analysis'
    #pdf.cell(80,10, text)
    textDateTime = f"Work Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    pdf.cell(80,10, textDateTime, ln=1, border=False)


    #leggi Units da Units
    with open('files/tags.csv') as file_units:
        readerUnits = csv.reader(file_units, delimiter = ";")
        #dfUnits = [rowUn for rowUn in readerUnits]
    
        # Ottieni le intestazioni (prima riga)
        headerUnits = next(readerUnits)
        
        # Modifica la prima colonna se il nome è 'Unnamed: 0.1'
        headerUnits[0] = re.sub(r'[^A-Za-z0-9]+', '_', headerUnits[0])
    
        # Leggi i dati rimanenti
        dfUnits = [rowUn for rowUn in readerUnits]
        
    # Aggiungi la nuova intestazione ai dati
    dfUnits.insert(0, headerUnits)
    

    #leggi dati di input da DatiGenerali.csv
    sessionDir = "sessions"
    fileDatiGen = os.path.join(sessionDir, f"DatiGenerali_{st.session_state.session_id}.csv")
    with open(fileDatiGen, newline='') as file_input:
        reader = csv.reader(file_input)
        data = [row[1:] for row in reader]

   
    # Leggi i dati di input da 'piping_groups.csv'
    #with open('files/piping_groups.csv', newline='') as pip_input:
    fileCmpGroups = os.path.join(sessionDir, f"comp_groups_{st.session_state.session_id}.csv")
    with open(fileCmpGroups) as cmp_input:
        readercmp = csv.reader(cmp_input)
        
        # Ottieni le intestazioni (prima riga)
        header = next(readercmp)
        
        # Modifica la prima colonna se il nome è 'Unnamed: 0.1'
        if header[0] == 'Unnamed: 0.1':
            header[0] = 'id'  # Rinomina la prima colonna
        
        
        # Leggi i dati rimanenti
        datacmp = [rowcmp for rowcmp in readercmp]

    # Aggiungi la nuova intestazione ai dati
    datacmp.insert(0, header)

    #leggi risultati da Output.csv
    #with open('files/Output.csv') as output:

    #leggi risultati da pressures_by_temperature.csv
    filePressTemp = os.path.join(sessionDir, f"pressures_by_temperature_{st.session_state.session_id}.csv")
    with open(filePressTemp) as ratingOutput:    
        readerout = csv.reader(ratingOutput)
        
    # Ora `out` contiene i valori con tre cifre decimali per i numeri.
    # Ottieni le intestazioni (prima riga)
        headerratingOutput = next(readerout)
        
        # Modifica la prima colonna se il nome è 'Unnamed: 0.1'
        if headerratingOutput[0] == 'Unnamed: 0.1':
            headerratingOutput[0] = 'id'  # Rinomina la prima colonna
        
        # Leggi i dati rimanenti
        #dataratingOutput = [row for row in readerout]
        dataratingOutput = list(readerout)

    # Trova l'indice della prima riga in cui almeno un valore (escluso l'id) è 0 o vuoto
    cut_index = None
    for i, row in enumerate(dataratingOutput):
        # Escludi prima colonna (id), controlla se c'è almeno un valore 0 o vuoto
        for value in row[1:]:
            if value.strip() == '' or value.strip() == '0':
                cut_index = i
                break
        if cut_index is not None:
            break

    # Se trovato, elimina tutte le righe da quella in poi
    if cut_index is not None:
        dataratingOutput = dataratingOutput[:cut_index]

    # Reinserisci l'intestazione in cima
    dataratingOutput.insert(0, headerratingOutput)


    #pdf.cell(100,10, first_line, border=False , new_y= 'NEXT', align='L')
    #pdf.set_x(10)
    #pdf.cell(100,10, second_line, border=False, new_y= 'NEXT', align='L')
    #pdf.ln()


    #pdf.create_table(table_data = data,title='I\'m the first title', cell_width='even')
    pdf.create_table(table_data = dfUnits, title='Tags and units', cell_width='uneven')
    pdf.ln()
    #pdf.ln()

    #pdf.create_table(table_data = data,title='I\'m the first title', cell_width='even')
    pdf.create_table(table_data = data, title='General Data', cell_width='uneven')
    pdf.ln()
    #pdf.ln()

    #pdf.create_table(Piping data)
    pdf.create_table(table_data = datacmp, title='Components Data', cell_width='uneven')
    #pdf.ln()
    #pdf.ln()


    pdf.add_page()
    #pdf.create_table(Output)
    pdf.create_table(table_data = dataratingOutput, title='Output', cell_width='uneven')
    pdf.ln()
    #pdf.ln()

    #pdf.add_page()

    #pdf.set_font('times', 'BU', 12)
    #pdf.cell(80,10, 'Piping Groups Rating', ln=1, border=False)

    #pdf.set_font('times', '', 10)

 


    '''
    pdf.set_font('times', 'BU', 12)
    pdf.cell(80,10, 'Symbols Legend', ln=1, border=False)

    pdf.set_font('times', '', 10)
    
    # Definizione delle larghezze per le colonne
    column1_width = 50
    column2_width = 100

    # Aggiunta delle righe con tabulazioni
    pdf.cell(column1_width, 5, 'DN:', border=0)
    pdf.cell(column2_width, 5, 'Nominal Diameter [inch]', ln=1, border=0)

    pdf.cell(column1_width, 5, 'OD:', border=0)
    pdf.cell(column2_width, 5, 'Outside Diameter [mm]', ln=1, border=0)

    pdf.cell(column1_width, 5, 'CA:', border=0)
    pdf.cell(column2_width, 5, 'Corrosion Allowance [mm]', ln=1, border=0)

    pdf.cell(column1_width, 5, 'codeTol:', border=0)
    pdf.cell(column2_width, 5, 'Manufacturing Tolerance code', ln=1, border=0)   

    pdf.cell(column1_width, 5, 'TOL:', border=0)
    pdf.cell(column2_width, 5, 'Manufacturing Tolerance [perc. or mm]', ln=1, border=0)

    pdf.cell(column1_width, 5, 'E:', border=0)
    pdf.cell(column2_width, 5, '', ln=1, border=0)

    pdf.cell(column1_width, 5, 'W:', border=0)
    pdf.cell(column2_width, 5, '', ln=1, border=0)

    pdf.cell(column1_width, 5, 'Y:', border=0)
    pdf.cell(column2_width, 5, '', ln=1, border=0)    

    pdf.cell(column1_width, 5, 'Temp:', border=0)
    pdf.cell(column2_width, 5, 'Temperature [°C]', ln=1, border=0)   

    pdf.cell(column1_width, 5, 'Press:', border=0)
    pdf.cell(column2_width, 5, 'Pressure [bar]', ln=1, border=0)  

    pdf.cell(column1_width, 5, 'thkC:', border=0)
    pdf.cell(column2_width, 5, 'Minimum calculated thickness [mm]', ln=1, border=0)

    pdf.cell(column1_width, 5, 'thkCReq:', border=0)
    pdf.cell(column2_width, 5, 'Minmum required thickness [mm]', ln=1, border=0)

    pdf.cell(column1_width, 5, 'thkCom:', border=0)
    pdf.cell(column2_width, 5, 'Commercially available thickness [mm]', ln=1, border=0)

    pdf.cell(column1_width, 5, 'Allow:', border=0)
    pdf.cell(column2_width, 5, 'Mat. Allowable Stress [MPa]', ln=1, border=0)    

    pdf.cell(column1_width, 5, 'MAWP:', border=0)
    pdf.cell(column2_width, 5, 'Maximum Allowable Working Pressure [bar]', ln=1, border=0)



    #pdf.add_page()
    #pdf.image('files/grafico.png', x=30, y=50, w=300) 

    '''
    CmpReportPdf = os.path.join(sessionDir, f"report2_{st.session_state.session_id}.pdf")
    pdf.output(CmpReportPdf)

    

