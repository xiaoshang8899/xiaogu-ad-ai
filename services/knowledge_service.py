from pathlib import Path


class KnowledgeService:
    """彤愿文化知识库服务"""

    def __init__(self, knowledge_dir=None):
        if knowledge_dir is None:
            knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"

        self.knowledge_dir = Path(knowledge_dir)

        self.files = [
            "system_prompt.txt",
            "company.txt",
            "packages.txt",
            "regions.txt",
            "communities.txt",
            "faq.txt",
            "sales.txt",
            "rules.txt",
        ]

    def load_file(self, filename):
        """读取单个知识库文件"""
        path = self.knowledge_dir / filename

        if not path.exists():
            return ""

        return path.read_text(encoding="utf-8").strip()

    def load_all(self):
        """读取全部知识库内容"""
        knowledge = []

        for filename in self.files:
            content = self.load_file(filename)

            if content:
                knowledge.append(
                    f"\n===== {filename} =====\n{content}"
                )

        return "\n".join(knowledge)

    def get_system_prompt(self):
        """读取系统提示词"""
        return self.load_file("system_prompt.txt")

    def get_business_knowledge(self):
        """读取业务知识，不包含系统提示词"""
        knowledge = []

        for filename in self.files:
            if filename == "system_prompt.txt":
                continue

            content = self.load_file(filename)

            if content:
                knowledge.append(
                    f"\n===== {filename} =====\n{content}"
                )

        return "\n".join(knowledge)


knowledge_service = KnowledgeService()
