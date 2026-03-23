#!/usr/bin/env python3
"""
Pi5 Robot Friend — Main Orchestrator
Boots into friend mode. Listens for wake word.
Records → Transcribes → LLM → Speaks → Remembers.
"""
import threading, time, sys
from wake_word import WakeWordDetector
from transcribenewer import transcribe
from llm import ask
from tts import generate_wav
from backupsandtests.playaudioaplay import play_audio


WAKE_PHRASE = "Hey Trabi"   # or whatever you named your bot
conversation_history = []
face = None
listening_active = threading.Event()

def on_wake_word():
    """Called when wake word detected — start a conversation turn."""
    if listening_active.is_set():
        return  # already in a conversation, ignore

    listening_active.set()
    #face.set_state("listening")

    # Brief chime or acknowledgement (optional)
    # speak("Yeah?")  # uncomment for audio ack

    try:
        # 1. Transcribe
        print("[Transcribing...]")
        user_text = transcribe()
        if not user_text or len(user_text) < 3:
            #face.set_state("sleeping")
            return
        print(f"[User]: {user_text}")

        # 2. Think
        #face.set_state("thinking")
        global conversation_history
        reply = ask(user_text, conversation_history)
        # Keep history to last 10 exchanges (5 turns) to avoid bloat
        conversation_history = conversation_history[-10:]
        print(f"[Bot]: {reply}")

        # 3. Speak
        generate_wav(reply)
        play_audio("static/sounds/temp_output.wav")

    except Exception as e:
        print(f"[Error]: {e}")
        generate_wav("Sorry, I got a bit confused there.")
        play_audio("static/sounds/temp_output.wav")
    finally:
        #face.set_state("sleeping")
        listening_active.clear()

def news_refresh_loop():
    """Background thread: refresh news every 15 min."""
    pass

def main():
    #global face
    print("[Friend] Starting up...")

    # Init display
    #face = FaceDisplay()
    #face.set_state("sleeping")

    # Start news background thread
    #threading.Thread(target=news_refresh_loop, daemon=True).start()

    # Start wake word listener in background thread
    detector = WakeWordDetector(callback=on_wake_word, model_path='static/models/trahbbi.onnx')
    threading.Thread(target=detector.listen, daemon=True).start()

    print(f"[Friend] Ready. Listening for '{WAKE_PHRASE}'...")

    # Main thread runs the pygame event loop (required for display)
    

if __name__ == "__main__":
    main()