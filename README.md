# Webová aplikácia - Analýza Nezamestnanosti na Slovensku


> Webová aplikácia vytvorená pomocou **Streamlit**, ktorá umožňuje používateľom vykonávať dátovú analýzu prostredníctvom vizualizovaných dát. Táto webová aplikácia je súčasťou praktickej časti bakalárskej práce s názvom **Využitie dátovej analytiky v oblasti pracovného trhu**.


## Obsah bakalárskej práce
>Bakalárska práca sa zameriava na deskriptívnu analýzu nezamestnanosti na Slovensku a odhaľovaní vplyvných faktorov - región, pohlavie, vek, vzdelanie a ekonomické odvetvie.
>Súčasťou práce je aj predikcia nezamestnanosti pomocou predikčného modelu Auto-ARIMA, ktorý predikuje vývoj nezamestnanosti na nasledujúci rok.


## Použité technológie a knižnice
- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**
- **Plotly**
- **Auto_arima**
- **Os**


## Zdroje dát
Všetky využité dáta sú verejne dostupné na **Štatistickom úradu SR** a pokrývajú časové obdobie 2005 - 2025 <br>
Použité datasety:
- Nezamestnaní podľa veku (od roku 2021) [pr3117qr]
- Nezamestnaní podľa veku (do roku 2020) [pr3817qr]
- Nezamestnaní podľa vzdelania (do roku 2020) [pr3818qr]
- Nezamestnaní podľa vzdelania (do roku 2020) [pr3818qr]
- Nezamestnaní podľa ekonomickej činnosti (SK NACE Rev. 2) posledného zamestnania a pohlavia - ročné údaje [pr2024rs]
- Nezamestnaní podľa ekonomickej činnosti (SK NACE Rev. 2) posledného zamestnania a pohlavia - ročné údaje (do roku 2020) [pr2830rs] (od roku 2008 - 2025)

## Štruktúra projektu
<pre> 
Streamlit_app/
│
├── Appka/
│   ├── .streamlit/
│   │   └── config.toml
│   │
│   ├── app_pages/
│   │   ├── home_page.py
│   │   └── predikcia_page.py
│   │
│   ├── app.py
│   ├── dataset.csv
│   ├── dataset_odvetvie.csv
│   └── requirements.txt
│
├── README.md
└── LICENCE

</pre>

## Prístup k aplikácii
Na tomto odkaze sa nachádza webová aplikácia [Analýza Nezamestnanosti na Slovensku](https://appbianca.streamlit.app/)

## Autor
Bianca Estefánová, 2025
