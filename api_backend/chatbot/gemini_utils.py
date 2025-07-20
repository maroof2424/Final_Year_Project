from decouple import config
import google.generativeai as genai

GEMINI_API_KEY = config("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def get_gemini_response(message):
    response = model.generate_content(message)
    return response.text
