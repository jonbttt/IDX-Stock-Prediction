import certifi
import json
import pandas as pd
import pycurl
import re
import requests
import streamlit as st
from streamlit.components.v1 import html
from bs4 import BeautifulSoup
from datetime import date
from dateutil.relativedelta import relativedelta
from io import BytesIO
from plotly import graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly

def get_st_button_a_tag(url_link, button_name):
    """
    generate html a tag
    :param url_link:
    :param button_name:
    :return:
    """
    return f'''
    <a href={url_link}><button style="
    fontWeight: 400;
    padding: 0.25rem 0.75rem;
    borderRadius: 0.25rem;
    margin: 0px;
    lineHeight: 1.6;
    width: auto;
    userSelect: none;
    backgroundColor: #FFFFFF;
    border: 1px solid rgba(49, 51, 63, 0.2);">{button_name}</button></a>
    '''

apikey = st.secrets["apikey"]
#apikey = st.text_input('Input API key')

buffer = BytesIO()
c = pycurl.Curl()
custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']
today = date.today().strftime("%Y-%m-%d")

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
dictgainer = json.loads(datagainer)
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
  tab1, tab2, tab3 = st.tabs(["Gainers", "Losers", "News"])
  with tab1:
    st.write("Top 10 Gainers")
    dictgainer = dictgainer["data"]
    dictgainer = dictgainer["results"]
    df_gainer = pd.DataFrame.from_dict(dictgainer)
    df_gainer = df_gainer['ticker']
    gainerlist = df_gainer.values.tolist()
    gainerlist = [re.sub('[^a-zA-Z0-9. ]+', '', str(_)) for _ in gainerlist]
    st.caption('1. '+gainerlist[0])
    st.caption('2. '+gainerlist[1])
    st.caption('3. '+gainerlist[2])
    st.caption('4. '+gainerlist[3])
    st.caption('5. '+gainerlist[4])
    st.caption('6. '+gainerlist[5])
    st.caption('7. '+gainerlist[6])
    st.caption('8. '+gainerlist[7])
    st.caption('9. '+gainerlist[8])
    st.caption('10. '+gainerlist[9])

  with tab2:
    st.write("Top 10 Losers")
    dictloser = dictloser["data"]
    dictloser = dictloser["results"]
    df_loser = pd.DataFrame.from_dict(dictloser)
    df_loser = df_loser['ticker']
    loserlist = df_loser.values.tolist()
    loserlist = [re.sub('[^a-zA-Z0-9. ]+', '', str(_)) for _ in loserlist]
    st.caption('1. '+loserlist[0])
    st.caption('2. '+loserlist[1])
    st.caption('3. '+loserlist[2])
    st.caption('4. '+loserlist[3])
    st.caption('5. '+loserlist[4])
    st.caption('6. '+loserlist[5])
    st.caption('7. '+loserlist[6])
    st.caption('8. '+loserlist[7])
    st.caption('9. '+loserlist[8])
    st.caption('10. '+loserlist[9])

  with tab3:
    st.write("Recent Finance News")
    st.caption("Articles are from the official IDX channel")
    string1 = ""
    newsurl = "https://www.idxchannel.com/indeks?date="+today+"&idkanal=1"
    print(newsurl)
    reqs = requests.get(newsurl)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    divs = soup.find_all("div", {"class": "title-capt"})

    newslist = []
    for x in divs:
        newslist.append(str(x))
    newslist = [item.replace('<div class="title-capt">\n<h2 class="list-berita-baru">', '') for item in newslist]
    newslist = [item.replace('</a></h2>\n</div>', '') for item in newslist]
    newslist = [item.replace('<a href="', '') for item in newslist]
    newslist = [item.replace('">', '||') for item in newslist]
    separator = '||'
    string1 = separator.join(newslist)
    newslist = string1.split('||')
    st.markdown(get_st_button_a_tag(newslist[0], newslist[1]), unsafe_allow_html=True)
    st.button(newslist[3], on_click=open_page(newslist[2]), key="2")
    st.button(newslist[5], on_click=open_page(newslist[4]), key="3")
    st.button(newslist[7], on_click=open_page(newslist[6]), key="4")
    st.button(newslist[9], on_click=open_page(newslist[8]), key="5")
    st.button(newslist[11], on_click=open_page(newslist[10]), key="6")
    st.button(newslist[13], on_click=open_page(newslist[12]), key="7")
    st.button(newslist[15], on_click=open_page(newslist[14]), key="8")
    st.button(newslist[17], on_click=open_page(newslist[16]), key="9")

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
