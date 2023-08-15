import certifi
import json
import pandas as pd
import pandas_ta as ta
import plotly.offline as pyo
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
from plotly.subplots import make_subplots
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
    color: #E6EAF1;
    fontSize: 12px;
    fontWeight: 400;
    padding: 0.25rem 0.75rem;
    borderRadius: 0.25rem;
    margin: 0px;
    lineHeight: 1.6;
    width: auto;
    userSelect: none;
    backgroundColor: #262730;
    border: 2px solid rgb(59, 60, 68);">{button_name}</button></a>
    '''

def bollinger_bands(df, n, m):
    TP = (df['high'] + df['low'] + df['close']) / 3
    df = df.merge(TP.rename('TP'), left_index=True, right_index=True)
    df = df.astype({"TP": int})
    B_MA = df['TP'].rolling(n, min_periods=n).mean()
    df = df.merge(B_MA.rename('B_MA'), left_index=True, right_index=True)
    sigma = df['TP'].rolling(n, min_periods=n).std()
    df = df.merge(sigma.rename('sigma'), left_index=True, right_index=True)
    BU = pd.Series((B_MA + m * sigma), name='BU')
    BL = pd.Series((B_MA - m * sigma), name='BL')
    df = df.merge(BU.rename('BU'), left_index=True, right_index=True)
    df = df.merge(BL.rename('BL'), left_index=True, right_index=True)
    
    return df

def get_stochastic_oscillator(df, period=14):
    for i in range(len(df)):
        low = df.iloc[i]['close']
        high = df.iloc[i]['close']
        if i >= period:
            n = 0
            while n < period:
                if df.iloc[i-n]['close'] >= high:
                    high = df.iloc[i-n]['close']
                elif df.iloc[i-n]['close'] < low:
                    low = df.iloc[i-n]['close']
                n += 1
            df.at[i, 'best_low'] = low
            df.at[i, 'best_high'] = high
           
            df['best_low'] = df['best_low'].round(0).astype('Int64')
            df['best_high'] = df['best_high'].round(0).astype('Int64')
            df.at[i, 'fast_k'] = 100*((df.iloc[i]['close']-df.iloc[i]['best_low'])/(df.iloc[i]['best_high']-df.iloc[i]['best_low']))
    df['fast_d'] = df['fast_k'].rolling(3, min_periods=3).mean().round(2)
    df['slow_k'] = df['fast_d']
    df['slow_d'] = df['slow_k'].rolling(3, min_periods=3).mean().round(2)

    return df

buffer = BytesIO()
c = pycurl.Curl()
custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']
today = date.today().strftime("%Y-%m-%d")

st.title('IDX Stock Prediction')
apikey = st.secrets['apikey']
apikey = st.text_input('Input API key')
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
    try:
        dictgainer = dictgainer["data"] # type: ignore
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
    except KeyError:
        pass

  with tab2:
    st.write("Top 10 Losers")
    try:
        dictloser = dictloser["data"] # type: ignore
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
    except KeyError:
        pass

  with tab3:
    st.write("Recent Finance News")
    st.caption("Articles are obtained from the official IDX channel")
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
    try:
      x = 0
      y = 1
      while True:
        st.markdown(get_st_button_a_tag(newslist[x], newslist[y]), unsafe_allow_html=True)
        x = x + 2
        y = y + 2
    except IndexError:
      pass


dict1 = dict1["data"]
dict1 = dict1["results"]
df_ticker = pd.DataFrame.from_dict(dict1)
df_ticker = df_ticker[['ticker', 'name']]
selectlist = df_ticker.values.tolist()
selectlist = [re.sub('[^a-zA-Z0-9. ]+', '', str(_)) for _ in selectlist]


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
buffer.seek(0)
buffer.truncate(0)

dict = dict["data"]
dict = dict["results"]
data = pd.DataFrame.from_dict(dict)
df_train = data[['date', 'close']]
df_train = df_train.rename(columns={"date": "ds", "close": "y"})
df_train['floor'] = 0

period = st.slider("How many days ahead?", min_value=1, max_value=1500, value=250)

tab1, tab2 = st.tabs(["Forecasting", "Indicators"])
with tab1:
    m = Prophet(daily_seasonality=True, yearly_seasonality=True) # type: ignore
    m.fit(df_train) # type: ignore
    future = m.make_future_dataframe(periods=period)
    future['floor'] = 0
    forecast = m.predict(future)
    fig1 = plot_plotly(m, forecast)
    fig1.update_yaxes(rangemode = "nonnegative")
    fig1.update_layout(yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig1)
        
    st.write("Prophet forecast components")
    fig2 = m.plot_components(forecast)
    st.write(fig2)

with tab2:
    databol = data
    try:
        databol = databol.astype({"high": int, "open": int, "low": int, "close": int})
    except ValueError:
        databol = databol.astype({"high": float, "open": float, "low": float, "close": float})
        databol = databol.astype({"high": int, "open": int, "low": int, "close": int})
    df_extra = databol[['date', 'open', 'high', 'low', 'close']]
    df_extra = df_extra.iloc[::-1]
    df_extra = bollinger_bands(df_extra, 20, 2)

    df_open = df_extra['open']
    df_low = df_extra['low']
    df_high = df_extra['high']
    df_close = df_extra['close']
    df_date = df_extra['date']
    df_bu = df_extra['BU']
    df_bl = df_extra['BL']
    df_bma = df_extra['B_MA']

    fig3 = make_subplots(rows=5, cols=1, shared_xaxes=True, row_heights=[1, 0.75, 0.75, 0.75, 0.75], vertical_spacing=0.05,
                         subplot_titles=("Bollinger Bands", "Stochastic Oscillator", "Relative Strength Index (RSI)", "StochRSI", "Moving Average Convergence/Divergence (MACD)"))
    fig3.update_layout(showlegend=False, height=1200)
    
    trace1 = go.Scatter(x=df_date, y=df_close, name='Closing Price', line_color='#A5D6FF')
    trace2 = go.Scatter(x=df_date, y=df_bu, # type: ignore
                    mode='lines',
                    name='Upper Bound',
                    line_shape='spline',
                    line_color='#0072B2',
                    line_width=1
        )
    trace3 = go.Scatter(x=df_date, y=df_bl, # type: ignore
                    mode='lines',
                    name='Lower Bound',
                    line_shape='spline',
                    line_color='#0072B2',
                    line_width=1
        )
    trace4 = go.Scatter(x=df_date, y=df_bma, # type: ignore
                    mode='lines',
                    name='Moving Average',
                    line_color='#0072B2',
                    line_width=1
        )

    df_extra.ta.stoch(high='high', low='low', k=14, d=3, append=True)
    df_k = df_extra['STOCHk_14_3_3']
    df_d = df_extra['STOCHd_14_3_3']

    trace5 = go.Scatter(x=df_date, y=df_k, # type: ignore
                    mode='lines',
                    name='%K',
                    line_width=1
        )
    trace6 = go.Scatter(x=df_date, y=df_d, # type: ignore
                    mode='lines',
                    name='%D',
                    line_width=1
        )
    
    df_extra.ta.rsi(close='close', append=True)
    df_R = df_extra['RSI_14']
    
    trace7 = go.Scatter(x=df_date, y=df_R, # type: ignore
                    mode='lines',
                    name='RSI',
                    line_width=1
        )
    
    df_extra.ta.stochrsi(close='close', append=True)
    df_SRk = df_extra['STOCHRSIk_14_14_3_3']
    df_SRd = df_extra['STOCHRSId_14_14_3_3']
    
    trace8 = go.Scatter(x=df_date, y=df_SRk, # type: ignore
                    mode='lines',
                    name='StochRSIk',
                    line_width=1
        )
    trace9 = go.Scatter(x=df_date, y=df_SRd, # type: ignore
                    mode='lines',
                    name='StochRSId',
                    line_width=1
        )
    
    df_extra.ta.macd(close='close', append=True)
    df_M = df_extra['MACD_12_26_9']
    df_Mh = df_extra['MACDh_12_26_9']
    df_Ms = df_extra['MACDs_12_26_9']
    
    trace10 = go.Scatter(x=df_date, y=df_M, # type: ignore
                    mode='lines',
                    name='MACD',
                    line_width=1
        )
    trace11 = go.Scatter(x=df_date, y=df_Mh, # type: ignore
                    mode='lines',
                    name='MACDh',
                    line_width=1
        )
    trace12 = go.Scatter(x=df_date, y=df_Ms, # type: ignore
                    mode='lines',
                    name='MACDs',
                    line_width=1
        )
    
    fig3.add_trace(trace1,1,1)
    fig3.add_trace(trace2,1,1)
    fig3.add_trace(trace3,1,1)
    fig3.add_trace(trace4,1,1)
    fig3.add_trace(trace5,2,1)
    fig3.add_trace(trace6,2,1)
    fig3.add_trace(trace7,3,1)
    fig3.add_trace(trace8,4,1)
    fig3.add_trace(trace9,4,1)
    fig3.add_trace(trace10,5,1)
    fig3.add_trace(trace11,5,1)
    fig3.add_trace(trace12,5,1)
    fig3.add_shape(type="rect",
        xref="x2", yref="y2",
        x0=df_date.iloc[0], y0=80,
        x1=today, y1=100,
        fillcolor="rgba(165, 214, 255, 0.1)",
        line_width=0,
        line_color="rgba(165, 214, 255, 0.1)"
    )
    fig3.add_shape(type="rect",
        xref="x2", yref="y2",
        x0=df_date.iloc[0], y0=0,
        x1=today, y1=20,
        fillcolor="rgba(165, 214, 255, 0.1)",
        line_width=0,
        line_color="rgba(165, 214, 255, 0.1)"
    )
    fig3.add_shape(type="rect",
        xref="x3", yref="y3",
        x0=df_date.iloc[0], y0=70,
        x1=today, y1=100,
        fillcolor="rgba(255, 135, 0, 0.1)",
        line_width=0,
        line_color="rgba(255, 135, 0, 0.1)"
    )
    fig3.add_shape(type="rect",
        xref="x3", yref="y3",
        x0=df_date.iloc[0], y0=0,
        x1=today, y1=30,
        fillcolor="rgba(255, 135, 0, 0.1)",
        line_width=0,
        line_color="rgba(255, 135, 0, 0.1)"
    )
    fig3.add_shape(type="rect",
        xref="x4", yref="y4",
        x0=df_date.iloc[0], y0=80,
        x1=today, y1=100,
        fillcolor="rgba(255, 209, 106, 0.1)",
        line_width=0,
        line_color="rgba(255, 209, 106, 0.1)"
    )
    fig3.add_shape(type="rect",
        xref="x4", yref="y4",
        x0=df_date.iloc[0], y0=0,
        x1=today, y1=20,
        fillcolor="rgba(255, 209, 106, 0.1)",
        line_width=0,
        line_color="rgba(255, 209, 106, 0.1)"
    )
    
    st.plotly_chart(fig3)