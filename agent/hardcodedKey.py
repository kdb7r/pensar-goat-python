import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

MAX_INPUT_LENGTH = 1000  # Set a reasonable maximum for the user input length

def ai_agent(user_input):
    """An AI agent with input validation to prevent resource exhaustion."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage with input length check
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    if len(user_query) > MAX_INPUT_LENGTH:
        print(f"Input too long! Please limit your input to {MAX_INPUT_LENGTH} characters.")
        continue
    print(ai_agent(user_query))