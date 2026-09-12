import streamlit as st
import json
import pandas as pd
import io
from docx import Document
from structuring import process_file_bytes
from advanced_engines import process_advanced_task

st.set_page_config(page_title="Enterprise AI System", layout="wide")

st.title("Rockwell Enterprise AI Operations")
st.markdown("Select a department tab below to access specialized AI capabilities.")

tab1, tab2, tab3 = st.tabs(["1. Manual Entry (Vision)", "2. Report Making", "3. Finance Team (Math Engine)"])

# =====================================================================
# TAB 1: MANUAL ENTRY
# =====================================================================
with tab1:
    st.markdown("### Replace Physical Data Entry")
    if "structured_data" not in st.session_state: 
        st.session_state.structured_data = None
        
    col1, col2 = st.columns(2)

    with col1:
        # THE NEW VOICE TOGGLE
        instr_mode_1 = st.radio("Instruction Method:", ("Type Text", "Record Voice"), horizontal=True, key="t1_radio")
        user_instructions, audio_bytes = "", None
        
        if instr_mode_1 == "Type Text":
            user_instructions = st.text_area("What do you want the AI to extract?", value="Extract all data into a table.", key="t1_text")
        else:
            audio_file = st.audio_input("Record your instructions")
            if audio_file: 
                audio_bytes = audio_file.getvalue()

        input_method = st.radio("Select Input Method:", ("File Upload", "Camera Capture"))
        file_bytes, mime_type = None, None
        
        if input_method == "File Upload":
            uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"])
            if uploaded_file:
                file_bytes, mime_type = uploaded_file.getvalue(), uploaded_file.type
                if mime_type == "application/pdf": st.success("PDF Uploaded")
                else: st.image(uploaded_file, use_container_width=True)
        elif input_method == "Camera Capture":
            camera_photo = st.camera_input("Take a picture")
            if camera_photo: 
                file_bytes, mime_type = camera_photo.getvalue(), camera_photo.type

        if file_bytes and st.button("Process Document", type="primary"):
            with st.spinner("AI Vision is analyzing..."):
                try:
                    json_string = process_file_bytes(file_bytes, mime_type, user_instructions, audio_bytes)
                    st.session_state.structured_data = json.loads(json_string)
                    st.success("Analysis complete!")
                except Exception as e: st.error(f"Error: {e}")

    with col2:
        if st.session_state.structured_data:
            data = st.session_state.structured_data
            table_data = data.get("extracted_table", None)
            flat_data = {k: v for k, v in data.items() if k != "extracted_table"}
            edited_df, edited_data = None, {}
            
            with st.form("validation_form"):
                st.markdown("### Validate Output")
                for key, value in flat_data.items():
                    label = key.replace("_", " ").title()
                    if isinstance(value, list): edited_data[key] = st.text_area(label, value=", ".join(str(v) for v in value))
                    elif len(str(value)) > 100: edited_data[key] = st.text_area(label, value=str(value), height=150)
                    else: edited_data[key] = st.text_input(label, value=str(value))
                if table_data:
                    st.markdown("### 📋 Extracted Table")
                    df = pd.DataFrame(table_data)
                    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
                    edited_data["extracted_table"] = edited_df.to_dict(orient="records")
                if st.form_submit_button("Approve & Save"): st.success("Saved!")

# =====================================================================
# TAB 2: REPORT MAKING (Excel Template Injection Engine)
# =====================================================================
with tab2:
    st.markdown("### Strict Excel Template Injection")
    
    # THE NEW VOICE TOGGLE
    instr_mode_2 = st.radio("Instruction Method:", ("Type Text", "Record Voice"), horizontal=True, key="t2_radio")
    rep_instructions, audio_bytes_2 = "", None
    
    if instr_mode_2 == "Type Text":
        rep_instructions = st.text_area("Define your {{tags}} and calculations:", key="t2_text")
    else:
        audio_file_2 = st.audio_input("Record your calculation instructions", key="t2_audio")
        if audio_file_2: audio_bytes_2 = audio_file_2.getvalue()
    
    colA, colB = st.columns(2)
    with colA: data_file = st.file_uploader("1. Upload Raw Data", type=["xlsx", "csv"], key="t2_data")
    with colB: template_file = st.file_uploader("2. Upload Master Template", type=["xlsx"], key="t2_temp")
        
    if data_file and template_file and st.button("Inject Data & Generate Report", type="primary"):
        with st.spinner("Executing math scripts and injecting into template..."):
            try:
                json_string = process_advanced_task(
                    data_bytes=data_file.getvalue(),
                    data_mime=data_file.type,
                    instructions=rep_instructions,
                    task_type="report",
                    audio_bytes=audio_bytes_2
                )
                clean_json = json_string.strip().replace("```json", "").replace("```", "")
                ai_data_dict = json.loads(clean_json)
                st.success("Math execution successful! Data extracted:")
                st.json(ai_data_dict)
                final_excel_bytes = fill_excel_template(template_file.getvalue(), ai_data_dict)
                st.download_button(label="📊 Download Injected Excel Report", data=final_excel_bytes, file_name="Final_Laboratory_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e: st.error(f"Error: {e}")

# =====================================================================
# TAB 3: FINANCE TEAM (Complex Math Engine)
# =====================================================================
with tab3:
    st.markdown("### Secure Financial Computations")
    
    # THE NEW VOICE TOGGLE
    instr_mode_3 = st.radio("Instruction Method:", ("Type Text", "Record Voice"), horizontal=True, key="t3_radio")
    fin_instructions, audio_bytes_3 = "", None
    
    if instr_mode_3 == "Type Text":
        fin_instructions = st.text_area("Financial Task:", key="t3_text")
    else:
        audio_file_3 = st.audio_input("Record your financial query", key="t3_audio")
        if audio_file_3: audio_bytes_3 = audio_file_3.getvalue()
    
    fin_file = st.file_uploader("Upload Financial Ledger", type=["xlsx", "csv"], key="t3_file")
    
    if fin_file and st.button("Execute Math Engine", type="primary"):
        with st.spinner("Sandbox active. AI is writing Python scripts..."):
            try:
                fin_answer = process_advanced_task(
                    data_bytes=fin_file.getvalue(),
                    data_mime=fin_file.type,
                    instructions=fin_instructions,
                    task_type="finance",
                    audio_bytes=audio_bytes_3
                )
                st.success("Mathematical execution complete!")
                st.info(fin_answer)
            except Exception as e: st.error(f"Error: {e}")