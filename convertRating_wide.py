import pandas as pd


# 1. Carica il file
df1 = pd.read_csv("files/Rating_Desc.csv", sep=";") 

df = pd.read_csv("files/Rating.csv", sep=";")

# 2. Converti la temperatura da °F a °C
df["TempC"] = ((df["TempF"] - 32) * 5 / 9).round(1)

# 3. Converti la pressione da psi a MPa
#df["AllowMPa"] = (df["AllowPsi"] / 145.0377).round(2)

# 4. Crea pivot: una riga per Rating_material, colonne per TempC, valori = AllowMPa
df_pivot = df.pivot_table(
    index="Rating_material",
    columns="TempC",
    values="AllowMPa",
    aggfunc="first"
)

# 5. Rinomina colonne (es: T_38.0°C)
df_pivot.columns = [f"T_{temp}°C" for temp in df_pivot.columns]

# 6. Reset index
df_pivot.reset_index(inplace=True)

# 7. Informazioni aggiuntive senza duplicati
col_info = ["Record_Nr", "Pipe_description", "Code_ASME", "Code_Y", "Code_Toll"]
df_info = df[col_info].drop_duplicates(subset="Pipe_description")

# 8. Merge finale
df_finale = pd.merge(df_info, df_pivot, on="Pipe_description", how="left")

# 9. Salva su nuovo CSV
df_finale.to_csv("files/Allowables.csv", sep=";", index=False)
