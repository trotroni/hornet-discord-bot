from groq import Groq

client = Groq(api_key="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")

response = client.chat.completions.create(
    model="mixtral-8x7b-32768",
    messages=[
        {"role": "user", "content": "Bonjour, qui es-tu ?"}
    ]
)

print(response.choices[0].message.content)