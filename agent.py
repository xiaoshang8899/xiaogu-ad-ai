import time

from services.ai_service import ai_service
from services.customer_service import customer_service
from utils.logger import logger
from utils.security import sha256_text


class TongyuanAgent:
    def __init__(self):
        self.ai_service = ai_service
        self.customer_service = customer_service

    @staticmethod
    def _safe_openid(openid):
        """
        OpenID 不直接写入日志，只保留 SHA256 前12位用于排查问题。
        """
        if not openid:
            return "-"

        return sha256_text(openid)[:12]

    def chat(self, message, openid=None, nickname=None, channel="api"):
        start_time = time.time()

        message = str(message or "").strip()
        channel = str(channel or "api").strip() or "api"

        if not message:
            logger.warning(
                "客服请求被拒绝 | 原因=消息为空 | channel=%s",
                channel
            )
            raise ValueError("客户消息不能为空")

        safe_openid = self._safe_openid(openid)

        logger.info(
            "客服请求开始 | channel=%s | openid_hash=%s | message_length=%s",
            channel,
            safe_openid,
            len(message)
        )

        customer = None

        try:
            # ==========================================
            # 1. 获取 / 创建客户
            # ==========================================
            if openid:
                customer = self.customer_service.get_or_create_customer(
                    openid=openid,
                    nickname=nickname,
                    source=channel
                )

                logger.info(
                    "客户信息已加载 | customer_id=%s | channel=%s | openid_hash=%s",
                    customer.get("id") if customer else "-",
                    channel,
                    safe_openid
                )

            # ==========================================
            # 2. 人工接管检查
            # ==========================================
            if customer and customer.get("human_takeover"):
                elapsed = round(time.time() - start_time, 3)

                logger.info(
                    "人工接管中，跳过AI | customer_id=%s | channel=%s | elapsed=%ss",
                    customer["id"],
                    channel,
                    elapsed
                )

                return {
                    "answer": "您的咨询正在由工作人员处理中，请稍候。",
                    "customer": customer,
                    "human_takeover": True
                }

            # ==========================================
            # 3. 加载历史对话
            # ==========================================
            conversation_history = []

            if customer:
                history = self.customer_service.get_conversations(
                    customer["id"],
                    limit=10
                )

                history = list(reversed(history))

                for item in history:
                    if item.get("user_message"):
                        conversation_history.append({
                            "role": "user",
                            "content": item["user_message"]
                        })

                    if item.get("ai_reply"):
                        conversation_history.append({
                            "role": "assistant",
                            "content": item["ai_reply"]
                        })

                logger.info(
                    "历史对话已加载 | customer_id=%s | history_count=%s",
                    customer["id"],
                    len(history)
                )

            # ==========================================
            # 4. 调用AI服务
            # ==========================================
            answer = self.ai_service.chat(
                user_message=message,
                conversation_history=conversation_history
            )

            # ==========================================
            # 5. 保存AI对话
            # ==========================================
            if customer:
                self.customer_service.save_conversation(
                    customer_id=customer["id"],
                    user_message=message,
                    ai_reply=answer,
                    channel=channel,
                    is_human=False
                )

                logger.info(
                    "AI对话已保存 | customer_id=%s | channel=%s",
                    customer["id"],
                    channel
                )

            # ==========================================
            # 6. 请求完成
            # ==========================================
            elapsed = round(time.time() - start_time, 3)

            logger.info(
                "客服请求成功 | channel=%s | customer_id=%s | elapsed=%ss",
                channel,
                customer.get("id") if customer else "-",
                elapsed
            )

            return {
                "answer": answer,
                "customer": customer,
                "human_takeover": False
            }

        except ValueError:
            raise

        except Exception:
            elapsed = round(time.time() - start_time, 3)

            logger.exception(
                "客服请求失败 | channel=%s | customer_id=%s | elapsed=%ss",
                channel,
                customer.get("id") if customer else "-",
                elapsed
            )

            raise


agent = TongyuanAgent()


def ask_ai(user_message):
    result = agent.chat(
        message=user_message,
        channel="api"
    )

    return result["answer"]
