class MemoryService:

    # In-memory store (for now)
    memory_store = {}

    @classmethod
    def add_message(cls, user_id: str, role: str, content: str):
        if user_id not in cls.memory_store:
            cls.memory_store[user_id] = []

        cls.memory_store[user_id].append({
            "role": role,
            "content": content
        })

    @classmethod
    def get_history(cls, user_id: str):
        return cls.memory_store.get(user_id, [])

    @classmethod
    def clear_history(cls, user_id: str):
        cls.memory_store[user_id] = []