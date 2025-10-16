import os

def save_to_html(result, title_text, folder="./data/tistory/", images_folder="./img/"):
    headers = ["순번","날짜(KST)", "시가", "고가", "저가", "종가", "조정 종가", "거래량"]

    # 예시 매핑 (원하는 대로 수정 가능)
    ticker_map = {
        "QQQ": "QQQ",
        "JEPQ": "JEPQ",
        "SPYI": "SPYI",
        "BITO": "BITO",
        "SCHD": "SCHD",
        "TLTW": "TLTW",
        "O"   : "O",
        "BAC" : "BAC",
        "AAPL": "AAPL",
        "WM"  : "WM",
        "KO"  : "KO",
        "ACE 미국 S&P500": "360200.KS",
        "ACE 미국 나스닥100": "367760.KS",
        "NAVER": "035420.KS",
        "KODEX 200": "161510.KS"
    }

    html_content = """
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <title>Yahoo Finance History</title>
        <style>
            body {
                font-family: 'Noto Sans KR', 'Segoe UI', sans-serif;
                background-color: #eef2f7;
                padding: 40px;
                color: #333;
                line-height: 1.6;
            }

            h1 {
                color: #222;
                text-align: center;
                margin-bottom: 40px;
                font-size: 28px;
            }

            .ticker {
                cursor: pointer;
                padding: 14px 18px;
                margin: 12px 0;
                background: linear-gradient(135deg, #007bff, #0056d1);
                color: white;
                border-radius: 10px;
                font-weight: 600;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .ticker:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }

            .table-container {
                display: none;
                margin-top: 10px;
                margin-bottom: 30px;
                padding: 20px;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.08);
                animation: fadeIn 0.4s ease-in-out;
                overflow-x: auto;
            }

            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 10px;
                font-size: 14px;
                min-width: 700px;
            }

            th, td {
                border: 1px solid #ddd;
                padding: 10px 8px;
                text-align: center;
            }

            th {
                position: sticky;
                top: 0;
                background-color: #007bff;
                color: #fff;
                font-weight: 600;
            }

            tr:nth-child(even) {
                background-color: #f9fafc;
            }

            tr:hover {
                background-color: #e8f0ff;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-5px); }
                to { opacity: 1; transform: translateY(0); }
            }

            footer {
                text-align: center;
                font-size: 13px;
                color: #666;
                margin-top: 50px;
            }

            @media (max-width: 768px) {
                body { padding: 20px; }
                h1 { font-size: 22px; }
                .ticker { font-size: 15px; }
                table { font-size: 12px; }
            }
        </style>

        <script>
            // Python 딕셔너리를 JS 객체로 변환
            const tickersValue = {
    """

    # --- Python ticker_map을 JS 객체로 변환 ---
    for k, v in ticker_map.items():
        html_content += f'                "{k}": "{v}",\n'

    html_content += """
            };

            function toggleTable(id, tickerName) {
                const tableDiv = document.getElementById(id);
                const isVisible = tableDiv.style.display === "block";
                document.querySelectorAll('.table-container').forEach(div => div.style.display = "none");
                if (!isVisible) {
                    tableDiv.style.display = "block";
                    tableDiv.scrollIntoView({ behavior: "smooth", block: "start" });
                }

                const realTicker = tickersValue[tickerName] || tickerName;
                console.log(`선택된 티커: ${tickerName} → 실제 코드: ${realTicker}`);
            }
        </script>
    </head>
    <body>
    """

    html_content += f"<h1>📊 {title_text.replace('_', ':').split('$')[0]} - Yahoo Finance 과거 데이터</h1>\n"

    # --- HTML 표 생성 ---
    for i, (ticker, rows) in enumerate(result.items()):
        div_id = f"table_{i}"
        display_name = next((k for k, v in ticker_map.items() if v == ticker), ticker)
        html_content += f"<div class='ticker' onclick=\"toggleTable('{div_id}', '{display_name}')\">▶ {display_name}</div>\n"
        html_content += f"<div id='{div_id}' class='table-container'>\n"
        html_content += "<table>\n<thead><tr>"
        for h in headers:
            html_content += f"<th>{h}</th>"
        html_content += "</tr></thead>\n<tbody>\n"

        if not rows:
            html_content += "<tr><td colspan='8'>데이터가 없습니다.</td></tr>\n"
        else:
            for row in rows:
                html_content += "<tr>" + "".join([f"<td>{col}</td>" for col in row]) + "</tr>\n"

        html_content += "</tbody></table>\n</div>\n"

    html_content += """
        <footer>
            © 2025 Yahoo Finance Data Viewer | 출처 : finance.yahoo.com ✨
        </footer>
    </body>
    </html>
    """
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{title_text}.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ HTML 파일 생성 완료 (매핑 기능 포함): {file_path}")
    return file_path
