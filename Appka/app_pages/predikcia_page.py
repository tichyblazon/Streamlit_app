import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import plotly.express as px

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "..", "dataset.csv"))

df_melted = df.melt(id_vars = ["region", "pohlavie","typ_skupiny", "skupina"], var_name = "rok", value_name = "nezamestnanost")
df_melted["rok"] = df_melted["rok"].astype(int)

st.set_page_config(page_title="App", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
st.title("Predikcia nezamestnanosti")


df_sr = df_melted[(df_melted["region"] == "Slovenská republika") & (df_melted["pohlavie"] == "Muži") & (df_melted["skupina"] == "25-34")].drop(columns=["region", "typ_skupiny", "pohlavie", "skupina"]).iloc[:0:-1]


df_sr["rok"] = pd.to_datetime(df_sr["rok"], format = "%Y")
df_sr = df_sr.set_index("rok")
with st.expander("Time series"):
    st.write(df_sr)

line_bar =px.line(df_sr, x = df_sr.index, y = "nezamestnanost")
line_bar.update_layout(xaxis_title="Rok", yaxis_title="Nezamestnanosť", title="Nezamestnanosť mužov vo veku 25-34 v Slovenskej republike")
st.plotly_chart(line_bar)

#https://www.influxdata.com/blog/python-ARIMA-tutorial-influxDB/
result = adfuller(df_sr['nezamestnanost'])
#st.write('ADF Statistic: %f' % result[0]) 
st.write('p-value: %f' % result[1]) #0,75 nie su stacionarne, treba diferencovat

df_sr_diff = df_sr.diff().dropna()
result1 = adfuller(df_sr_diff['nezamestnanost'])
st.write('p-value: %f' % result1[1])

train = df_sr_diff[:"2020"]
test = df_sr_diff["2021":]


model = ARIMA(df_sr_diff, order=(1,0,1)) 
model_fit = model.fit()

predictions = model_fit.forecast(steps=1)
st.write(predictions)

line_bar =px.line(df_sr_diff, x = df_sr_diff.index, y = "nezamestnanost")
line_bar.update_layout(xaxis_title="Rok", yaxis_title="Nezamestnanosť", title="Nezamestnanosť mužov vo veku 25-34 v Slovenskej republike")
st.plotly_chart(line_bar)
#https://medium.com/data-science/time-series-forecasting-using-auto-arima-in-python-bb83e49210cd
