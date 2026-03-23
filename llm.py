import ollama
#from memory import get_user_context
#from web_news import get_news_snippet

SYSTEM_PROMPT = """You are a friendly, conversational AI companion.
Rules:
- Keep ALL responses under 2 sentences. Be concise and natural.
- Sound like a human friend, not an assistant.
- Occasionally (not always) bring up relevant news or topics you know the user likes.
- Never say "As an AI" or "I'm just a language model".
- If you don't know something, say so naturally like a human would.
- Respond ONLY with speech — no lists, no markdown, no asterisks."""

def ask(user_text, conversation_history=None):
    """Send text to Ollama and get a short, friendly response."""
    #user_context = get_user_context()   # their fav topics from memory
    #news = get_news_snippet(user_context)  # optional news injection

    messages = conversation_history or []

    # Occasionally inject a news hook into context
    system = SYSTEM_PROMPT
    #if news:
    #    system += f"\n\nFYI for context (you can bring this up naturally if relevant): {news}"
    #if user_context:
    #    system += f"\n\nThis user enjoys talking about: {', '.join(user_context)}"

    messages.append({"role": "user", "content": user_text})
    print('thinking...')
    response = ollama.chat(
            model='tinyllama',
            messages=[{"role": "system", "content": system}] + messages,
            stream=False,
            options = {
                "num_predict": 180,    # max ~80 tokens ≈ 3 sentences
                "temperature": 0.75,
                "top_p": 0.9
            }
        )

        
    reply = response["message"]["content"].strip()
    messages.append({"role": "assistant", "content": reply})
    

    answer = messages[1]['content']
    print(messages)
    return answer

if __name__=='__main__':
    q = input('prompt: ')
    ask(q)