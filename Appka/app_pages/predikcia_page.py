import streamlit as st
import pandas as pd
import plotly.express as px
from pmdarima import auto_arima
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "..", "dataset.csv"))
df_odvetvie = pd.read_csv(os.path.join(BASE_DIR, "..", "dataset_odvetvie.csv"))

df_melted = df.melt(id_vars=["region", "pohlavie", "typ_skupiny", "skupina"], var_name="rok", value_name="nezamestnanost")
df_melted["rok"] = df_melted["rok"].astype(int)

df_odvetvie["Hodnota"] = pd.to_numeric(df_odvetvie["Hodnota"].str.replace(",", "."), errors="coerce")

st.set_page_config(page_title="App", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
st.title("Predikcia nezamestnanosti")

# SIDEBAR
st.sidebar.header("Vyber si filtre pre prvý dataset")

selected_region = st.sidebar.multiselect("Zvoľ si región", options=df_melted["region"].unique(), default=["Slovenská republika"])
selected_pohlavie = st.sidebar.multiselect("Zvoľ si pohlavie", options=df_melted["pohlavie"].unique(), default=["Muži", "Ženy"])
selected_typ = st.sidebar.selectbox("Zvoľ si typ skupiny", options=df_melted["typ_skupiny"].unique())

if selected_typ == "Vek":
    selected_skupina = st.sidebar.multiselect("Zvoľ si vekovú skupinu", options=df_melted[df_melted["typ_skupiny"] == "Vek"]["skupina"].unique(), default=["25-34"])
else:
    selected_skupina = st.sidebar.multiselect("Zvoľ si vzdelanie", options=df_melted[df_melted["typ_skupiny"] == "Vzdelanie"]["skupina"].unique(), default=["Vysokoškolské"])

selected_roky = st.sidebar.slider("Zvoľ si roky", min_value=df_melted["rok"].min(), max_value=df_melted["rok"].max(), value=(2005, 2025), step=1)

filtered_df = df_melted[
    (df_melted["region"].isin(selected_region)) &
    (df_melted["pohlavie"].isin(selected_pohlavie)) &
    (df_melted["skupina"].isin(selected_skupina)) &
    (df_melted["rok"].between(selected_roky[0], selected_roky[1]))
]

st.sidebar.divider()
st.sidebar.header("Vyber si filtre pre druhý dataset")

selected_pohlavie_odvetvie = st.sidebar.multiselect("Zvoľ si pohlavie", options=df_odvetvie[df_odvetvie["Pohlavie"] != "Spolu"]["Pohlavie"].unique(), default=["Muži", "Ženy"], key="pohlavie_odvetvie")
selected_odvetvie = st.sidebar.multiselect("Zvoľ si odvetvie", options=df_odvetvie["Odvetvie"].unique(), default=["M Odborné, vedecké a technické činnosti"])
selected_roky_odvetvie = st.sidebar.slider("Zvoľ si roky", min_value=df_odvetvie["Rok"].min(), max_value=df_odvetvie["Rok"].max(), value=(2008, 2025), step=1)

filtered_df_odvetvie = df_odvetvie[
    (df_odvetvie["Pohlavie"].isin(selected_pohlavie_odvetvie)) &
    (df_odvetvie["Odvetvie"].isin(selected_odvetvie)) &
    (df_odvetvie["Rok"].between(selected_roky_odvetvie[0], selected_roky_odvetvie[1]))
]

#DATASET
st.subheader("Predikcia nezamestnanosti pre prvý dataset")
st.caption("Predikcia počtu nezamestnaných v tisícoch pre ďalší rok podľa zvolených filtrov")

if filtered_df.empty:
    st.warning("Žiadne dáta pre zvolené filtre")
else:
    agg_df = filtered_df.groupby("rok", as_index=False)["nezamestnanost"].mean()
    ts = agg_df.set_index("rok")["nezamestnanost"]

    if len(ts) < 5:
        st.warning("Pre predikciu potrebuješ aspoň 5 rokov dát")
    else:
        with st.spinner("Počítam predikciu..."):
            model = auto_arima(ts, seasonal=False, trace=False, error_action="ignore", suppress_warnings=True)
            prediction = model.predict(n_periods=1)
            next_year = selected_roky[1] + 1
            predicted_value = round(prediction.iloc[0], 2)

        real_next = df_odvetvie[
            (df_odvetvie["Pohlavie"].isin(selected_pohlavie_odvetvie)) &
            (df_odvetvie["Odvetvie"].isin(selected_odvetvie)) &
            (df_odvetvie["Rok"] == next_year)]["Hodnota"].mean()

        with st.expander("Porovnanie predikcie s reálnymi dátami"):
            if not pd.isna(real_next):
                real_value = round(real_next, 2)
                delta = round(predicted_value - real_value, 2)
                
                st.metric(label=f"Predikovaná nezamestnanosť pre rok {next_year}", value=predicted_value, delta=f"{real_value} oproti reálnej hodnote {delta}", delta_color="inverse")
            else:
                st.metric(label=f"Predikovaná nezamestnanosť pre rok {next_year}", value=predicted_value)
                st.info("Reálne dáta pre predikovaný rok nie sú k dispozícii")

        #Graf predikcie
        df_prediction = pd.DataFrame({
            "rok": list(agg_df["rok"]) + [next_year],
            "nezamestnanost": list(agg_df["nezamestnanost"]) + [predicted_value],
            "Dáta": ["Reálne"] * len(agg_df) + ["Predikcia"]})

        line_pred = px.line(df_prediction, x="rok", y="nezamestnanost", color="Dáta", markers=True, title=f"Predikcia nezamestnanosti pre rok {next_year}", color_discrete_map={"Reálne": "#2EC4B6", "Predikcia": "#FFE066"})
        line_pred.update_layout(xaxis_title="Rok", yaxis_title="Počet nezamestnaných v tisícoch", xaxis=dict(dtick=1, tickformat="d"))
        st.plotly_chart(line_pred, use_container_width=True)


st.divider()

#DATASET 2
st.subheader("Predikcia nezamestnanosti pre druhý dataset")
st.caption("Predikcia počtu nezamestnaných v tisícoch pre ďalší rok podľa odvetvia")

if filtered_df_odvetvie.empty:
    st.warning("Žiadne dáta pre zvolené filtre")
else:
    agg_df_odvetvie = filtered_df_odvetvie.groupby("Rok", as_index=False)["Hodnota"].mean()
    ts_odvetvie = agg_df_odvetvie.set_index("Rok")["Hodnota"].dropna()

    if len(ts_odvetvie) < 5:
        st.warning("Pre predikciu potrebuješ aspoň 5 rokov dát")
    else:
        with st.spinner("Počítam predikciu..."):
            model_odvetvie = auto_arima(ts_odvetvie, seasonal=False, trace=False, error_action="ignore", suppress_warnings=True)
            prediction_odvetvie = model_odvetvie.predict(n_periods=1)
            next_year_odvetvie = selected_roky_odvetvie[1] + 1
            predicted_value_odvetvie = round(prediction_odvetvie.iloc[0], 2)

        real_next_odvetvie = df_odvetvie[
            (df_odvetvie["Pohlavie"].isin(selected_pohlavie_odvetvie)) &
            (df_odvetvie["Odvetvie"].isin(selected_odvetvie)) &
            (df_odvetvie["Rok"] == next_year_odvetvie)]["Hodnota"].mean()

        with st.expander("Porovnanie predikcie s reálnymi dátami"):
            if not pd.isna(real_next_odvetvie):
                real_value_odvetvie = round(real_next_odvetvie, 2)
                delta_odvetvie = round(predicted_value_odvetvie - real_value_odvetvie, 2)
                
                st.metric(label=f"Predikovaná nezamestnanosť pre rok {next_year_odvetvie}", value=predicted_value_odvetvie, delta=f"{real_value_odvetvie} oproti reálnej hodnote {delta_odvetvie}", delta_color="inverse")
            else:
                st.metric(label=f"Predikovaná nezamestnanosť pre rok {next_year_odvetvie}", value=predicted_value_odvetvie)
                st.info("Reálne dáta pre predikovaný rok nie sú k dispozícii")

        # Graf s predikciou
    df_prediction_odvetvie = pd.DataFrame({
        "Rok": list(agg_df_odvetvie["Rok"]) + [next_year_odvetvie],
        "Hodnota": list(agg_df_odvetvie["Hodnota"]) + [predicted_value_odvetvie],
        "Dáta": ["Reálne"] * len(agg_df_odvetvie) + ["Predikcia"]})

    line_pred_odvetvie = px.line(df_prediction_odvetvie, x="Rok", y="Hodnota", color="Dáta", markers=True, title=f"Predikcia nezamestnanosti podľa odvetvia pre rok {next_year_odvetvie}", color_discrete_map={"Reálne": "#2EC4B6", "Predikcia": "#FFE066"})
    line_pred_odvetvie.update_layout(xaxis_title="Rok", yaxis_title="Počet nezamestnaných v tisícoch", xaxis=dict(dtick=1, tickformat="d"))
    st.plotly_chart(line_pred_odvetvie, use_container_width=True)
