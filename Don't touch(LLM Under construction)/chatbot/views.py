from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from gpt4all import GPT4All

model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")  # Ensure this file is downloaded

class ChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = request.data.get("message")
        response = model.chat_completion(message)
        return Response({"response": response})
