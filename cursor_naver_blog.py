from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import platform
import json
from datetime import datetime, timedelta
import time

# ----------------------------
# 1) .env 로드
# ----------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), "playwright_naver.env")
load_dotenv(dotenv_path)

NAVER_ID = os.getenv("NAVER_ID")
NAVER_PW = os.getenv("NAVER_PW")
BLOG_URL = os.getenv("BLOG_URL")  # 글쓰기 URL 권장: https://blog.naver.com/PostWriteForm.naver?blogId=xxx 또는 https://blog.editor.naver.com/editor

STATE_FILE = "naver_state.json"   # 세션 저장
USER_DATA_DIR = os.path.abspath(".pw_user")  # 영속 프로필

# ----------------------------
# 2) 날짜(이전 주 월~금)
# ----------------------------
today = datetime.today()
start_date = today - timedelta(days=today.weekday() + 7)
end_date = start_date + timedelta(days=4)

title_text = f"{start_date.year}년{start_date.month:02d}월{start_date.day:02d}일 ~ {end_date.year}년{end_date.month:02d}월{end_date.day:02d}일 매수 일지"

# ----------------------------
# 3) 이미지 경로
# ----------------------------
cover_img = "C:/images/cover.png"
pension_img = "C:/images/pension.png"
buy_img = "C:/images/buy.png"
sell_img = "C:/images/sell.png"
retirement_img = "C:/images/retirement.png"

# ----------------------------
# 4) 본문 텍스트
# ----------------------------
body_text = f"""
{start_date.year}년{start_date.month:02d}월{start_date.day:02d}일 ~ {end_date.year}년{end_date.month:02d}월{end_date.day:02d}일 매수 일지 입니다.

1. 연금 저축

2. 일반 계좌
- 매수
- 매도

3. 퇴직 연금
"""

# ----------------------------
# 유틸
# ----------------------------
def ensure_files(paths):
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(f"이미지 파일 없음: {missing}")

def accel_key():
    return "Meta" if platform.system() == "Darwin" else "Control"

def find_frame_with_selector(frames, selector):
    for frame in frames:
        try:
            if frame.locator(selector).count() > 0:
                return frame
        except:
            pass
        if frame.child_frames:
            f = find_frame_with_selector(frame.child_frames, selector)
            if f:
                return f
    return None

def type_stable_contenteditable(target, text, verify_contains=True, retries=2):
    for _ in range(retries + 1):
        try:
            target.scroll_into_view_if_needed()
        except:
            pass
        target.click()
        try:
            target.press(f"{accel_key()}+A")
            target.press("Delete")
        except:
            pass
        target.type(text, delay=20)

        ok = False
        try:
            content = target.inner_text(timeout=3000)
            ok = (text.strip() in content) if verify_contains else (content.strip() == text.strip())
        except:
            ok = False
        if ok:
            return True

        try:
            target.evaluate("""(el, value) => {
  el.focus();
  try { document.execCommand('selectAll', false, null); } catch(e) {}
  try { document.execCommand('insertText', false, value); } catch(e) {
    el.textContent = value;
    const evt = new InputEvent('input', {bubbles:true});
    el.dispatchEvent(evt);
  }
}""", text)
            content = target.inner_text(timeout=3000)
            if text.strip() in content:
                return True
        except:
            pass
    return False

def get_title_locator(page):
    # 루트 우선
    sel_input = "input[placeholder*='제목'], textarea[placeholder*='제목']"
    sel_ce = "div.se-documentTitle .se-component-content p span, div.se-documentTitle .se-component-content p, [data-placeholder*='제목'], [contenteditable='true'][data-placeholder*='제목']"
    if page.locator(sel_input).count() > 0:
        return page.locator(sel_input).first
    if page.locator(sel_ce).count() > 0:
        return page.locator(sel_ce).first
    # 프레임
    for f in page.frames:
        try:
            if f.locator(sel_input).count() > 0:
                return f.locator(sel_input).first
            if f.locator(sel_ce).count() > 0:
                return f.locator(sel_ce).first
        except:
            pass
    return None

def get_body_locator(page):
    # 루트
    if page.locator("div.se-text div.se-component-content p").count() > 0:
        return page.locator("div.se-text div.se-component-content p").first
    if page.locator("[contenteditable='true']").count() > 0:
        return page.locator("[contenteditable='true']").first
    # 프레임
    for f in page.frames:
        try:
            if f.locator("div.se-text div.se-component-content p").count() > 0:
                return f.locator("div.se-text div.se-component-content p").first
            if f.locator("[contenteditable='true']").count() > 0:
                return f.locator("[contenteditable='true']").first
        except:
            pass
    return None

def fill_title(page, title_text):
    el = get_title_locator(page)
    if not el:
        return False, "제목 요소 없음"
    try:
        if el.evaluate("(el)=>el.tagName==='INPUT'||el.tagName==='TEXTAREA'"):
            el.fill("")
            el.type(title_text, delay=10)
            val = el.input_value(timeout=2000)
            return (title_text.strip() == val.strip()), "ok" if title_text.strip() == val.strip() else "검증 실패"
    except:
        pass
    ok = type_stable_contenteditable(el, title_text)
    return ok, "ok" if ok else "입력 실패"

def fill_body(page, body_text):
    el = get_body_locator(page)
    if not el:
        return False, "본문 요소 없음"
    ok = type_stable_contenteditable(el, body_text)
    return ok, "ok" if ok else "입력 실패"

def upload_image(page, image_path, timeout=30000):
    if not os.path.exists(image_path):
        raise FileNotFoundError(image_path)

    trigger_candidates = [
        "button.se-insert-menu-button-image",
        "button:has-text('이미지')",
        "button:has-text('사진')",
        "[aria-label='사진'], [aria-label='이미지']",
    ]
    contexts = [page] + list(page.frames)

    # 1) FileChooser
    for ctx in contexts:
        try:
            for sel in trigger_candidates:
                if ctx.locator(sel).count() > 0:
                    with ctx.expect_file_chooser(timeout=2000) as fc_info:
                        ctx.click(sel)
                    fc = fc_info.value
                    fc.set_files(image_path)
                    ctx.wait_for_selector("img[src*='blob'], figure img, img.se-image-resource", timeout=timeout)
                    return True
        except:
            continue

    # 2) input[type=file]
    for ctx in contexts:
        try:
            if ctx.locator("input[type='file']").count() > 0:
                ctx.locator("input[type='file']").set_input_files(image_path)
                ctx.wait_for_selector("img[src*='blob'], figure img, img.se-image-resource", timeout=timeout)
                return True
        except:
            continue
    return False

def click_publish(page):
    sels = [
        "button:has-text('발행')",
        "button:has-text('등록')",
        "[role='button']:has-text('발행')",
        "[role='button']:has-text('등록')",
    ]
    # 루트
    for s in sels:
        if page.locator(s).count() > 0:
            page.click(s)
            return True
    # 프레임
    for f in page.frames:
        for s in sels:
            try:
                if f.locator(s).count() > 0:
                    f.click(s)
                    return True
            except:
                pass
    return False

def login_context(p, headless=False):
    # 기존 프로필/세션 재사용
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=headless,
        locale="ko-KR"
    )
    page = context.new_page()

    # 이미 로그인돼 있으면 바로 사용
    page.goto("https://www.naver.com", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    # 간단히 상단 메뉴로 로그인 여부 추정(실패해도 이어감)
    # 필요 시 강제 로그인 시도
    if NAVER_ID and NAVER_PW:
        page.goto("https://nid.naver.com/nidlogin.login", wait_until="load")
        try:
            if page.locator("input#id").count() > 0 and page.locator("input#pw").count() > 0:
                page.fill("input#id", NAVER_ID)
                page.fill("input#pw", NAVER_PW)
                if page.locator("button.btn_login").count() > 0:
                    page.click("button.btn_login")
                else:
                    page.press("input#pw", "Enter")
                time.sleep(1.0)
                # 캡챠/추가 인증 시 수동 처리 대기
                if page.locator("text=자동입력").count() > 0 or page.locator("text=캡차").count() > 0:
                    print("캡챠/추가 인증 발견. 브라우저에서 완료 후 Enter.")
                    input()
        except:
            pass

    try:
        context.storage_state(path=STATE_FILE)
    except:
        pass
    return context, page

# ----------------------------
# 메인
# ----------------------------
if __name__ == "__main__":
    ensure_files([cover_img, pension_img, buy_img, sell_img, retirement_img])
    if not BLOG_URL:
        raise RuntimeError("BLOG_URL(.env) 설정 필요")

    with sync_playwright() as p:
        context, page = login_context(p, headless=False)
        print("✅ 로그인/세션 준비 완료")

        # 글쓰기 페이지 이동
        page.goto(BLOG_URL)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("networkidle")

        # 에디터 로딩 힌트
        _ = page.locator("iframe")
        # 1) 제목
        ok, msg = fill_title(page, title_text)
        print("✅ 제목 작성 완료" if ok else f"❌ 제목 실패: {msg}")

        # 2) 본문
        ok, msg = fill_body(page, body_text)
        print("✅ 본문 작성 완료" if ok else f"❌ 본문 실패: {msg}")

        # 3) 이미지 업로드(순차)
        for img in [cover_img, pension_img, buy_img, sell_img, retirement_img]:
            ok = upload_image(page, img)
            print(f"✅ 이미지 업로드: {os.path.basename(img)}" if ok else f"❌ 이미지 업로드 실패: {os.path.basename(img)}")

        # 4) 발행
        if click_publish(page):
            # 확인 모달 처리(있다면)
            for sel in ["button:has-text('확인')", "button:has-text('예')", "button:has-text('OK')"]:
                if page.locator(sel).count() > 0:
                    page.click(sel)
                    break
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except:
                pass
            print("✅ 발행 단계 진행됨")
        else:
            print("⚠️ 발행 버튼을 찾지 못했습니다. 브라우저에서 수동 발행해 주세요.")

        input("Enter를 누르면 브라우저를 닫습니다...")
        context.close()
