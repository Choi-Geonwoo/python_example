import os

def save_to_html(result, title_text, folder="./data/tistory/" , images_folder="./img/"):
    headers = ["날짜(KST)", "시가", "고가", "저가", "종가", "조정 종가", "거래량"]

    html_content = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>Yahoo Finance History</title>
        <style>
            body {
                font-family: 'Noto Sans KR', Arial, sans-serif;
                background-color: #f8f9fa;
                padding: 20px;
                color: #333;
            }
            h1, h2 { color: #222; }
            .ticker {
                cursor: pointer;
                padding: 10px 15px;
                margin: 8px 0;
                background-color: #007bff;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            .ticker:hover {
                background-color: #0056b3;
            }
            .table-container {
                display: none;
                margin-top: 10px;
                margin-bottom: 25px;
                padding: 10px;
                background: #ffffff;
                border-radius: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 10px;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #007bff;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
        </style>

        <script>
            function toggleTable(id) {
                var tableDiv = document.getElementById(id);
                if (tableDiv.style.display === "none" || tableDiv.style.display === "") {
                    tableDiv.style.display = "block";
                } else {
                    tableDiv.style.display = "none";
                }
            }
        </script>
    </head>
    <body>
    """

    html_content += f"<h1>{title_text.replace('_', ':').split('$')[0]}</h1>\n"
    # 이미지 포함
    image_path = os.path.join(images_folder, f"stock_chart.jpg")
    if os.path.exists(image_path):
        html_content += f'<img src="{image_path}" alt="차트" style="max-width:100%;"/><br/>\n'

    html_content += f"<h1>📊 Yahoo Finance 과거 데이터</h1>\n"

    for i, (ticker, rows) in enumerate(result.items()):
        div_id = f"table_{i}"
        html_content += f"<div class='ticker' onclick=\"toggleTable('{div_id}')\">▼&emsp;{ticker}</div>\n"
        html_content += f"<div id='{div_id}' class='table-container'>\n"
        html_content += "<table>\n<thead><tr>"
        for h in headers:
            html_content += f"<th>{h}</th>"
        html_content += "</tr></thead>\n<tbody>\n"

        if not rows:
            html_content += "<tr><td colspan='7'>데이터가 없습니다.</td></tr>\n"
        else:
            for row in rows:
                html_content += "<tr>" + "".join([f"<td>{col}</td>" for col in row]) + "</tr>\n"

        html_content += "</tbody></table>\n</div>\n"

    html_content += "</body></html>"

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{title_text}.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ HTML 파일 생성 완료 (아코디언 적용): {file_path}")
    return file_path
