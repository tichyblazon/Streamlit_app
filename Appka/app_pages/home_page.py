
import streamlit as st
import pandas as pd
import plotly.express as px
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "dataset.csv"))

#z wide formatu na long format
df_melted = df.melt(id_vars = ["region", "pohlavie","typ_skupiny", "skupina"], var_name = "rok", value_name = "nezamestnanost")
df_melted["rok"] = df_melted["rok"].astype(int)


st.set_page_config(page_title="Analýza trhu práce SK", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

st.title("Analýza Nezamestnanosti na Slovensku")
st.caption("Interaktívna analýza nezamestnanosti na Slovensku v rokoch 2005–2025 podľa regiónu, pohlavia, veku a vzdelania")
###
#ZACIATOK sidebar    
df_sr = df_melted[df_melted["region"] == "Slovenská republika"]


st.sidebar.header("Vyber si filter")

selected_region = st.sidebar.multiselect("Zvol region",options=df_melted["region"].unique(), default=df_sr["region"].unique())
selected_pohlavie = st.sidebar.multiselect("Zvol pohlavie",options=df_melted["pohlavie"].unique(), default=df_melted["pohlavie"].unique())
selected_roky = st.sidebar.slider("Zvol roky", min_value = df_melted["rok"].min(), max_value = df_melted["rok"].max(), value = (2005, 2025), step = 1)
selected_typ = st.sidebar.selectbox("Zvol typ skupiny",options=df_melted["typ_skupiny"].unique())
if selected_typ == "vek":
    selected_skupina = st.sidebar.multiselect("Zvol vekovu skupinu", options=df_melted[df_melted["typ_skupiny"] == "vek"]["skupina"].unique(), default=["25-34"])
    
else:
    selected_skupina = st.sidebar.multiselect("Zvol vzdelanie", options=df_melted[df_melted["typ_skupiny"] == "vzdelanie"]["skupina"].unique(), default=["Vysokoškolské"])


filtered_df = df_melted[
    (df_melted["region"].isin(selected_region)) &
    (df_melted["pohlavie"].isin(selected_pohlavie)) &
    (df_melted["skupina"].isin(selected_skupina)) &
    (df_melted["rok"].between(selected_roky[0], selected_roky[1]))
]

#KONIEC SIDEBARU
###

###
#STATISTIKY
#1 statistika
najhorsi_region = filtered_df.groupby("region")["nezamestnanost"].mean().idxmax()

#2 statistika
df_sr_vek = df[(df["region"] == "Slovenská republika") & 
               (df["typ_skupiny"] == "vek")
               ].drop(columns=["region", "typ_skupiny", "pohlavie", "skupina"]).mean().iloc[::-1]

#3 statistika gender gap
muzi_mean = filtered_df[filtered_df["pohlavie"] == "Muži"]["nezamestnanost"].mean()
zeny_mean = filtered_df[filtered_df["pohlavie"] == "Ženy"]["nezamestnanost"].mean()
gender_gap = (muzi_mean - zeny_mean)/100


col1, col2, col3 = st.columns(3)
col1.metric(label = "Region s najväčšou nezamestnanosťou", value = najhorsi_region, border=True)
col2.metric(label = "Priemerná Nezamestnanost v priebehu rokov na Slovensku na základe veku", value = "2005 - 2025", chart_data=df_sr_vek, chart_type="line", border=True) #nejako pospekulovat
col3.metric(label = "Gender gap", value = gender_gap, border=True, format = "percent")

#tu je error ked je nan hodnota a vyriesit tie 2020,5 a 2021,5 v datasetu, kedze su to priemery a nie realne roky, tak ich nahradit za 2020 a 2021, to sa da v update_layout urobit, ale skaredo to ukazuje grafy
#to lano v line grafe je len vtedy ak je viacero regionov, inak je to len jedna ciara a nevyzera to pekne, takze tam dat podmienku, ze ak je len jeden region, tak line_shape="linear" a ak je viacero regionov, tak line_shape="spline"

###
#GRAFY



if selected_typ == "vek":
    bar_graph_title = "Nezamestnanosť podľa veku v priebehu rokov"
else:
    bar_graph_title = "Nezamestnanosť podľa vzdelania v priebehu rokov"

cols_graphs_first = st.columns(1)
with cols_graphs_first[0]:
    bar_graph_1 = px.bar(filtered_df, x="rok", y="nezamestnanost", color="pohlavie", barmode= "group", color_discrete_sequence=px.colors.qualitative.Set3, title=bar_graph_title, hover_data=["skupina"], facet_col="region")
    #bar_graph_1.update_traces(marker_line_color="grey", marker_line_width=0.4)
    st.plotly_chart(bar_graph_1)







if selected_typ == "vek":
    boxplot_title = "Rozloženie Nezamestnanosti podľa Veku"
else:    
    boxplot_title = "Rozloženie Nezamestnanosti podľa Vzdelania"

cols_graphs_second=st.columns(3)
with cols_graphs_second[0]:
    region_pohlavie_agg = filtered_df.groupby(["region", "pohlavie"], as_index=False)["nezamestnanost"].mean()
    bar_graph_2 = px.bar(region_pohlavie_agg, x="region", y="nezamestnanost", color="pohlavie", barmode= "group", color_discrete_sequence=px.colors.qualitative.Set3, title="Priemerná Nezamestnanosť v Regiónoch")
    bar_graph_2.update_layout(title = boxplot_title, xaxis_title = "Región", yaxis_title = "Nezamestnanosť")
    bar_graph_1.update_traces(marker_line_color="grey", marker_line_width=0.4)
    st.plotly_chart(bar_graph_2)
    
with cols_graphs_second[1]:  
    boxplot_graph = px.box(filtered_df,x = "skupina", y = "nezamestnanost", color = "pohlavie", color_discrete_sequence=px.colors.qualitative.Set3, facet_col="region", facet_col_spacing = 0.2, title=boxplot_title)
    boxplot_graph.update_layout(title = boxplot_title, xaxis_title = "Skupina", yaxis_title = "Nezamestnanosť")
    st.plotly_chart(boxplot_graph)

with cols_graphs_second[2]:
    scatter = px.scatter(filtered_df, x = "rok", y = "skupina", color = "nezamestnanost", color_discrete_sequence=px.colors.qualitative.Set3, size = "nezamestnanost", title="Scatter")
    #scatter.update_layout(xaxis_title="Rok", yaxis_title="Nezamestnanosť")
    st.plotly_chart(scatter)
    #tu hadze error ohladom nan hodnot pri vzdelani
