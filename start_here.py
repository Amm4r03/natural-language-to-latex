user_api_key = input("enter your cohere API key : ")
user_api_key = user_api_key.strip()

with open(".env", "w") as file:
    file.write(f"COHERE_API_KEY=\"{user_api_key}\"")

print("API key saved to .env file")