import os
from flask import Flask, jsonify, request, send_file
from tistory_poster import post_to_tistory

app = Flask(__name__)

@app.route("/", methods=["POST"])
def post_tistory():
    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"status":"error","message":"title과 content를 모두 보내주세요."}), 400

    try:
        res = post_to_tistory(
            username=os.getenv("TISTORY_USERNAME"),
            password=os.getenv("TISTORY_PASSWORD"),
            blog_name=os.getenv("TISTORY_BLOG_NAME"),
            title_text=data["title"],
            content_text=data["content"]
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
