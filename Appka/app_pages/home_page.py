
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Analýza trhu práce SK", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

st.title("Analýza Nezamestnanosti na Slovensku")
st.caption("Interaktívna analýza nezamestnanosti v rokoch 2005–2025 podľa regiónu, pohlavia, veku a vzdelania")

#DATASETY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "..", "dataset.csv"))
df_odvetvie = pd.read_csv(os.path.join(BASE_DIR, "..", "dataset_odvetvie.csv"))

#z wide formatu na long format
df_melted = df.melt(id_vars = ["region", "pohlavie","typ_skupiny", "skupina"], var_name = "rok", value_name = "Nezamestnaní v tisicoch")
df_melted["rok"] = df_melted["rok"].astype(int)
df_sr = df_melted[df_melted["region"] == "Slovenská republika"]

#desatinna ciarka v druhom datasete, nahradenie a pretypovaNie stlpca
df_odvetvie["Hodnota"] = df_odvetvie["Hodnota"].str.replace(",", ".").replace("-", float("nan")).astype(float)

#ZACIATOK sidebar 
st.sidebar.header("Vyber si filter pre prvý dataset")

selected_region = st.sidebar.multiselect("Zvoľ si región",options=df_melted["region"].unique(), default=df_sr["region"].unique())
selected_pohlavie = st.sidebar.multiselect("Zvoľ si pohlavie",options=df_melted["pohlavie"].unique(), default=df_melted["pohlavie"].unique())
selected_roky = st.sidebar.slider("Zvoľ si roky", min_value = df_melted["rok"].min(), max_value = df_melted["rok"].max(), value = (2005, 2025), step = 1)
selected_typ = st.sidebar.selectbox("Zvoľ si typ skupiny",options=df_melted["typ_skupiny"].unique())
if selected_typ == "Vek":
    selected_skupina = st.sidebar.multiselect("Zvoľ si vekovú skupinu", options=df_melted[df_melted["typ_skupiny"] == "Vek"]["skupina"].unique(), default=["25-34"])
    
else:
    selected_skupina = st.sidebar.multiselect("Zvoľ si vzdelanie", options=df_melted[df_melted["typ_skupiny"] == "Vzdelanie"]["skupina"].unique(), default=["Vysokoškolské"])

filtered_df = df_melted[
    (df_melted["region"].isin(selected_region)) &
    (df_melted["pohlavie"].isin(selected_pohlavie)) &
    (df_melted["skupina"].isin(selected_skupina)) &
    (df_melted["rok"].between(selected_roky[0], selected_roky[1]))
]

st.sidebar.divider()
st.sidebar.header("Vyber si filtre pre druhy dataset")

#filtre pre druhy dataset
selected_pohlavie_odvetvie = st.sidebar.multiselect("Zvoľ si pohlavie", options=df_odvetvie["Pohlavie"].unique(), default=["Spolu"])
selected_odvetvie = st.sidebar.multiselect("Zvoľ si odvetvie", options=df_odvetvie["Odvetvie"].unique(), default=["M Odborné, vedecké a technické činnosti"])
selected_roky_odvetvie = st.sidebar.slider("Zvoľ si roky", min_value = df_odvetvie["Rok"].min(), max_value = df_odvetvie["Rok"].max(), value = (2008, 2025), step = 1)

filtered_df_odvetvie = df_odvetvie[
    (df_odvetvie["Pohlavie"].isin(selected_pohlavie_odvetvie)) &
    (df_odvetvie["Odvetvie"].isin(selected_odvetvie)) &
    (df_odvetvie["Rok"].between(selected_roky_odvetvie[0], selected_roky_odvetvie[1]))
]
#KONIEC SIDEBARU

#WARNING
if len(filtered_df[["region", "pohlavie", "skupina"]])<1:
    st.warning("Zvoľ si inú kombináciu filtrov")

#STATISTIKY
#1 statistika
najhorsi_region = filtered_df.groupby("region")["Nezamestnaní v tisicoch"].mean().idxmax()


#2 statistika
df_sr_vek = df[(df["region"] == "Slovenská republika") & 
               (df["typ_skupiny"] == "Vek")
               ].drop(columns=["region", "typ_skupiny", "pohlavie", "skupina"]).mean().iloc[::-1]

#3 statistika gender gap
if filtered_df[filtered_df["pohlavie"] == "Muži"].empty or filtered_df[filtered_df["pohlavie"] == "Ženy"].empty:
    gender_gap = "Nie je možné určiť"
else:
    muzi_mean = filtered_df[filtered_df["pohlavie"] == "Muži"]["Nezamestnaní v tisicoch"].mean()
    zeny_mean = filtered_df[filtered_df["pohlavie"] == "Ženy"]["Nezamestnaní v tisicoch"].mean()
    gender_gap = round((muzi_mean - zeny_mean)*1000)

with st.expander("Štatistiky"):
    col1, col2, col3 = st.columns(3)
    col1.metric(label = "Region s najvačším počtom nezamestnaných ľudí", value = najhorsi_region, border=True)
    col2.metric(label = "Priemerný počet nezamestnaných ľudí v priebehu rokov na Slovensku na základe veku", value = "2005 - 2025", chart_data=df_sr_vek, chart_type="line", border=True) #nejako pospekulovat
    if gender_gap == "Nie je možné určiť":
        col3.metric(label = "Gender gap", value=gender_gap, border=True)
    elif gender_gap > 0:
        col3.metric(label = "Priemerne Mužov je viac nezamestnaných o", value=gender_gap, border=True)
    elif gender_gap < 0:
        col3.metric(label = "Priemerne Žien je viac nezamestnaných o", value=gender_gap*(-1), border=True)

#tu je error ked je nan hodnota a vyriesit tie 2020,5 a 2021,5 v datasetu, kedze su to priemery a nie realne roky, tak ich nahradit za 2020 a 2021, to sa da v update_layout urobit, ale skaredo to ukazuje grafy

#GRAFY 1 DATASET

if selected_typ == "Vek":
    bar_graph_title = "Počet nezamestnaných ľudí podľa veku v priebehu rokov"
    boxplot_title = "Rozloženie Počtu Nezamestnaných Ľudí podľa Veku"
    skupina = "Vek"
else:
    bar_graph_title = "Počet nezamestnaných ľudí podľa vzdelania v priebehu rokov"
    boxplot_title = "Rozloženie Počtu Nezamestnaných Ľudí podľa Vzdelania"
    skupina = "Vzdelanie"

cols_graphs_first = st.columns(1)
with cols_graphs_first[0]:
    bar_graph_1 = px.bar(filtered_df, x="rok", y="Nezamestnaní v tisicoch", color="pohlavie", barmode= "group", color_discrete_sequence=px.colors.qualitative.Set3, title=bar_graph_title, hover_data=["skupina"], facet_col="region")
    #bar_graph_1.update_traces(marker_line_color="grey", marker_line_width=0.4)
    bar_graph_1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(bar_graph_1)


cols_graphs_second=st.columns(3)
with cols_graphs_second[0]:
    region_pohlavie_agg = filtered_df.groupby(["region", "pohlavie"], as_index=False)["Nezamestnaní v tisicoch"].mean()
    bar_graph_2 = px.bar(region_pohlavie_agg, x="region", y="Nezamestnaní v tisicoch", color="pohlavie", barmode= "group", color_discrete_sequence=px.colors.qualitative.Set3, title="Priemerná Nezamestnanosť v Regiónoch")
    bar_graph_2.update_layout(title = boxplot_title, xaxis_title = "Región", yaxis_title = "Nezamestnaní v tisicoch")
    bar_graph_1.update_traces(marker_line_color="grey", marker_line_width=0.4)
    st.plotly_chart(bar_graph_2)
    
with cols_graphs_second[1]:  
    boxplot_graph = px.box(filtered_df,x = "skupina", y = "Nezamestnaní v tisicoch", color = "pohlavie", color_discrete_sequence=px.colors.qualitative.Set3, facet_col="region", facet_col_spacing = 0.2, title=boxplot_title)
    boxplot_graph.update_layout(title = boxplot_title, yaxis_title = "Nezamestnaní v tisicoch")
    boxplot_graph.update_xaxes(title_text=skupina)
    boxplot_graph.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(boxplot_graph)

with cols_graphs_second[2]:
    scatter = px.scatter(filtered_df, x = "rok", y = "skupina", color = "Nezamestnaní v tisicoch", color_discrete_sequence=px.colors.qualitative.Set3, size = "Nezamestnaní v tisicoch", title="Scatter")
    scatter.update_layout(xaxis_title="Rok",  yaxis_title=skupina, title="Počet nezamestnaných ľudí podľa skupiny v priebehu rokov")
    st.plotly_chart(scatter)
    #tu hadze error ohladom nan hodnot pri vzdelani

st.divider()

###
#DRUHY DATASET

#HEADER
st.subheader("Nezamestnanosť podľa odvetvia")
st.caption("Interaktívna Analýza počtu nezamestnaných v rokoch 2008–2025 podľa pohlavia a odvetvia")

#WARNING
if len(filtered_df_odvetvie[["Pohlavie", "Odvetvie"]])<1:
    st.warning("Zvoľ si inú kombináciu filtrov")

#STATISTIKY
#1 statistika
najhorsie_odvetvie = filtered_df_odvetvie.groupby("Odvetvie")["Hodnota"].mean().idxmax()

#2 statistika
posledny_rok = selected_roky_odvetvie[1]
predposledny_rok = selected_roky_odvetvie[1] - 1

rozdiel = round(filtered_df_odvetvie[filtered_df_odvetvie["Rok"] == posledny_rok]["Hodnota"].mean() - filtered_df_odvetvie[filtered_df_odvetvie["Rok"] == predposledny_rok]["Hodnota"].mean(),1)

#3 statistika
if "Muži" in selected_pohlavie_odvetvie and "Ženy" in selected_pohlavie_odvetvie:
    muzi_mean = filtered_df_odvetvie[filtered_df_odvetvie["Pohlavie"] == "Muži"]["Hodnota"].mean()
    zeny_mean = filtered_df_odvetvie[filtered_df_odvetvie["Pohlavie"] == "Ženy"]["Hodnota"].mean()
    gender_gap = round((muzi_mean - zeny_mean)*1000)
else:
    gender_gap = "Nie je možné určiť"

with st.expander( "Štatistiky"):
    col1, col2, col3 = st.columns(3)
    col1.metric(label = "Odvetvie najväčšou nezamestnanosťou", value = najhorsie_odvetvie, border=True)
    col2.metric(label = "Rozdiel Posledného a predposledného roka", value = f"{predposledny_rok} - {posledny_rok}", delta = rozdiel, delta_color="inverse" ,border=True)

    if gender_gap == "Nie je možné určiť":
        col3.metric(label = "Gender gap", value=gender_gap, border=True)
    elif gender_gap > 0:
        col3.metric(label = "Priemerne Mužov je viac nezamestnaných o", value=gender_gap, border=True)
    elif gender_gap < 0:
        col3.metric(label = "Priemerne Žien je viac nezamestnaných o", value=gender_gap*(-1), border=True)

#GRAFY 2 DATASET
cols_graphs_third = st.columns(2)
with cols_graphs_third[0]:
    line_graph = px.line(filtered_df_odvetvie, x="Rok", y="Hodnota", color="Pohlavie", color_discrete_sequence=px.colors.qualitative.Set3, facet_row="Odvetvie", facet_row_spacing= 0.2, title="Nezamestnanosť podľa odvetvia v priebehu rokov")
    line_graph.update_layout(xaxis_title = "Roky", yaxis_title = "Počet nezamestnaných v tisicoch")
    line_graph.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    #line_graph.update_yaxes(title_text="Počet nezamestnaných v tisícoch")
    st.plotly_chart(line_graph)

muzi_zeny_df_odvetvie = filtered_df_odvetvie[filtered_df_odvetvie["Pohlavie"] != "Spolu"]
agg_radar = filtered_df_odvetvie.groupby(["Odvetvie", "Pohlavie"], as_index=False)["Hodnota"].mean()

with cols_graphs_third [1]:
    radar_graph = px.line_polar(agg_radar, r = "Hodnota", theta = "Odvetvie", line_close= True, color= "Pohlavie", color_discrete_sequence=px.colors.qualitative.Pastel, hover_data="Hodnota", title="Počet nezamestnaných v odvetviach")
    radar_graph.update_traces(fill = "toself")
    radar_graph.update_polars(bgcolor="#0e0e0e")
    st.plotly_chart(radar_graph)


#TODO
#pridaj dalsie grafy, bar plot
