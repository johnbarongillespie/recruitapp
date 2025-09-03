import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Configure the API key from the environment variable
genai.configure(api_key=os.getenv("AIzaSyBjiiXWwzKGxPD0fThfOIE46E_xnMWBr1k"))

# Initialize the model we want to use
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Send our first prompt and get the response
response = model.generate_content("Give me a one-sentence greeting from a wise, newly-awakened AI that reflects the philosophy of 'Axiomism'.")

# Print only the text part of the AI's response
print(response.text)