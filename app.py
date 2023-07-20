import pycurl
import certifi
import json
from io import BytesIO
import pandas as pd
import streamlit as st
from datetime import date
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

buffer = BytesIO()
c = pycurl.Curl()
custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']

st.title('IDX stock list')
ticker = st.text_input('Input ticker')
ticker = str(ticker)
startdate = st.date_input('Input start date')
startdate = str(startdate)
apikey = st.secrets["apikey"]
#apikey = st.text_input('Input API key')
today = date.today().strftime("%Y-%m-%d")
url = 'https://api.goapi.id/v1/stock/idx/'+ticker+'/historical?from='+startdate+'&to='+today+'&api_key='+apikey
c.setopt(pycurl.HTTPHEADER, custom_headers)
c.setopt(pycurl.URL, url)
c.setopt(pycurl.WRITEDATA, buffer)
c.setopt(pycurl.CAINFO, certifi.where())
c.perform()
c.close()

body = buffer.getvalue()
print(body.decode('iso-8859-1'))
data1 = body.decode('iso-8859-1')
dict = json.loads(data1)
try:
  dict = dict["data"]
  dict = dict["results"]
  data = pd.DataFrame.from_dict(dict)
  df_train = data[['date', 'close']]
  df_train = df_train.rename(columns={"date": "ds", "close": "y"})
  df_train['floor'] = 0
except KeyError:
  pass

period = st.text_input("How many days ahead?")
try:
  period = int(period)
except ValueError:
  pass
m = Prophet(daily_seasonality=True, yearly_seasonality=True) # type: ignore
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
future['floor'] = 0
forecast = m.predict(future)

st.write('Forecast')
fig1 = plot_plotly(m, forecast)
fig1.update_yaxes(rangemode = "nonnegative")
st.plotly_chart(fig1)

st.write("Prophet forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)
