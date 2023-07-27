import pycurl
import certifi
import json
from io import BytesIO
import pandas as pd
import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import re

apikey = st.secrets["apikey"]
#apikey = st.text_input('Input API key')

buffer = BytesIO()
c = pycurl.Curl()
custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']

st.title('IDX Stock Prediction')
tickerlist = 'https://api.goapi.id/v1/stock/idx/companies?api_key='+apikey
c.setopt(pycurl.HTTPHEADER, custom_headers)
c.setopt(pycurl.URL, tickerlist)
c.setopt(pycurl.WRITEDATA, buffer)
c.setopt(pycurl.CAINFO, certifi.where())
c.perform()

tickers = buffer.getvalue()
data1 = tickers.decode('iso-8859-1')
dict1 = json.loads(data1)
buffer.seek(0)
buffer.truncate(0)

gainerjson = 'https://api.goapi.id/v1/stock/idx/top_gainer?api_key='+apikey
c.setopt(pycurl.HTTPHEADER, custom_headers)
c.setopt(pycurl.URL, gainerjson)
c.setopt(pycurl.WRITEDATA, buffer)
c.setopt(pycurl.CAINFO, certifi.where())
c.perform()

gainers = buffer.getvalue()
datagainer = gainers.decode('iso-8859-1')
dictgainer = json.loads(data1)
buffer.seek(0)
buffer.truncate(0)

loserjson = 'https://api.goapi.id/v1/stock/idx/top_loser?api_key='+apikey
c.setopt(pycurl.HTTPHEADER, custom_headers)
c.setopt(pycurl.URL, loserjson)
c.setopt(pycurl.WRITEDATA, buffer)
c.setopt(pycurl.CAINFO, certifi.where())
c.perform()

losers = buffer.getvalue()
dataloser = losers.decode('iso-8859-1')
dictloser = json.loads(dataloser)
buffer.seek(0)
buffer.truncate(0)

with st.sidebar:
  st.write("Top 5 Gainers")
  dictgainer = dictgainer["data"]
  dictgainer = dictgainer["results"]
  df_gainer = pd.DataFrame.from_dict(dictgainer)
  df_gainer = df_gainer['ticker']
  gainerlist = df_gainer.values.tolist()
  gainerlist = [re.sub('[^a-zA-Z0-9. ]+', '', str(_)) for _ in gainerlist]
  st.caption('1. '+gainerlist[1])
  st.caption('2. '+gainerlist[2])
  st.caption('3. '+gainerlist[3])
  st.caption('4. '+gainerlist[4])
  st.caption('5. '+gainerlist[5])
  st.caption("Top 5 Losers")
  dictloser = dictloser["data"]
  dictloser = dictloser["results"]
  df_loser = pd.DataFrame.from_dict(dictloser)
  df_loser = df_loser['ticker']
  loserlist = df_loser.values.tolist()
  loserlist = [re.sub('[^a-zA-Z0-9. ]+', '', str(_)) for _ in loserlist]
  st.write('1. '+loserlist[1])
  st.write('2. '+loserlist[2])
  st.write('3. '+loserlist[3])
  st.write('4. '+loserlist[4])
  st.write('5. '+loserlist[5])
  
try:
  dict1 = dict1["data"]
  dict1 = dict1["results"]
  df_ticker = pd.DataFrame.from_dict(dict1)
  df_ticker = df_ticker[['ticker', 'name']]
  selectlist = df_ticker.values.tolist()
  selectlist = [re.sub('[^a-zA-Z0-9. ]+', '', str(_)) for _ in selectlist]
except (NameError, KeyError, ValueError):
  pass

ticker = st.selectbox('Input ticker', selectlist) # type: ignore
ticker = str(ticker)
ticker = ticker[:4]
yr2date = date.today() - relativedelta(years=2)
startdate = st.date_input('Input start date', value=yr2date)
startdate = str(startdate)
today = date.today().strftime("%Y-%m-%d")
url = 'https://api.goapi.id/v1/stock/idx/'+ticker+'/historical?from='+startdate+'&to='+today+'&api_key='+apikey
c.setopt(pycurl.HTTPHEADER, custom_headers)
c.setopt(pycurl.URL, url)
c.setopt(pycurl.WRITEDATA, buffer)
c.setopt(pycurl.CAINFO, certifi.where())
c.perform()
c.close()

body = buffer.getvalue()
data2 = body.decode('iso-8859-1')
dict = json.loads(data2)
try:
  dict = dict["data"]
  dict = dict["results"]
  data = pd.DataFrame.from_dict(dict)
  df_train = data[['date', 'close']]
  df_train = df_train.rename(columns={"date": "ds", "close": "y"})
  df_train['floor'] = 0
except (NameError, KeyError, ValueError):
  pass

period = st.slider("How many days ahead?", min_value=1, max_value=1500, value=250)

try:
  m = Prophet(daily_seasonality=True, yearly_seasonality=True) # type: ignore
  m.fit(df_train) # type: ignore
  future = m.make_future_dataframe(periods=period)
  future['floor'] = 0
  forecast = m.predict(future)
  st.write()
  st.write('Forecast')
  fig1 = plot_plotly(m, forecast)
  fig1.update_yaxes(rangemode = "nonnegative")
  st.plotly_chart(fig1)

  st.write("Prophet forecast components")
  fig2 = m.plot_components(forecast)
  st.write(fig2)
except (NameError, TypeError, KeyError, ValueError):
  pass
