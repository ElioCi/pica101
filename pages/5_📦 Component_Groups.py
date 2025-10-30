import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Component_Groups", layout="centered")
st.title("📦 Component Groups")

with st.expander("🆘 Help"):
    st.markdown("""
    - **What to do here?**  
      In the table below You can see the stored component groups. By clicking the check box '***Activate/Deactivate***' You can enter in **modification mode**.
               
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
n_max = 3

# === Caricamento file rating/materiali ===
df_comp = pd.read_csv("files/Rating_Desc.csv", sep=";")
component = df_comp["cmp_material"].dropna().unique()
ratings = ['150', '300', '400', '600', '900', '1500', '2500', '4500']

# === Caricamento file gruppi salvati ===
sessionDir = "sessions"
file_path = f"{sessionDir}/comp_groups_{st.session_state.session_id}.csv"
#file_path = "files/component_groups.csv"

if os.path.exists(file_path):
    df_gruppi_caricati = pd.read_csv(file_path)
else:
    df_gruppi_caricati = pd.DataFrame()

# === Mostra gruppi esistenti ===
if not df_gruppi_caricati.empty:
    st.markdown("### Existing Groups")
    st.dataframe(df_gruppi_caricati, hide_index=True)

    if st.button("🗑️ Clear all groups and start from scratch"):
        # Ricreo file solo con intestazione
        df_vuoto = pd.DataFrame(columns=["Comp_Group", "Comp_Material", "id", "Rating"])
        df_vuoto.to_csv(file_path, index=False)
        st.success("All groups cleared. Start adding new ones from scratch.")
        df_gruppi_caricati = df_vuoto  # reset anche in sessione


checked = st.checkbox(
    ":red[**A**ctivate] / :gray[**D**eactivate] ➡️ Input or Modification Section"
)

# === Sezione modifica gruppi (compare solo dopo click) ===
if checked == True:

    # === Numero gruppi ===
    if not df_gruppi_caricati.empty:
        num_gruppi_comp = st.number_input(
            "🔢 Adjust number of component groups",
            min_value=1, max_value=n_max,
            value=len(df_gruppi_caricati), step=1
        )
    else:
        num_gruppi_comp = st.number_input(
            "🔢 Number of component groups",
            min_value=1, max_value=n_max,
            value=1, step=1
        )

    # === INPUT gruppi ===
    st.markdown("### Input / Modify Component Groups")
    gruppi_comp = []

    for i in range(int(num_gruppi_comp)):
        with st.expander(f"➕ Comp. Group {i+1}", expanded=True):
            gruppo_comp = {}
            gruppo_comp["Comp_Group"] = f"Cmp_G_{i+1}"

            # Precompila se esistono dati salvati
            if not df_gruppi_caricati.empty and i < len(df_gruppi_caricati):
                saved = df_gruppi_caricati.iloc[i]
            else:
                saved = {}

            selected_material = st.selectbox(
                f"Comp_Material (Group {i+1})",
                component,
                index=list(component).index(saved["Comp_Material"]) if "Comp_Material" in saved else 0,
                key=f"comp_mat_{i}"
            )
            gruppo_comp["Comp_Material"] = selected_material

            # id dal DataFrame Rating_desc
            code = df_comp.loc[df_comp["cmp_material"] == selected_material, "id"].values
            gruppo_comp["id"] = int(code[0]) if len(code) > 0 else None

            selected_rating = st.selectbox(
                f"Rating (Comp_Group {i+1})",
                ratings,
                index=ratings.index(str(saved["Rating"])) if "Rating" in saved and str(saved["Rating"]) in ratings else 0,
                key=f"rating_{i}"
            )
            gruppo_comp["Rating"] = selected_rating

            gruppi_comp.append(gruppo_comp)

    # === OUTPUT CSV ===
    st.markdown("### Component Groups Summary")
    df_finaleComp = pd.DataFrame(gruppi_comp)
    st.dataframe(df_finaleComp, hide_index=True)

    if st.button("💾 Save groups"):
        df_finaleComp.to_csv(file_path, index=False)
        st.success("Component groups saved successfully!")
