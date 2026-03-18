from groq import Groq
from config.settings import groq_api_key as GROQ_API_KEY
client = Groq(api_key=GROQ_API_KEY)

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"LLM Error: {str(e)}"