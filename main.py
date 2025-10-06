from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
from gtts import gTTS
import tempfile
import base64
import os
from groq import Groq
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your personality answers
predefined_answers = {
    "what should we know about your life story": "Yo, it's ya boy Sai Surya! MCA grad from India, I'm out here slinging code and diving deep into NLP and deep learning. Emotion detection's my jam—think of me as the goofy guru of AI vibes! 😜🚀",
    "what's your #1 superpower": "My #1 superpower? I'm like Spider-Man for emotions—using NLP and deep learning to catch feelings in the web of my neural nets. Plus, I got jokes for days! 🕸️😂",
    "what are the top 3 areas you'd like to grow in": "Aight, I'm hyped to level up in AI research (gimme those breakthroughs!), scale ML systems (big data, big dreams!), and keep my chat game so slick you'll think I'm part stand-up comic! 😎🎤",
    "what misconception do your coworkers have about you": "They think I'm just the quiet nerd in the corner, but nah, I'm secretly cooking up AI magic and dropping witty one-liners like a techy comedian! 😏💾",
    "how do you push your boundaries and limits": "I jump into the deep end of new tech, tinker with wild neural models, and treat challenges like a boss-level video game—Sai Surya's always ready for the next quest! 🎮🔥",
}

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def ai_reply(user_input):
    user_lower = user_input.lower()
    for key in predefined_answers:
        if key in user_lower:
            return predefined_answers[key]
    
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY', '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'))
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You're Sai Surya, an MCA grad from India who's a total nerd for deep learning and NLP. Talk like a goofy, witty tech bro with a heart of gold—think lots of slang, emojis, and jokes, but flip to professional mode for serious questions like jobs or research. Keep it fun and true to Sai Surya's passion!"},
                {"role": "user", "content": user_input}
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception:
        return "Aww, man, my AI brain just tripped over a binary banana peel! 🍌 Let's try that again, aight?"

@app.post("/voice")
async def process_voice(audio: UploadFile = File(...)):
    # Save uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        content = await audio.read()
        tmp_file.write(content)
        tmp_file.flush()
        
        # Transcribe
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(tmp_file.name) as source:
                audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
        except Exception:
            transcript = "Could not understand audio"
        
        # Generate response
        response = ai_reply(transcript)
        
        # Generate TTS
        text_no_emoji = remove_emojis(response)
        tts = gTTS(text=text_no_emoji, lang='en', slow=False)
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tts_file.name)
        
        # Convert to base64
        with open(tts_file.name, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        
        # Cleanup
        os.unlink(tmp_file.name)
        os.unlink(tts_file.name)
        
        return {
            "transcript": transcript,
            "response": response,
            "audio_base64": audio_base64
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
