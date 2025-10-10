from datetime import datetime, timedelta

def get_config():
    today = datetime.today()

    # 이전 주 월요일 ~ 어제
    start_date = today - timedelta(days=today.weekday() + 10)
    end_date = today - timedelta(days=1)
    # "AAPL", "QQQ", "O", "SPYI", "SCHD"
    tickers = ["JEPQ"]

    title_text = (
        f"기준일자_{start_date.year}년{start_date.month:02d}월{start_date.day:02d}일-"
        f"{end_date.year}년{end_date.month:02d}월{end_date.day:02d}일"
    )

    for t in tickers:
        title_text += f"${t}"

    return tickers, title_text, start_date, end_date
