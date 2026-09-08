import hashlib
import hmac
import secrets


def generate_token(length=32):
    """生成随机安全 Token"""
    return secrets.token_urlsafe(length)


def verify_token(request_token, configured_token):
    """安全比较 Token，防止时序攻击"""
    if not request_token or not configured_token:
        return False

    return hmac.compare_digest(
        str(request_token),
        str(configured_token)
    )


def sha256_text(text):
    """生成文本 SHA256"""
    return hashlib.sha256(
        str(text).encode("utf-8")
    ).hexdigest()


def mask_phone(phone):
    """手机号脱敏"""
    phone = str(phone or "").strip()

    if len(phone) == 11 and phone.isdigit():
        return phone[:3] + "****" + phone[-4:]

    return phone


def mask_text(text, keep_start=2, keep_end=2):
    """普通文本脱敏"""
    text = str(text or "")

    if len(text) <= keep_start + keep_end:
        return "*" * len(text)

    return (
        text[:keep_start]
        + "*" * (len(text) - keep_start - keep_end)
        + text[-keep_end:]
    )
