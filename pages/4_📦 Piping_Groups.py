import streamlit as st
import pandas as pd
import fractions
import os

st.set_page_config(page_title="Piping_Groups", layout="centered")
st.title("📦 Pipe Groups")

with st.expander("🆘 Help"):
    st.markdown("""
    - **What to do here?**  
      In the table below You can see the stored piping groups. By clicking the check box '***Activate/Deactivate***' You can enter in **modification mode**.
               
    - **Before to go on ...**  
      After modifications or adding of new groups You have to click on the button '💾***Save groups***', that appears below, to apply and save modifications . 
      
    - **further information:**  
      click on ℹ️ info button menu]
    """)

#    === Controllo accesso ===
if 'prot' not in st.session_state:
    st.session_state.prot = False
    
if st.session_state.prot == False:
    st.info('unauthorized access')
    st.stop()


# === Parametro: numero massimo di gruppi ===
n_max = 4

# === Caricamento file dati statici ===
df_allow = pd.read_csv("files/Allowables.csv", sep=";")
df_Y = pd.read_csv("files/Table304_1_1.csv", sep=";")
df_diam = pd.read_csv("files/diametri.csv")  # contiene colonna "Diam"

# === Funzione per parsare diametri frazionari ===
def parse_diameter(d):
    try:
        return float(sum(fractions.Fraction(part) for part in d.strip().split()))
    except:
        return float('inf')

diametri_raw = df_diam["Diam"].dropna().astype(str).unique()
diametri = sorted(diametri_raw, key=parse_diameter)

# === Funzione di interpolazione ==========================
def interpolazione(materiale, temperatura):
    riga = df_allow[df_allow["Pipe_description"] == materiale]
    code_y = riga["Code_Y"].values[0]
    code_toll = riga["codeTol"].values[0]

    col_temp = [col for col in riga.columns if col.startswith("T_")]
    dati_temp = {
        float(col.replace("T_", "").replace("°C", "").replace(",", ".")): riga[col].values[0]
        for col in col_temp if not pd.isna(riga[col].values[0])
    }
    dati_temp = dict(sorted(dati_temp.items()))
    temp_list = list(dati_temp.keys())
    val_list = list(dati_temp.values())

    # Preparazione dati Y
    dfY_filtrato = df_Y[df_Y["Code_Y"] == code_y].copy()
    dfY_filtrato["TempC"] = dfY_filtrato["TempC"].astype(str).str.replace(",", ".").astype(float).round(1)
    dfY_filtrato["Yvalue"] = dfY_filtrato["Yvalue"].astype(str).str.replace(",", ".").astype(float).round(4)
    y_dict = dfY_filtrato.set_index("TempC")["Yvalue"].dropna().to_dict()
    y_list = [y_dict.get(t, None) for t in temp_list]

    # Interpolazione
    V_interp, Y_interp = None, None
    for i in range(len(temp_list) - 1):
        T1, T2 = temp_list[i], temp_list[i + 1]
        if T1 <= temperatura <= T2:
            V1, V2 = val_list[i], val_list[i + 1]
            V_interp = V1 + (V2 - V1) * (temperatura - T1) / (T2 - T1)
            Y1, Y2 = y_list[i], y_list[i + 1]
            if Y1 is not None and Y2 is not None:
                Y_interp = Y1 + (Y2 - Y1) * (temperatura - T1) / (T2 - T1)
            break

    return V_interp, Y_interp, code_y, code_toll


# === Caricamento gruppi esistenti se presenti ===
sessionDir = "sessions"
filePipeGroups = f"{sessionDir}/piping_groups_{st.session_state.session_id}.csv"

if os.path.exists(filePipeGroups):
    df_gruppi_caricati = pd.read_csv(filePipeGroups)
    st.markdown("### Existing Groups")
    st.dataframe(df_gruppi_caricati, hide_index=True)
else:
    df_gruppi_caricati = pd.DataFrame()
    st.info("No existing piping groups found.")

# === Pulsante per cancellare tutto e partire da zero ===
if st.button("🗑️ Clear all groups and start from scratch"):
    # tieni solo le intestazioni (DataFrame vuoto con le stesse colonne)
    df_empty = df_gruppi_caricati.iloc[0:0]
    # salva di nuovo il file con sole intestazioni
    df_empty.to_csv(filePipeGroups, index=False)
    #df_gruppi_caricati = pd.DataFrame()
    st.rerun()

# === Pulsante per mostrare sezione modifica gruppi ===
#if "show_groups" not in st.session_state:
#    st.session_state.show_groups = False

#if st.button("✏️ Change Groups"):
#    st.session_state.show_groups = True

    
# checkbox con stato
#checked = st.checkbox(
#    f":{st.session_state.colore1}[Activate]/:{st.session_state.colore2}[Deactivate] Input or Modification Section"
#)
checked = st.checkbox(
    ":red[**A**ctivate] / :gray[**D**eactivate] ➡️ Input or Modification Section"
)


# === Sezione modifica gruppi (compare solo dopo click) ===


if checked == True:
    
    st.markdown("### Modify / Add Groups")

    # Numero di gruppi
    if not df_gruppi_caricati.empty:
        num_gruppi = st.number_input(
            "🔢 Adjust number of piping groups",
            min_value=1, max_value=n_max,
            value=len(df_gruppi_caricati), step=1
        )
    else:
        num_gruppi = st.number_input(
            "🔢 Number of piping groups",
            min_value=1, max_value=n_max, value=1, step=1
        )

    materiali = df_allow["Pipe_description"].dropna().unique()
    gruppi_dati = []

    # Input completo dei gruppi (tutti i campi come nella tua versione originale)
    for i in range(int(num_gruppi)):
        with st.expander(f"➕ Group {i+1}"):
            gruppo = {}
            gruppo["Group"] = f"G_{i+1}"

            # Precompilazione se esiste
            if not df_gruppi_caricati.empty and i < len(df_gruppi_caricati):
                saved = df_gruppi_caricati.iloc[i]
            else:
                saved = {}

            gruppo["Material"] = st.selectbox(
                f"Material (Group {i+1})",
                materiali,
                index=0 if "Material" not in saved else list(materiali).index(saved["Material"]),
                key=f"mat_{i}"
            )
            gruppo["Temp"] = st.number_input(
                f"Temperature °C (Group {i+1})",
                value=100.0 if "Temp" not in saved else saved["Temp"],
                key=f"temp_{i}"
            )
            gruppo["Press"] = st.number_input(
                f"Pressure bar (Group {i+1})",
                value=1.0 if "Press" not in saved else saved["Press"],
                key=f"press_{i}"
            )
            gruppo["CA"] = st.number_input(
                f"Corrosion Allowance mm (Group {i+1})",
                value=3.0 if "CA" not in saved else saved["CA"],
                key=f"ca_{i}"
            )
            gruppo["E"] = st.number_input(
                f"Weld Joint Quality Factor E (Group {i+1})",
                min_value=0.0, max_value=1.0,
                value=1.0 if "E" not in saved else saved["E"],
                key=f"E_{i}"
            )
            gruppo["W"] = st.number_input(
                f"Weld Joint Strength Reduction Factor W (Group {i+1})",
                min_value=0.0, max_value=1.0,
                value=1.0 if "W" not in saved else saved["W"],
                key=f"W_{i}"
            )

            # Diametri
            diam_min_default = diametri[0] if "Dia_min" not in saved else str(saved["Dia_min"])
            diam_min_index = list(diametri).index(diam_min_default) if diam_min_default in diametri else 0
            diam_min = st.selectbox(
                f"Minimum Diameter (Group {i+1})",
                diametri,
                index=diam_min_index,
                key=f"min_diam_{i}"
            )

            diametri_filtrati = [d for d in diametri if parse_diameter(d) >= parse_diameter(diam_min)]
            diam_max_default = diametri_filtrati[-1] if "Dia_max" not in saved else str(saved["Dia_max"])
            diam_max_index = list(diametri_filtrati).index(diam_max_default) if diam_max_default in diametri_filtrati else len(diametri_filtrati)-1
            diam_max = st.selectbox(
                f"Maximum Diameter (Group {i+1})",
                diametri_filtrati,
                index=diam_max_index,
                key=f"max_diam_{i}"
            )

            gruppo["Dia_min"] = diam_min
            gruppo["Dia_max"] = diam_max

            # Qui puoi aggiungere la tua interpolazione Allow/Y come prima
            # Interpolazione
            V_interp, Y_interp, code_y, code_toll = interpolazione(gruppo["Material"], gruppo["Temp"])
            gruppo["Allow"] = round(V_interp, 2) if V_interp is not None else None
            gruppo["Y"] = round(Y_interp, 4) if Y_interp is not None else None
            #gruppo["Code_Y"] = code_y
            gruppo["codeTol"] = code_toll

            if V_interp is not None:
                st.success(f"Allowable Pressure: {V_interp:.2f} MPa")
            else:
                st.error("Temperature out of range for interpolation.")

            if Y_interp is not None:
                st.info(f"Interpolated Y: {Y_interp:.4f}")
            else:
                st.warning("Y not available.")


            gruppi_dati.append(gruppo)

    # Tabella finale solo in questa sezione
    st.markdown("### Pipe Groups Summary")
    df_finale = pd.DataFrame(gruppi_dati)
    st.dataframe(df_finale, hide_index=True)

    if st.button("💾 Save groups"):
        df_finale.to_csv(filePipeGroups, index=False)
        st.success("Piping groups saved successfully!")
        #st.rerun()


