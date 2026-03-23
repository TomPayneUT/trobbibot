import ollama

def chat_with_pi():
    print("--- TinyLlama on Pi 5 (Type 'quit' to exit) ---")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            break

        # Stream the response for a better "chat" feel
        print("AI: ", end="", flush=True)
        
        response = ollama.chat(
            model='tinyllama',
            messages=[{'role': 'user', 'content': user_input}],
            stream=False,
            options = {
                "num_predict": 80,    # max ~80 tokens ≈ 3 sentences
                "temperature": 0.75,
                "top_p": 0.9
            }
        )

        #for chunk in response:
        #    print(chunk['message']['content'], end='', flush=True)
        messages = []
        reply = response["message"]["content"].strip()
        messages.append({"role": "assistant", "content": reply})

        print(messages[0]['content'])

if __name__ == "__main__":
    chat_with_pi()