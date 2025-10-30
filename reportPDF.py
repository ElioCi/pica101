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

def UpdateReportPdf():
    # create FPDF object
    # layout ('P', 'L')
    # unit ('mm', 'cm', 'in')
    # format ('A3', 'A4 (default), 'A5', 'Letter', (100, 150))

    # Definizione dei parametri
    title = "Piping groups thickness calculation report"
    orientation = 'P'
    unit = 'mm'
    format = 'A4'
    
    '''
    class PDF(FPDF):
        def header(self):
            #logo
            self.image('assets/rep.jpg', 15,5,12 )
            self.set_font('helvetica', 'B', 15)
            # padding
            #self.cell(80)
            # title
            
            title_w = self.get_string_width(title)
            doc_w = self.w
            
            self.set_x((doc_w - title_w)/2)

            self.cell(10,10, title, border=False, new_y= 'NEXT', align='L')
            # line breack
            self.set_draw_color(255,0,0)
            self.line(10,5,200,5)
            self.line(10,25,200,25)

        # page footer
        def footer(self):
            # set position of the footer 
            doc_w = self.w 
            self.set_xy(doc_w/2,-15)
            self.set_font('helvetica', 'I', 10)
            # page number
            self.cell(10, 10, f'Page {self.page_no()}/{{nb}}')  

    '''

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
    filePipingGroups = os.path.join(sessionDir, f"piping_groups_{st.session_state.session_id}.csv")
    with open(filePipingGroups) as pip_input:
        readerpip = csv.reader(pip_input)
        
        # Ottieni le intestazioni (prima riga)
        header = next(readerpip)
        
        # Modifica la prima colonna se il nome è 'Unnamed: 0.1'
        if header[0] == 'Unnamed: 0.1':
            header[0] = 'id'  # Rinomina la prima colonna
        
        
        # Leggi i dati rimanenti
        datapip = [rowpip for rowpip in readerpip]

    # Aggiungi la nuova intestazione ai dati
    datapip.insert(0, header)

    #leggi risultati da Output.csv
    #with open('files/Output.csv') as output:

    #leggi risultati da piping_report.csv
    filePipingReport = os.path.join(sessionDir, f"piping_report_{st.session_state.session_id}.csv")
    with open(filePipingReport) as pipOutput:    
        readerout = csv.reader(pipOutput)
        
        # Leggi la prima riga e memorizzala
        #first_line = ', '.join(next(readerout))
        
        # Leggi la seconda riga e memorizzala
        #second_line = ', '.join(next(readerout))
        
        # Salta la terza riga
        #next(readerout)
 
        # Leggi le righe successive e formattale
        #out = []
        #for rowout in readerout:
        #    formatted_row = []
        #    for value in rowout:
        #        try:
        #            # Prova a convertire in float e formattare
        #            formatted_value = f"{float(value):.3f}"
        #        except ValueError:
        #            # Se non è un numero, lascia il valore originale
        #            formatted_value = value
        #        formatted_row.append(formatted_value)
        #    out.append(formatted_row)

    # Ora `out` contiene i valori con tre cifre decimali per i numeri.
    # Ottieni le intestazioni (prima riga)
        headerpipOutput = next(readerout)
        
        # Modifica la prima colonna se il nome è 'Unnamed: 0.1'
        if headerpipOutput[0] == 'Unnamed: 0.1':
            headerpipOutput[0] = 'id'  # Rinomina la prima colonna
        
        # Leggi i dati rimanenti
        datapipOutput = [row for row in readerout]

    # Aggiungi la nuova intestazione ai dati
    datapipOutput.insert(0, headerpipOutput)

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
    pdf.create_table(table_data = datapip, title='Piping Data', cell_width='uneven')
    #pdf.ln()
    #pdf.ln()


    pdf.add_page()
    #pdf.create_table(Output)
    pdf.create_table(table_data = datapipOutput, title='Output', cell_width='uneven')
    pdf.ln()
    #pdf.ln()

    pdf.add_page()

    pdf.set_font('times', 'BU', 12)
    pdf.cell(80,10, 'Piping Groups Rating', ln=1, border=False)

    pdf.set_font('times', '', 10)

    # Percorso file
    file_path = os.path.join(sessionDir, f"groupRatingInfo_{st.session_state.session_id}.json")
    #file_path = os.path.join("files", "groupRatingInfo.json")

    # Carica la lista
    with open(file_path, "r") as f:
        ratingPipingGroup = json.load(f)

    # Scorri tutti i gruppi e stampa le variabili su righe consecutive
    for group_name, variabili in ratingPipingGroup.items():
        dia_min = variabili.get("dia_min")
        dia_max = variabili.get("dia_max")
        dia_rating = variabili.get("dia_rating")

        MAWP_min = variabili.get("MAWP_min")
        
        phrase = f"- RATING for material group {group_name} (NPS range from `{dia_min}` to `{dia_max}`) is determined by: NPS = {dia_rating}, MAWP = {MAWP_min:.2f} bar"
        #st.write(f"🔹 **{group_name}** ({D_min} - {D_max}) Rating = {MAWP}")
        
        pdf.cell(80,10, phrase, ln=1, border=False)



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
    pipReportPdf = os.path.join(sessionDir, f"report1_{st.session_state.session_id}.pdf")

    pdf.output(pipReportPdf)

    

