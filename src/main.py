from openai import OpenAI
import os

def main():
    # Initialize the OpenAI client
    # Note: Make sure to set your OPENAI_API_KEY in your environment variables
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        # Create a simple completion using GPT-3.5
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say Hello World!"}
            ]
        )
        
        # Print the response
        print("OpenAI Response:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
