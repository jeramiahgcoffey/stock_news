import requests
import datetime as dt
from twilio.rest import Client


TWILIO_ACCT_SID = "AC4442dbd8d3d3cc5bfb535ac0fda3d4fa"
TWILIO_AUTH_TOKEN = "c4dd864ab32c513f2c29a12a1dc215d5"

STOCK = "TSLA"
COMPANY_NAME = "Tesla"
STOCK_API_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = "LKTCM6MY1LBLFYBS"
STOCK_API_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY,
}

NEWS_API_ENDPOINT = "https://newsapi.org/v2/top-headlines"
NEWS_API_KEY = "a8d159444eb74bc6950745a9accb4af0"
NEWS_API_PARAMS = {
    "q": COMPANY_NAME,
    "apiKey": NEWS_API_KEY,
    "pageSize": 3
}


today = dt.datetime.now().date()
yesterday = str(today - dt.timedelta(days=1))
day_before_yesterday = str(today - dt.timedelta(days=2))


def get_news():
    with requests.get(NEWS_API_ENDPOINT, NEWS_API_PARAMS) as news_response:
        headlines = news_response.json()["articles"]
        company_news = []
        for article in headlines:
            headline = {
                "title": article["title"],
                "description": article["description"],
                "url": article["url"]
            }
            company_news.append(headline)
        return company_news


def notify(company_news):
    global percent_of_change
    if percent_of_change < 0:
        percent_of_change = abs(percent_of_change)
        percent_of_change = "🔻" + str(percent_of_change)
    else:
        percent_of_change = "🔺" + str(percent_of_change)
    notification = ""
    for headline in company_news:
        notification += f"{COMPANY_NAME}: {percent_of_change}%\n" \
                       f"Headline: {headline['title']}\n" \
                       f"Brief: {headline['description']}\n" \
                       f"URL: {headline['url']}\n\n"

    client = Client(TWILIO_ACCT_SID, TWILIO_AUTH_TOKEN)

    message = client.messages \
                    .create(
                         body=notification,
                         from_='+17029860727',
                         to='+15129688615'
                     )

    print(message.status)


with requests.get(STOCK_API_ENDPOINT, params=STOCK_API_PARAMS) as stock_response:
    daily_stock_data = stock_response.json()["Time Series (Daily)"]
    yesterday_close = float(daily_stock_data[yesterday]["4. close"])
    day_before_yesterday_close = float(daily_stock_data[day_before_yesterday]["4. close"])
    percent_of_change = round((yesterday_close - day_before_yesterday_close) / yesterday_close * 100, 2)
    print(percent_of_change)
    if percent_of_change > 5 or percent_of_change < -5:
        notify(get_news())
