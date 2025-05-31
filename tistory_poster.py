import traceback

import pyperclip
from flask import send_file
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


def post_to_tistory(username, password, blog_name, title_text, content_text):
    # 드라이버 실행
    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")         # <<< 이거도 추가
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service("/usr/local/bin/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 1. 티스토리 로그인 페이지 접속
        driver.get("https://www.tistory.com/auth/login")
        time.sleep(2)

        # 2. "카카오계정으로 로그인" 버튼 클릭
        kakao_login_btn = driver.find_element(By.CLASS_NAME, "link_kakao_id")
        kakao_login_btn.click()
        time.sleep(3)

        # 3. 카카오 로그인 창에서 ID, 비밀번호 입력
        email_input = driver.find_element(By.NAME, "loginId")
        password_input = driver.find_element(By.NAME, "password")

        # 👉 입력값 초기화
        email_input.send_keys(Keys.CONTROL + "a")
        email_input.send_keys(Keys.DELETE)

        password_input.send_keys(Keys.CONTROL + "a")
        password_input.send_keys(Keys.DELETE)

        # 👉 값 입력
        email_input.send_keys(username)
        password_input.send_keys(password)

        # 4. 로그인 버튼 클릭
        login_button = driver.find_element(By.CLASS_NAME, "submit")
        login_button.click()
        time.sleep(5)

        # 4. 글관리 페이지로 이동
        post_list_url = f"https://{blog_name}.tistory.com/manage/post"
        driver.get(post_list_url)
        time.sleep(2)

        driver.get("https://tistory.com/editor")  # 여긴 네가 열려는 주소
        WebDriverWait(driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        driver.save_screenshot('screenshot.png')

        # # 6. 글쓰기 버튼 클릭
        # write_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, "link_write"))
        # )
        # write_button.click()
        # time.sleep(2)

        # 제목 입력 후, 첫 alert 처리 (임시저장 이어쓰기 여부)
        accept_if_alert_present("제목",driver, action="dismiss")  # 취소(dismiss)할 경우
        time.sleep(2)

        # 7. 제목 입력
        title_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "post-title-inp"))
        )
        title_input.clear()
        title_input.send_keys(title_text)

        # 8. HTML 모드로 전환
        mode_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "editor-mode-layer-btn-open"))
        )
        mode_button.click()
        time.sleep(1)

        html_mode_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "editor-mode-html"))
        )
        html_mode_option.click()

        # 9. 알림 팝업(HTML모드 경고) 확인
        accept_if_alert_present("내용", driver, action="accept")  # 확인(accept)할 경우
        time.sleep(1)

        # 10. CodeMirror HTML 입력창 클릭 후 입력
        fixed_text = content_text

        code_area = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "CodeMirror"))
        )
        code_area.click()
        time.sleep(1)

        # Headless 체크
        if driver.execute_script("return navigator.webdriver"):
            # 헤드리스 모드일 때: send_keys 사용
            actions = ActionChains(driver)
            actions.send_keys(fixed_text).perform()
        else:
            # 일반 모드일 때: 원래 코드 사용
            driver.execute_script("""
                const editor = document.querySelector('.CodeMirror').CodeMirror;
                editor.setValue(arguments[0]);
                editor.refresh();
                editor.focus();
                editor.setCursor(editor.lineCount(), 0);
            """, fixed_text)

        time.sleep(3)

        # 11. 임시저장 버튼 클릭
        save_draft_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-draft .action"))
        )
        save_draft_button.click()
        time.sleep(3)

        return "Post Successful"

    except Exception as e:
        print("❌ 오류 발생:", e)
        traceback.print_exc()  # 전체 에러 스택 출력
        return str(e)

    finally:
        driver.quit()


def limit_indentation_for_send(text: str, max_indent=4):
    lines = text.splitlines()
    fixed = []
    for line in lines:
        spaces = len(line) - len(line.lstrip())
        allowed = min(spaces, max_indent)
        fixed.append(' ' * allowed + line.lstrip())
    return "\n".join(fixed)


# 🔐 alert 처리 함수
def accept_if_alert_present(type, driver, action="accept", timeout=5):
    """
    Tistory alert가 뜨면 '확인' 또는 '취소' 중 하나를 선택하여 처리함.
    :param driver: Selenium WebDriver
    :param action: 'accept' 또는 'dismiss'
    :param timeout: 대기 시간
    """
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert = driver.switch_to.alert

        if action == "accept":
            alert.accept()
        elif action == "dismiss":
            alert.dismiss()
        else:
            print("⚠️ 알 수 없는 action, 기본 확인 실행")
            alert.accept()

        WebDriverWait(driver, timeout).until_not(EC.alert_is_present())
        time.sleep(1)

    except Exception as e:
        print("ℹ️"+ type+ "Alert 없음 또는 이미 닫힘:", e)