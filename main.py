import os
from flask import Flask, jsonify, request
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
