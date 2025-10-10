import os

# ✅ 폴더 내 HTML 파일 불러오기
def get_html_files(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"[❗] 폴더가 존재하지 않아 새로 생성함: {folder_path}")
        return []
    return [f for f in os.listdir(folder_path) if f.endswith(".html")]

# ✅ 파일 내용 읽기 (자동 인코딩 감지)
def read_html_file(file_path):
    for encoding in ["utf-8", "cp949"]:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"파일 인코딩을 확인하세요: {file_path}")

# ✅ 파일명에서 제목과 태그 추출
def parse_title_and_tags(file_name):
    parts = file_name.split("$")
    title = parts[0]
    tags = [p.replace(".html", "").strip() for p in parts[1:] if p.strip()]
    return title, tags

# ✅ 포스팅 완료 후 파일 삭제
def delete_all_html(folder_path):
    if os.path.exists(folder_path):
        for file in os.scandir(folder_path):
            os.remove(file.path)
        return "파일 삭제 완료"
    return "파일 없음으로 인한 종료"
