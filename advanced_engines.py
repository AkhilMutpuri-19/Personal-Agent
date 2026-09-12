import os
import io
import pandas as pd
from docx import Document
from google import genai
from google.genai import types

def process_advanced_task(data_bytes: bytes, data_mime: str, instructions: str = "", template_bytes: bytes = None, template_mime: str = None, task_type: str = "finance", audio_bytes: bytes = None) -> str:
    """Uploads massive files and handles optional voice commands for code execution."""
    
    client = genai.Client(api_key="xxx")
    uploaded_files = []
    temp_paths = []
    extracted_template_text = None

    try:
        # 1. BULLETPROOF DATA UPLOAD (Flatten Excel to CSV)
        data_path = "temp_data.csv"
        forced_data_mime = "text/csv"
        try:
            df = pd.read_csv(io.BytesIO(data_bytes), low_memory=False)
            df.to_csv(data_path, index=False)
        except Exception:
            xls = pd.ExcelFile(io.BytesIO(data_bytes))
            all_sheets_data = []
            for sheet_name in xls.sheet_names:
                df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
                df_sheet['Source_Sheet'] = sheet_name 
                all_sheets_data.append(df_sheet)
            combined_df = pd.concat(all_sheets_data, ignore_index=True)
            combined_df.to_csv(data_path, index=False)

        temp_paths.append(data_path)
        uploaded_data = client.files.upload(file=data_path, config={'mime_type': forced_data_mime})
        uploaded_files.append(uploaded_data)

        # 2. BULLETPROOF TEMPLATE HANDLING (Word Docs -> Text)
        if template_bytes and template_mime:
            if "word" in template_mime or "document" in template_mime or "docx" in template_mime:
                doc = Document(io.BytesIO(template_bytes))
                extracted_template_text = "\n".join([para.text for para in doc.paragraphs])
            else:
                forced_temp_mime = "text/plain"
                ext = ".txt"
                if "pdf" in template_mime: 
                    ext, forced_temp_mime = ".pdf", "application/pdf"
                elif "png" in template_mime: 
                    ext, forced_temp_mime = ".png", "image/png"
                elif "jpeg" in template_mime or "jpg" in template_mime: 
                    ext, forced_temp_mime = ".jpg", "image/jpeg"
                
                template_path = f"temp_template{ext}"
                with open(template_path, "wb") as f: f.write(template_bytes)
                temp_paths.append(template_path)
                uploaded_template = client.files.upload(file=template_path, config={'mime_type': forced_temp_mime})
                uploaded_files.append(uploaded_template)
                
        # 3. HANDLE VOICE RECORDINGS
        if audio_bytes:
            audio_path = "temp_audio.wav"
            with open(audio_path, "wb") as f: f.write(audio_bytes)
            temp_paths.append(audio_path)
            uploaded_audio = client.files.upload(file=audio_path, config={'mime_type': 'audio/wav'})
            uploaded_files.append(uploaded_audio)

        # 4. PROMPT CONSTRUCTION
        if task_type == "report":
            prompt = f"""
            You are an expert R&D Data Scientist and Python programmer.
            Listen carefully to the attached audio file or read the text instructions. The user will give you complex, dynamic instructions to filter, slice, or evaluate reporting data.
            
            TEXT INSTRUCTIONS (if any): "{instructions}"
            
            CRITICAL INSTRUCTIONS FOR YOUR PYTHON SCRIPT:
            1. ADAPTIVE LOGIC: Translate the user's complex verbal logic (e.g., "only check the first 3 hours", "if temp is over 40, output 'FAIL'", "find the average but exclude zeroes") directly into advanced pandas operations.
            2. FORMATTING RULES: If the user asks you to format a number (e.g., "round to 2 decimals" or "add '°C' to the end"), you must apply that formatting to the string inside your final output.
            3. You MUST output your final answer PURELY as a valid JSON dictionary. 
            4. The keys in your JSON MUST match the names of the {{tags}} the user mentions.
            5. Do NOT output any other text, markdown, or explanation. Only the JSON object.
            """
        elif task_type == "finance":
            prompt = f"""
            You are an expert financial AI data analyst.
            Listen to the attached audio file or read the text instructions to determine the calculations.
            
            CRITICAL INSTRUCTIONS FOR YOUR PYTHON SCRIPT:
            1. You MUST use Python Code Execution to perform the math.
            2. Use `import os; os.listdir('.')` to identify the exact uploaded `.csv` file name.
            3. Load it with pandas. Check `df['Source_Sheet'].unique()` to find exact string names before filtering.
            
            TEXT INSTRUCTIONS (if any): "{instructions}"
            
            CRITICAL RULE: Never generate stock-style charts or candlestick graphs. 
            Do not write a formal report. Simply output the exact calculations requested. Be concise and strictly mathematical.
            """

        print(f"Sending {task_type} request to Code Execution (Voice Enabled: {bool(audio_bytes)})...")
        contents = uploaded_files + [prompt]
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.1, tools=[{"code_execution": {}}]),
        )
        return response.text

    finally:
        for uf in uploaded_files:
            try:
                client.files.delete(name=uf.name)
            except: pass
        for tp in temp_paths:
            if os.path.exists(tp): os.remove(tp)