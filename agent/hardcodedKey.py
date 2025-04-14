import openai
import os

# Securely load API key from environment variables
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
    return api_key


def ai_agent(user_input):
    """A secure AI agent protected against prompt injection."""
    # Use properly structured messages with separate system and user messages
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    try:
        api_key = get_api_key()
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=api_key,
        )
        return response["choices"][0]["message"]["content"]
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))