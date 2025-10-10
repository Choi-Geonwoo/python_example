from fetch_yahoo_history.config import get_config
from fetch_yahoo_history.yahoo_scraper import fetch_yahoo_history
from fetch_yahoo_history.html_builder import save_to_html

def run_html_generation():
    tickers, title_text, start_date, end_date = get_config()
    result = fetch_yahoo_history(tickers)
    file_path = save_to_html(result, title_text)
    return file_path

if __name__ == "__main__":
    run_html_generation()
