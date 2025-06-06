import html
import logging
import os
import re

from flask_cors import CORS
from flask import Flask, jsonify, request, send_file
from tistory_poster import post_to_tistory
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB까지 허용
CORS(app)  # 🔥 모든 도메인 허용

@app.route("/", methods=["POST"])
def post_tistory():
    # 콘솔에 출력할 기본 설정
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    raw_body = request.get_data(as_text=True)
    logger.info(f"🛬 Raw Body: {raw_body}")

    # 컨트롤 문자 제거 (필요 시)
    raw_body_clean = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', raw_body)

    # JSON 파싱
    try:
        data = json.loads(raw_body_clean)
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "JSON 포맷 오류입니다."}), 400

    #data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"status":"error","message":"title과 content를 모두 보내주세요."}), 400

    try:
        title = html.unescape(data["title"].lstrip("\ufeff"))
        content = html.unescape(data["content"].lstrip("\ufeff"))

        res = post_to_tistory(
            username=os.getenv("TISTORY_USERNAME"),
            password=os.getenv("TISTORY_PASSWORD"),
            blog_name=os.getenv("TISTORY_BLOG_NAME"),
            title_text=title,
            content_text=content
        )
        return jsonify({"status":"success","result":res})
    except Exception as e:
        print(f"Error occurred: {e}")  # ⭐️⭐️⭐️ 추가!

        return jsonify({"status":"error","message":str(e)}), 500

# ⭐️⭐️⭐️ 새로 추가하는 부분
@app.route("/screenshot", methods=["GET"])
def screenshot():
    screenshot_path = "/app/screenshot.png"
    if os.path.exists(screenshot_path):
        return send_file(screenshot_path, mimetype='image/png')
    else:
        return jsonify({"status": "error", "message": "스크린샷 파일이 없습니다."}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
