import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        # time.sleep(5)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "table yf-1jecxey")]/tbody/tr'))
            )
        except:
            print(f"[❌] {ticker} 데이터 로드 실패 — 재시도 중...")
            time.sleep(3)
            driver.refresh()
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "table yf-1jecxey")]/tbody/tr'))
            )


        parser = html.fromstring(driver.page_source)
        rows = parser.xpath('//table[contains(@class, "table yf-1jecxey")]/tbody/tr')

        ticker_data = []
        for r in rows[:10]:
            cols = [c.text_content().strip() for c in r.xpath('./td')]
            cols.insert(0, str(len(ticker_data) + 1))  # 순번 추가
            if len(cols) == 8:
                dt = datetime.strptime(cols[1], "%b %d, %Y")
                dt_kst = dt + timedelta(hours=9)
                cols[1] = dt_kst.strftime("%Y-%m-%d")
                ticker_data.append(cols)

        results[ticker] = ticker_data or []
        print(f"[✔] {ticker} 완료 ({len(ticker_data)}개 행)")

    driver.quit()
    return results
