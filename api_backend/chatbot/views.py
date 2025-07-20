import os
import google.generativeai as genai
from django.http import StreamingHttpResponse, JsonResponse
from rest_framework.decorators import api_view
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@api_view(["POST"])
def chat_with_gemini(request):
    user_msg = request.data.get("message")
    if not user_msg:
        return JsonResponse({"error": "No message provided"}, status=400)

    try:
        # Initialize Gemini Pro
        model = genai.GenerativeModel("gemini-2.5-flash")
        chat = model.start_chat()

        def generate_response():
            for chunk in chat.send_message(user_msg, stream=True):
                if chunk.text:
                    yield chunk.text

        return StreamingHttpResponse(generate_response(), content_type="text/plain")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
