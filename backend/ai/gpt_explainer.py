import google.generativeai as genai

# Configure your Gemini API key
genai.configure(api_key="Enter Your API key")

def explain_event(log: str) -> str:
    """
    Generate a human-friendly explanation for a page replacement event.
    """
    prompt = (
        "You are an expert Operating Systems tutor helping a student understand "
        "page replacement algorithms. Explain the following simulation event "
        "clearly and simply:\n\n"
        f"{log}\n\n"
        "Focus on why it was a hit or fault, how the chosen algorithm made that decision, "
        "and what it implies for future accesses."
    )

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "No explanation generated."
    except Exception as e:
        return f"AI explanation unavailable due to error: {str(e)}"
