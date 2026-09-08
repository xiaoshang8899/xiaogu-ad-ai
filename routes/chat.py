from flask import Blueprint, request, jsonify

from agent import agent


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """AI客服聊天接口"""

    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()
    openid = str(data.get("openid", "")).strip() or None
    nickname = str(data.get("nickname", "")).strip() or None
    channel = str(data.get("channel", "api")).strip() or "api"

    if not message:
        return jsonify({
            "status": "error",
            "message": "请输入咨询内容"
        }), 400

    try:
        result = agent.chat(
            message=message,
            openid=openid,
            nickname=nickname,
            channel=channel
        )

        return jsonify({
            "status": "success",
            "answer": result["answer"],
            "customer": result["customer"]
        })

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:
        print(f"[CHAT ERROR] {e}")

        return jsonify({
            "status": "error",
            "message": "客服系统暂时无法处理，请稍后再试"
        }), 500
