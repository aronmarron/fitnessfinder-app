import streamlit as st
import fitz  # PyMuPDF
import zipfile
import io

# Sidebar setup
with st.sidebar:
    st.header("Search Controls")
    user_keywords = st.text_area("Keywords (comma separated):", "fitness, gym, exercise, workout, strength, cardio")
    keywords = [k.strip().lower() for k in user_keywords.split(",")]
    
    st.divider()
    start_btn = st.button("🚀 Run Extraction", use_container_width=True)

st.title("🏋️‍♂️ Fitness Finder")

# Main uploader
uploaded_file = st.file_uploader("Upload PDF or ZIP", type=["pdf", "zip"])

def process_stream(stream, search_terms):
    """Processes PDF stream without loading everything into redundant variables."""
    src_doc = fitz.open(stream=stream, filetype="pdf")
    out_doc = fitz.open()
    
    for page in src_doc:
        text = page.get_text().lower()
        if any(word in text for word in search_terms):
            out_doc.insert_pdf(src_doc, from_page=page.number, to_page=page.number)
            
    return out_doc

if uploaded_file and start_btn:
    final_pdf = fitz.open()
    total_found = 0
    
    with st.status("Processing large files...", expanded=True) as status:
        file_bytes = uploaded_file.getvalue() # Get bytes once
        
        if uploaded_file.name.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
                pdf_list = [n for n in z.namelist() if n.lower().endswith(".pdf")]
                for name in pdf_list:
                    st.write(f"Scanning: {name}")
                    with z.open(name) as f:
                        temp_doc = process_stream(f.read(), keywords)
                        if len(temp_doc) > 0:
                            final_pdf.insert_pdf(temp_doc)
                            total_found += len(temp_doc)
                        temp_doc.close()
        else:
            temp_doc = process_stream(file_bytes, keywords)
            total_found = len(temp_doc)
            if total_found > 0:
                final_pdf.insert_pdf(temp_doc)
            temp_doc.close()
        
        status.update(label="Complete!", state="complete")

    if total_found > 0:
        out_buffer = io.BytesIO()
        final_pdf.save(out_buffer)
        final_pdf.close()
        
        st.success(f"Extracted {total_found} pages.")
        st.download_button("📥 Download PDF", out_buffer.getvalue(), "Fitness_Export.pdf", "application/pdf")
    else:
        st.error("No matches found.")