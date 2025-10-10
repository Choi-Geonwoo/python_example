import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import html

def fetch_yahoo_history(tickers):
    results = {}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    for ticker in tickers:
        print(f"\n📈 {ticker} 데이터 수집 중...\n")
        driver.get(f"https://finance.yahoo.com/quote/{ticker}/history")
        time.sleep(5)

        parser = html.fromstring(driver.page_source)
        rows = parser.xpath('//table[contains(@class, "table yf-1jecxey")]/tbody/tr')

        ticker_data = []
        for r in rows[:10]:
            cols = [c.text_content().strip() for c in r.xpath('./td')]
            if len(cols) == 7:
                dt = datetime.strptime(cols[0], "%b %d, %Y")
                dt_kst = dt + timedelta(hours=9)
                cols[0] = dt_kst.strftime("%Y-%m-%d")
                ticker_data.append(cols)

        results[ticker] = ticker_data or []
        print(f"[✔] {ticker} 완료 ({len(ticker_data)}개 행)")

    driver.quit()
    return results
