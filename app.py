from flask import Flask, jsonify

import config
from agent import agent
from routes.chat import chat_bp
from routes.admin import admin_bp
from services.knowledge_service import knowledge_service
from services.customer_service import customer_service
from services.community_service import community_service


def create_app():
    app = Flask(__name__)

    # ==========================================
    # API 路由
    # ==========================================

    app.register_blueprint(chat_bp)

    # 管理后台
    app.register_blueprint(admin_bp)

    # 微信公众号接口
    from routes.wechat import wechat_bp
    app.register_blueprint(wechat_bp)

    # ==========================================
    # 首页
    # ==========================================

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "status": "ok",
            "service": "彤愿文化 AI 客服",
            "message": "Flask Agent 正常运行"
        })

    # ==========================================
    # 基础健康检查
    # ==========================================

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "service": "tongyuan-wechat-ai"
        })

    # ==========================================
    # 系统框架状态
    # ==========================================

    @app.route("/api/system/status", methods=["GET"])
    def system_status():
        config_status = config.get_config_status()

        try:
            knowledge_files = len(
                knowledge_service.files
            )
        except Exception:
            knowledge_files = 0

        try:
            database_ready = customer_service.get_connection()
            database_ready.close()
            database_status = True
        except Exception:
            database_status = False

        try:
            community_connection = (
                community_service.get_connection()
            )
            community_connection.close()
            community_status = True
        except Exception:
            community_status = False

        return jsonify({
            "status": "ok",
            "service": config.SERVICE_NAME,
            "framework": {
                "flask": True,
                "agent": agent is not None,
                "knowledge_base": knowledge_files > 0,
                "knowledge_files": knowledge_files,
                "customer_database": database_status,
                "community_database": community_status,
                "chat_api": True,
                "admin_api": True,
                "wechat_api": True,
                "ai_api_configured": config_status["ai_api_configured"]
            },
            "port": config.PORT
        })

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=False
    )
