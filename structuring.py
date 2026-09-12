from google import genai
from google.genai import types

def process_file_bytes(file_bytes: bytes, mime_type: str, user_instructions: str = "", audio_bytes: bytes = None) -> str:
    """Sends file bytes to Gemini and extracts data based on text or voice instructions."""
    
    client = genai.Client(api_key="xxx")
    
    doc_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
    contents = [doc_part]
    
    # If the user recorded a voice command, append it to the AI's payload
    if audio_bytes:
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        contents.append(audio_part)
    
    prompt = f"""
    You are an expert AI extraction tool. 
    Analyze the provided document. The user has provided instructions (either via text below, or via the attached audio file). Follow their instructions EXACTLY.
    
    TEXT INSTRUCTIONS (if any): "{user_instructions}"
    
    Return the result as a JSON object. 
    
    FORMATTING RULES:
    1. TABLES: If extracting a table/register, place it under the key "extracted_table" as a list of JSON objects.
    2. EVERYTHING ELSE: Use short, lowercase keys with underscores.
    """
    contents.append(prompt)
    
    print(f"Sending dynamic request to Gemini (Voice Enabled: {bool(audio_bytes)})...")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1, 
        ),
    )
    
    return response.text