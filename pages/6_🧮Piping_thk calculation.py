import streamlit as st
import pandas as pd
from reportPDF import UpdateReportPdf
import json
import os
import base64

#    === Controllo accesso ===
if 'prot' not in st.session_state:
    st.session_state.prot = False
    
if st.session_state.prot == False:
    st.info('unauthorized access')
    st.stop()

# -------------------------------
# Funzioni di utilità
# -------------------------------

# Conversione "1 1/4" -> float
def convert_diameter(d):
    try:
        parts = d.strip().split()
        if len(parts) == 2:
            return float(parts[0]) + eval(parts[1])
        else:
            return eval(d.strip())
    except:
        return None


# Trova spessore commerciale >= richiesto
def get_next_thkCom(DN_label, thkCReq, thk_com_df):
    try:
        series = thk_com_df[DN_label].dropna().astype(float).sort_values()
        valid_thk = series[series >= thkCReq]
        if not valid_thk.empty:
            return round(valid_thk.iloc[0], 2)
        else:
            return None
    except KeyError:
        return None


# Calcolo MAWP per un gruppo (riutilizzabile)
def calculate_mawp_for_group(group_row, results, thkcom_list, toll_row):
    final_results = []
    c = 0.00
    code_toll = int(group_row["codeTol"])
    A, E, W, CA = group_row["Allow"], group_row["E"], group_row["W"], group_row["CA"]
    P_bar = group_row["Press"]
    P = P_bar * 0.1  # bar → MPa

    # Rimuove eventuali risultati già presenti per questo gruppo
    st.session_state.export_results = [
        r for r in st.session_state.export_results
        if r["Group"] != group_row["Group"]
    ]

    for i, row_result in enumerate(results):
        if i >= len(thkcom_list):
            continue

        DN_label = row_result["NPS"]
        D_mm = row_result["OD"]
        thkC = row_result["thkC"]
        thkCReq = row_result["thkCReq"]
        thkCom = thkcom_list[i]

        TOL = toll_row["Dia<18"] if D_mm <= 457.2 else toll_row["Dia>18"]

        # Calcolo t e MAWP
        if code_toll <= 4:
            t = ((100 - TOL) / 100) * thkCom - CA - c
        else:
            t = thkCom - CA - c - TOL

        if t <= 0 or (D_mm - 2 * t * (TOL / 100 if code_toll <= 4 else 1)) <= 0:
            MAWP = 0.0
        else:
            denom = D_mm - 2 * t * (TOL / 100 if code_toll <= 4 else 1)
            MAWP = (2 * t * A * E * W) / denom   # MPa → bar dopo

        status = "Ok" if MAWP >= P else "Fail"

        final_results.append({
            "NPS": DN_label,
            "OD": round(D_mm, 2),
            "thkC": round(thkC, 2),
            "thkCReq": round(thkCReq, 2),
            "thkCom": round(thkCom, 2),
            "MAWP": round(MAWP * 10, 2),
            "Check": status
        })

        # Salva nel session state
        st.session_state.export_results.append({
            "Group": group_row["Group"],
            "Material": group_row["Material"],
            "NPS": DN_label,
            "OD": round(D_mm, 2),
            "codeTol": code_toll,
            "TOL": round(TOL, 2),
            "thkC": round(thkC, 2),
            "thkCReq": round(thkCReq, 2),
            "thkCom": round(thkCom, 2),
            "MAWP": round(MAWP * 10, 2),
            "E": E,
            "W": W,
            "CA": CA,
            "c": c,
        })
    return final_results



# -------------------------------
# Inizializzazione
# -------------------------------
if "export_results" not in st.session_state:
    st.session_state.export_results = []
if "auto_calc_done" not in st.session_state:
    st.session_state.auto_calc_done = False

# --------------------------------------------------------------------
# Lettura dati dinamici dalla sessione ID utente e statici da files
# --------------------------------------------------------------------
sessionDir = "sessions"
filePipingGroups = os.path.join(sessionDir, f"piping_groups_{st.session_state.session_id}.csv")

piping_df = pd.read_csv(filePipingGroups)
diametri_df = pd.read_csv("files/diametri.csv", names=["NPS"])
ext_dia_df = pd.read_csv("files/ExtDia.csv", delimiter=";")
tolleranze_df = pd.read_csv("files/Tolerance.csv", delimiter=";")

thk_com_df = pd.read_csv("files/Dia_thk.csv", delimiter=";", index_col=0)
thk_com_df.columns = thk_com_df.columns.str.strip()
thk_com_df = thk_com_df.apply(lambda col: col.astype(str).str.replace(",", ".")).astype(float)

# Pulizia
diametri_df["NPS"] = diametri_df["NPS"].astype(str).str.strip()
ext_dia_df["NPS"] = ext_dia_df["NPS"].astype(str).str.strip()
ext_dia_df["Dia"] = ext_dia_df["Dia"].str.replace(",", ".").astype(float)

diametri_df = diametri_df.merge(ext_dia_df[["NPS", "Dia"]], on="NPS", how="left")
diametri_df["Diam_val"] = diametri_df["NPS"].apply(convert_diameter)

for col in ["Dia<18", "Dia>18"]:
    tolleranze_df[col] = tolleranze_df[col].str.replace(",", ".").astype(float)


# -------------------------------
# Interfaccia Streamlit
# -------------------------------
st.title("🧮 Thickness calculation")
with st.expander("🆘 Help"):
    st.markdown("""
    - **What to do here?**  
      This module gives you a first calculation with commercial thickness given on the basis of the calculated ones for each diameter. 
      You can change them by expanding each group, manually updating the proposal thickness values, and runnning again the calculation. 
                                           

    """)

for idx, group_row in piping_df.iterrows():
    with st.expander(f"➕ *Group {idx+1}*"):
        color = "blue"
        st.markdown(f"<h3 style='color:{color}'>{group_row['Material']}</h3>", unsafe_allow_html=True)

        D1_str, D2_str = str(group_row["Dia_min"]).strip(), str(group_row["Dia_max"]).strip()
        D1_val, D2_val = convert_diameter(D1_str), convert_diameter(D2_str)

        group_diam_df = diametri_df[
            (diametri_df["Diam_val"] >= D1_val) & (diametri_df["Diam_val"] <= D2_val)
        ].copy()
        group_diam_df = group_diam_df.dropna(subset=["Dia"])

        if group_diam_df.empty:
            st.warning(f"No valid diameter for group {group_row['Group']}")
            continue

        # Parametri formula
        P_bar = group_row["Press"]
        P = P_bar * 0.1
        CA = group_row["CA"]
        E = group_row["E"]
        W = group_row["W"]
        A = group_row["Allow"]
        Y = group_row["Y"]
        code_toll = int(group_row["codeTol"])

        toll_row = tolleranze_df[tolleranze_df["Tol_Code"] == code_toll].iloc[0]

        # Calcoli preliminari
        results = []
        for _, d_row in group_diam_df.iterrows():
            DN_label = d_row["NPS"]
            D_mm = d_row["Dia"]
            TOL = toll_row["Dia<18"] if D_mm <= 457.2 else toll_row["Dia>18"]

            thkC = (P * D_mm) / (2 * (A * E * W + P * Y))
            if code_toll <= 4:
                thkCReq = (thkC + CA) / ((100 - TOL) / 100)
            else:
                thkCReq = thkC + CA + TOL

            thkCReq = round(thkCReq, 2)
            thkCom_sugg = get_next_thkCom(DN_label, thkCReq, thk_com_df)
            results.append({
                "NPS": DN_label,
                "OD": round(D_mm, 2),
                "thkC": round(thkC, 2),
                "thkCReq": thkCReq,
                "thkCom_sugg": thkCom_sugg
            })

        df_result = pd.DataFrame(results)
        st.dataframe(df_result, use_container_width=True, hide_index=True)

        # Input spessori commerciali
        st.markdown("##### *Confirm or modify commercial thickness:*")
        thkcom_list = []
        for i, row_result in enumerate(results):
            DN_label = row_result["NPS"]
            D_mm = row_result["OD"]
            thkCReq = row_result["thkCReq"]
            thkCom_sugg = get_next_thkCom(DN_label, thkCReq, thk_com_df)

            if thkCom_sugg is None:
                st.error(f"❌ No Commercially available wall thickness ≥ {thkCReq} mm for DN {DN_label}")
                thkCom_input = thkCReq
            else:
                thkCom_input = st.number_input(
                    f'Commercial thickness for DN={DN_label} inches (value in mm)',
                    min_value=thkCReq,
                    value=thkCom_sugg,
                    step=0.1,
                    format="%.2f",
                    key=f"{group_row['Group']}_{DN_label}_thkCom"
                )
            thkcom_list.append(thkCom_input)

        # --- Calcolo automatico (solo alla prima apertura) ---
        if not st.session_state.auto_calc_done:
            auto_results = calculate_mawp_for_group(group_row, results, thkcom_list, toll_row)
            st.markdown("### ✅ MAWP (Auto-calculated)")
            st.dataframe(pd.DataFrame(auto_results), use_container_width=True, hide_index=True)
        else:
            st.markdown("*(You can recalculate MAWP manually below)*")

        # Pulsante ricalcolo manuale
        if st.button(f"🧮 Calculate MAWP for group {group_row['Group']}", key=f"btn_{group_row['Group']}"):
            manual_results = calculate_mawp_for_group(group_row, results, thkcom_list, toll_row)
            st.markdown("### ✅ MAWP (Manual calculation)")
            st.dataframe(pd.DataFrame(manual_results), use_container_width=True, hide_index=True)

# Segna che l’autocalcolo è stato eseguito
st.session_state.auto_calc_done = True

# -------------------------------
# Esportazione risultati e report
# -------------------------------
if st.session_state.export_results:
    df_export = pd.DataFrame(st.session_state.export_results)
    df_export = df_export.sort_values(by=["Group", "OD"])

    group_rating_info = []
    ratingPipingGroup = {}

    for group_name, group_df in df_export.groupby("Group"):
        min_row = group_df.loc[group_df["MAWP"].idxmin()]
        Material = min_row["Material"]
        MAWP_min = min_row["MAWP"]
        dia_rating = min_row["NPS"]
        OD = min_row["OD"]
        code_toll_Rating = int(min_row["codeTol"])
        TOL_rating = min_row["TOL"]
        thkCom_rating = min_row["thkCom"]
        E_rating = min_row["E"]
        W_rating = min_row["W"]
        CA_rating = min_row["CA"]
        c_rating = min_row["c"]

        #st.write("Groups in piping_df:", piping_df["Group"].tolist())
        #st.write("Groups in df_export:", df_export["Group"].unique().tolist())

        original_group = piping_df[piping_df["Group"] == group_name].iloc[0]
        dia_min = str(original_group["Dia_min"]).strip()
        dia_max = str(original_group["Dia_max"]).strip()

        phrase = f"- RATING for **{group_name}** (NPS range from `{dia_min}` to `{dia_max}`) is determined by: **NPS = {dia_rating}**, MAWP = {MAWP_min:.2f} bar"
        group_rating_info.append(phrase)

        ratingPipingGroup[group_name] = {
            "Material": Material,
            "dia_min": dia_min,
            "dia_max": dia_max,
            "dia_rating": dia_rating,
            "OD": OD,
            "codeTol": code_toll_Rating,
            "TOL_rating": TOL_rating,
            "thkCom_rating": thkCom_rating,
            "MAWP_min": MAWP_min,
            "E_rating": E_rating,
            "W_rating": W_rating,
            "CA_rating": CA_rating,
            "c_rating": round(float(c_rating), 2)
        }

    st.markdown("### 📌 Group Ratings Summary")
    for phrase in group_rating_info:
        st.markdown(phrase)

    file_path = os.path.join(sessionDir, f"groupRatingInfo_{st.session_state.session_id}.json")
    with open(file_path, "w") as f:
        json.dump(ratingPipingGroup, f, indent=4)

    df_export = df_export.drop(columns=["codeTol", "E", "W", "CA", "c"], errors="ignore")
    filePipingReport = os.path.join(sessionDir, f"piping_report_{st.session_state.session_id}.csv")
    df_export.to_csv(filePipingReport, index=False)

    csv_file = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Scarica risultati in CSV",
        data=csv_file,
        file_name="Piping_Thickness_Results.csv",
        mime="text/csv"
    )

    UpdateReportPdf()
    pdfReport = os.path.join(sessionDir, f"report1_{st.session_state.session_id}.pdf")

    if "show_pdf" not in st.session_state:
        st.session_state.show_pdf = False

    def toggle_pdf():
        st.session_state.show_pdf = not st.session_state.show_pdf

    st.markdown("<hr style='border: 0.5px solid red;'>", unsafe_allow_html=True)

    label = "👁️ Preview Report" if not st.session_state.show_pdf else "❌ Close Preview"
    st.button(label, on_click=toggle_pdf, key="toggle_pdf_btn")

    if st.session_state.show_pdf:
        with open(pdfReport, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)

    with open(pdfReport, "rb") as pdf_file:
        st.sidebar.download_button(
            label="💾 Download Report",
            data=pdf_file,
            file_name="ReportPipingThk.pdf",
            mime="application/pdf",
            help='***Save Report in your local drive***'
        )

