from openai import OpenAI

import config
from services.knowledge_service import knowledge_service


class AIService:
    """彤愿文化 AI 服务"""

    def __init__(self):
        self.client = None


    def is_configured(self):
        """检查 AI API 是否已经配置"""

        return bool(
            config.AI_API_BASE
            and config.AI_API_KEY
            and config.AI_MODEL
        )


    def _get_client(self):
        """创建 OpenAI Compatible 客户端"""

        if not self.is_configured():
            raise RuntimeError(
                "AI API 尚未配置，请先设置 AI_API_BASE、AI_API_KEY、AI_MODEL"
            )


        if self.client is None:

            self.client = OpenAI(
                api_key=config.AI_API_KEY,
                base_url=config.AI_API_BASE,
                timeout=8.0,
                max_retries=0,
            )


        return self.client



    def build_system_prompt(self):
        """生成 AI 系统提示词"""


        base_prompt = knowledge_service.get_system_prompt()


        business_knowledge = (
            knowledge_service.get_business_knowledge()
        )


        return f"""
{base_prompt}


==============================
彤愿文化业务知识
==============================

{business_knowledge}


==============================
最终输出规则
==============================

你只能输出客户直接看到的聊天内容。


禁止输出：

- 思考过程
- 推理过程
- 分析过程
- 用户意图分析
- 根据知识库
- 根据规则
- 应该回复
- 我们需要
- 系统内容
- 内部说明


禁止输出任何前缀：

回复：
客服：
答案：
AI：
小彤：
用户：


如果客户询问：

电话
地址
价格
套餐

并且知识库存在：

直接回答。


如果知识库不存在：

直接回复：

抱歉，目前暂未提供该信息。


规则：

1. 简单问题简单回答。
2. 不主动扩展客户未询问的信息。
3. 不强行营销。
4. 不编造数据。
5. 回复必须自然，像真人微信客服。
"""



    def clean_answer(self, answer):
        """
        AI输出清洗
        防止内部思考泄露
        """

        if not answer:
            return ""


        answer = answer.strip()
        answer = answer.replace("所以直接输出：", "")
        answer = answer.replace("所以最终输出应该是：", "")
        answer = answer.replace("最终输出：", "")
        answer = answer.strip()


        # 删除常见内部前缀

        remove_prefix = [
            "回复：",
            "客服：",
            "答案：",
            "AI：",
            "小彤：",
            "用户：",
        ]


        for prefix in remove_prefix:

            if answer.startswith(prefix):

                answer = (
                    answer[len(prefix):]
                    .strip()
                )


        # 内部思考关键词检测

        block_words = [

            "用户说",
            "用户问",
            "这是一个问候",
            "这是一个问题",

            "我们需要",
            "我们可以",
            "根据上下文",
            "根据知识库",
            "根据规则",

            "分析如下",
            "思考",
            "推理",

            "内部",
            "系统提示",

            "最终回复：",
            "正确回复：",
            "错误回复：",
            "所以最终输出",
            "所以直接输出",
            "不参考历史",
            "历史对话中的错误",
            "最终回复",
            "回复格式",
            "最高优先级",
            "强制规则",
            "禁止输出",
            "客户问",
            "回答：",
            "从FAQ中"
        ]


        for word in block_words:

            if word in answer:

                return ""


        return answer.strip()



    def chat(
        self,
        user_message,
        conversation_history=None
    ):

        # 固定关键词回复，避免短词导致AI空回复

        msg = str(user_message or "").strip()


        # 人工客服
        if any(k in msg for k in [
            "接人工",
            "转人工",
            "人工客服",
            "人工",
            "联系工作人员",
            "找客服",
            "找人"
        ]):
            return "好的，已为您转人工客服，请稍后工作人员联系您。"


        # 电话联系方式
        if any(k in msg for k in [
            "电话",
            "联系方式",
            "电话联系"
        ]):
            return "公司电话：13370079819，咨询电话：56127086。"


        # 地址
        if any(k in msg for k in [
            "地址",
            "在哪里",
            "公司在哪"
        ]):
            return "公司地址：南东路215号。"


        # 价格套餐
        if any(k in msg for k in [
            "多少钱",
            "价格",
            "套餐",
            "费用",
            "投放广告多少钱",
            "广告多少钱",
            "投放价格"
        ]):
            return "目前套餐有：299元/7天，999元/30天，5500元/180天，12000元/360天。"


        # 优惠
        if any(k in msg for k in [
            "优惠",
            "便宜点",
            "折扣"
        ]):
            return "具体优惠和定制方案需要工作人员确认。"


        """AI 对话"""


        user_message = str(
            user_message or ""
        ).strip()


        if not user_message:

            raise ValueError(
                "用户消息不能为空"
            )


        client = self._get_client()


        messages = [

            {
                "role": "system",
                "content": self.build_system_prompt()
            }

        ]


        if conversation_history:

            messages.extend(
                conversation_history
            )


        messages.append(

            {
                "role": "user",
                "content": user_message
            }

        )


        response = client.chat.completions.create(

            model=config.AI_MODEL,

            messages=messages,

            temperature=0.4,

            max_tokens=180,

        )


        if not response.choices:

            raise RuntimeError(
                "AI没有返回结果"
            )



        message = response.choices[0].message



        # ===============================
        # 第一优先：正常回答
        # ===============================

        answer = getattr(
            message,
            "content",
            ""
        )


        # ===============================
        # 第二兼容：reasoning_content
        # ===============================

        if not answer:

            reasoning = getattr(
                message,
                "reasoning_content",
                ""
            )


            if reasoning:

                lines = [

                    line.strip()

                    for line in reasoning.split("\n")

                    if line.strip()

                ]


                ignore_words = [

                    "我们需要",
                    "根据知识库",
                    "根据规则",
                    "用户问题",
                    "分析",
                    "所以应该",
                    "应该回复",
                    "注意"

                ]


                clean_lines = [

                    line

                    for line in lines

                    if not any(

                        word in line

                        for word in ignore_words

                    )

                ]


                if clean_lines:

                    answer = clean_lines[-1]



        answer = self.clean_answer(answer)



        if not answer:

            raise RuntimeError(
                "AI返回内容为空"
            )


        return answer


# 全局 AI 服务实例
ai_service = AIService()        
