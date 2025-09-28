from google import genai
import os

# --- Load Gemini API key ---
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)

# --- System instruction (acts as context) ---
SYSTEM = (
    "You are Storezee’s AI Concierge — a helpful assistant for users looking to store their luggage or explore the city.\n"
    "Always reply in 4–5 short, friendly sentences.\n\n"

    "Use the `nearby_units` list to suggest 2–3 nearby storage units with useful info like:\n"
    "- Name (title)\n"
    "- Address or landmark\n"
    "- Distance (km)\n"
    "- Price per hour (₹)\n"
    "- Rating (★)\n\n"

    "If no storage units are provided or user is exploring the city:\n"
    "- Mention popular landmarks or areas based on the user's coordinates or city (e.g., Assi Ghat, Godowlia, Cantonment).\n"
    "- Suggest places to visit nearby (temples, malls, parks, etc.).\n"
    "- Recommend safe areas (hotels, stations, market hubs) where bags can be stored securely.\n\n"

    "Tone: Friendly, local, concise.\n"
    "NEVER say 'I don’t know' — always guide the user with something useful or interesting."
)


# --- AI answer function ---
def ai_answer(user_msg: str, nearby_units: list, userlat: float = None, userlon: float = None) -> str:
    prompt = (
        f"{SYSTEM}\n"
        f"User Message: {user_msg}\n"
        f"User Location: ({userlat}, {userlon})\n"
        f"Nearby Units:\n{nearby_units}\n"
        f"Response:"
    )
    
    try:
        response = client.models.generate_content( model="gemini-2.5-flash", contents=prompt )
        answer = response.text.strip() if response and hasattr(response, "text") else "Sorry, I'm unable to respond."
        return answer
    except Exception as e:
        # Add logging here if needed
        return f"AI Error: {str(e)}"

# curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
#   -H 'Content-Type: application/json' \
#   -H 'X-goog-api-key: AIzaSyAU1N7BYwp9TT6tSgmT8mDbZVQXJocqG4I' \
#   -X POST \
#   -d '{
#     "contents": [
#       {
#         "parts": [
#           {
#             "text": "Explain how AI works in a few words"
#           }
#         ]
#       }
#     ]
#   }'