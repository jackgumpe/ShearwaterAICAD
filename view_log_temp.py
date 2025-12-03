from src.persistence.persistence_cli import ConversationBrowser

browser = ConversationBrowser()
messages = browser.get_recent_messages(10)

if not messages:
    print("No messages found.")
else:
    for msg in messages:
        timestamp = msg['timestamp'][:19] if msg['timestamp'] else 'unknown'
        sender = msg['sender'][:15]
        preview = msg['preview'][:50]
        print(f"  {timestamp} | {sender:15s} | {preview}")
