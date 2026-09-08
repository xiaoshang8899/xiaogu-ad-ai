import hashlib
import time
import xml.etree.ElementTree as ET
import os
import threading
import json
from flask import Blueprint, request, make_response

from agent import agent


wechat_bp = Blueprint("wechat", __name__)


# 微信公众号 Token
WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "").strip()


def check_signature(signature, timestamp, nonce):
    """验证微信公众号服务器签名"""

    if not WECHAT_TOKEN:
        return False

    values = [
        WECHAT_TOKEN,
        timestamp,
        nonce
    ]

    values.sort()

    raw = "".join(values)

    sign = hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()

    return sign == signature


def parse_wechat_xml(xml_data):
    """解析微信公众号 XML 消息"""

    root = ET.fromstring(xml_data)

    data = {}

    for child in root:
        data[child.tag] = child.text or ""

    return data


def build_text_response(to_user, from_user, content):
    """生成微信公众号文本回复 XML"""

    timestamp = int(time.time())

    # 防止 AI 回复中的内容破坏 XML
    content = str(content or "").replace("]]>", "]]&gt;")

    xml = f"""
<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{timestamp}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
</xml>
""".strip()

    response = make_response(xml)
    response.content_type = "application/xml"

    return response


@wechat_bp.route("/wx", methods=["GET"])
def wechat_verify():
    """微信公众号服务器验证"""

    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")

    if check_signature(signature, timestamp, nonce):
        return echostr

    return "signature error", 403


@wechat_bp.route("/wx", methods=["POST"])
def wechat_message():
    """接收微信公众号消息并调用 AI"""

    try:
        xml_data = request.data

        if not xml_data:
            return "success"

        data = parse_wechat_xml(xml_data)

        msg_type = data.get("MsgType", "")
        from_user = data.get("FromUserName", "")
        to_user = data.get("ToUserName", "")

        # ====================================================
        # 文本消息 → AI
        # ====================================================

        if msg_type == "text":

            content = data.get("Content", "").strip()

            if not content:
                return "success"

            print(
                f"[WECHAT] 收到文本消息 | "
                f"openid_hash={hashlib.sha256(from_user.encode()).hexdigest()[:12]} | "
                f"length={len(content)}"
            )

            # 调用现有 TongyuanAgent
            result = agent.chat(
                message=content,
                openid=from_user,
                nickname=None,
                channel="wechat"
            )

            reply = str(
                result.get("answer", "")
            ).strip()

            if not reply:
                reply = "您好，您的消息已经收到，请稍后再试。"

            print(
                f"[WECHAT] AI回复完成 | "
                f"customer_id={result.get('customer', {}).get('id', '-') if result.get('customer') else '-'}"
            )

            return build_text_response(
                to_user=from_user,
                from_user=to_user,
                content=reply
            )

        # ====================================================
        # 非文本消息暂时返回 success
        # ====================================================

        return "success"

    except Exception as e:

        print(
            f"[WECHAT ERROR] {e}"
        )

        # 微信要求接口异常时尽快返回
        return "success"


# ============================================================
# API兼容入口
# ============================================================

@wechat_bp.route("/api/wechat", methods=["GET"])
def wechat_api_verify():
    return wechat_verify()


@wechat_bp.route("/api/wechat", methods=["POST"])
def wechat_api_message():
    return wechat_message()
