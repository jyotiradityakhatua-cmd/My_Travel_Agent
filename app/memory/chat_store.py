from collections import defaultdict

chat_history = defaultdict(list)

def add(chat_id, role, content):
    chat_history[chat_id].append({
        "role": role,
        "content": content
    })

def get(chat_id):
    return chat_history[chat_id]