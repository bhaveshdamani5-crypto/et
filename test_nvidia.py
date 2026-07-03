from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

print("Testing NVIDIA 675B model connection...")
response = client.chat.completions.create(
    model="mistralai/mistral-large-3-675b-instruct-2512",
    messages=[{"role": "user", "content": "Return a JSON array: [{\"status\": \"connected\", \"model\": \"675B\"}]"}],
    max_tokens=50,
    temperature=0.1
)
print("SUCCESS:", response.choices[0].message.content)
