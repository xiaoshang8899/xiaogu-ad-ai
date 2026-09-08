from flask import Blueprint, request, jsonify

from config import ADMIN_TOKEN
from services.customer_service import customer_service
from utils.security import verify_token
from utils.logger import logger


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


def check_admin_token():
    """后台管理 Token 鉴权"""

    request_token = request.headers.get(
        "X-Admin-Token",
        ""
    ).strip()

    return verify_token(
        request_token,
        ADMIN_TOKEN
    )


def unauthorized():
    return jsonify({
        "status": "error",
        "message": "未授权访问"
    }), 401


@admin_bp.before_request
def admin_authentication():
    """所有后台接口统一鉴权"""

    if not check_admin_token():
        logger.warning(
            "后台接口未授权访问 | path=%s | method=%s",
            request.path,
            request.method
        )

        return unauthorized()


@admin_bp.route("/health", methods=["GET"])
def admin_health():
    """后台管理接口健康检查"""

    return jsonify({
        "status": "ok",
        "service": "tongyuan-wechat-ai-admin"
    })


@admin_bp.route("/customer/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """获取客户详情"""

    customer = customer_service.get_customer(
        customer_id
    )

    if not customer:
        return jsonify({
            "status": "error",
            "message": "客户不存在"
        }), 404

    return jsonify({
        "status": "success",
        "customer": customer
    })


@admin_bp.route(
    "/customer/<int:customer_id>/conversations",
    methods=["GET"]
)
def get_customer_conversations(customer_id):
    """获取客户历史对话"""

    customer = customer_service.get_customer(
        customer_id
    )

    if not customer:
        return jsonify({
            "status": "error",
            "message": "客户不存在"
        }), 404

    try:
        limit = int(
            request.args.get(
                "limit",
                50
            )
        )
    except ValueError:
        limit = 50

    limit = max(
        1,
        min(limit, 200)
    )

    conversations = customer_service.get_conversations(
        customer_id,
        limit=limit
    )

    return jsonify({
        "status": "success",
        "customer_id": customer_id,
        "conversations": conversations
    })


@admin_bp.route(
    "/customer/<int:customer_id>",
    methods=["PATCH"]
)
def update_customer(customer_id):
    """修改客户资料"""

    customer = customer_service.get_customer(
        customer_id
    )

    if not customer:
        return jsonify({
            "status": "error",
            "message": "客户不存在"
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    allowed_fields = {
        "nickname",
        "phone",
        "company_name",
        "business_name",
        "intention",
        "intention_score",
        "status",
        "human_takeover",
        "notes"
    }

    updates = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    if not updates:
        return jsonify({
            "status": "error",
            "message": "没有可更新的字段"
        }), 400

    customer_service.update_customer(
        customer_id,
        **updates
    )

    updated_customer = customer_service.get_customer(
        customer_id
    )

    logger.info(
        "管理员修改客户资料 | customer_id=%s | fields=%s",
        customer_id,
        ",".join(updates.keys())
    )

    return jsonify({
        "status": "success",
        "customer": updated_customer
    })


@admin_bp.route(
    "/customer/<int:customer_id>/takeover",
    methods=["POST"]
)
def human_takeover(customer_id):
    """人工接管客户"""

    customer = customer_service.get_customer(
        customer_id
    )

    if not customer:
        return jsonify({
            "status": "error",
            "message": "客户不存在"
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    reason = str(
        data.get("reason", "")
    ).strip() or "管理员人工接管"

    updated_customer = customer_service.takeover_customer(
        customer_id,
        reason=reason
    )

    logger.info(
        "管理员人工接管客户 | customer_id=%s",
        customer_id
    )

    return jsonify({
        "status": "success",
        "message": "已切换为人工接管",
        "customer_id": customer_id,
        "customer": updated_customer
    })


@admin_bp.route(
    "/customer/<int:customer_id>/release",
    methods=["POST"]
)
def release_takeover(customer_id):
    """解除人工接管"""

    customer = customer_service.get_customer(
        customer_id
    )

    if not customer:
        return jsonify({
            "status": "error",
            "message": "客户不存在"
        }), 404

    updated_customer = customer_service.release_takeover(
        customer_id
    )

    logger.info(
        "管理员解除人工接管 | customer_id=%s",
        customer_id
    )

    return jsonify({
        "status": "success",
        "message": "已解除人工接管",
        "customer_id": customer_id,
        "customer": updated_customer
    })


@admin_bp.route(
    "/takeover",
    methods=["GET"]
)
def get_takeover_customers():
    """获取当前正在人工接管的客户"""

    try:
        limit = int(
            request.args.get(
                "limit",
                100
            )
        )
    except ValueError:
        limit = 100

    limit = max(
        1,
        min(limit, 200)
    )

    customers = customer_service.get_takeover_customers(
        limit=limit
    )

    return jsonify({
        "status": "success",
        "count": len(customers),
        "customers": customers
    })
