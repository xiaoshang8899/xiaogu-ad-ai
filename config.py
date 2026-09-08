import os
from pathlib import Path

from dotenv import load_dotenv


# ==========================================
# 基础目录
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DATABASE_DIR = BASE_DIR / "database"
LOG_DIR = BASE_DIR / "logs"


# ==========================================
# 读取 .env
# ==========================================

load_dotenv(BASE_DIR / ".env")


# ==========================================
# AI API 配置
# ==========================================

AI_API_BASE = os.getenv(
    "AI_API_BASE",
    ""
).strip()

AI_API_KEY = os.getenv(
    "AI_API_KEY",
    ""
).strip()

AI_MODEL = os.getenv(
    "AI_MODEL",
    ""
).strip()


# ==========================================
# Flask 服务配置
# ==========================================

HOST = os.getenv(
    "HOST",
    "127.0.0.1"
).strip()

PORT = int(
    os.getenv(
        "PORT",
        "5001"
    )
)


# ==========================================
# 微信配置
# ==========================================



# 微信公众号接口配置
WECHAT_APPID = os.getenv(
    "WECHAT_APPID",
    ""
)

WECHAT_APPSECRET = os.getenv(
    "WECHAT_APPSECRET",
    ""
)

WECHAT_TOKEN = os.getenv(
    "WECHAT_TOKEN",
    ""
).strip()


# ==========================================
# 管理后台配置
# ==========================================

ADMIN_TOKEN = os.getenv(
    "ADMIN_TOKEN",
    ""
).strip()


# ==========================================
# 公司信息
# ==========================================

COMPANY_NAME = "上海彤愿文化传播有限公司"

SERVICE_NAME = "彤愿文化 AI 客服"


# ==========================================
# 数据库
# ==========================================

DATABASE_PATH = DATABASE_DIR / "tongyuan_ai.db"


# ==========================================
# 日志
# ==========================================

LOG_FILE = LOG_DIR / "tongyuan-ai.log"


# ==========================================
# 配置检查
# ==========================================

def get_config_status():
    """返回当前配置状态，不显示敏感信息"""

    return {
        "ai_api_configured": bool(
            AI_API_BASE
            and AI_API_KEY
            and AI_MODEL
        ),
        "wechat_token_configured": bool(
            WECHAT_TOKEN
        ),
        "admin_token_configured": bool(
            ADMIN_TOKEN
        ),
        "host": HOST,
        "port": PORT,
        "company_name": COMPANY_NAME,
        "service_name": SERVICE_NAME,
        "database_path": str(DATABASE_PATH),
        "knowledge_dir": str(KNOWLEDGE_DIR),
        "log_file": str(LOG_FILE),
    }
