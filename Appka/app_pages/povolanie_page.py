import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import plotly.express as px

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

df = pd.read_csv("dataset.csv")

df_melted = df.melt(id_vars = ["region", "pohlavie","typ_skupiny", "skupina"], var_name = "rok", value_name = "nezamestnanost")
df_melted["rok"] = df_melted["rok"].astype(int)

st.set_page_config(page_title="App", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
st.title("Nezamestnanost podľa ekonomickej činnosti")

