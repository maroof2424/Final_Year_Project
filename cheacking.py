import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyC9436BlgjLQI938Cloq99W3nLP_QLURN0"  # Replace with your key

def test_gemini():
    try:
        genai.configure(api_key=GEMINI_API_KEY)

        # ✅ Use the correct model ID
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")

        # ✅ Use generate_content method
        response = model.generate_content("Hello Gemini! Are you working?")
        print("✅ Gemini Response:")
        print(response.text)

    except Exception as e:
        print("❌ Error communicating with Gemini API:")
        print(e)

if __name__ == "__main__":
    test_gemini()
