import os
import streamlit as st
import base64
from groq import Groq
from PIL import Image
import io
import json
import httpx

# Streamlit page configuration
st.set_page_config(
    page_title="KYC Document Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key check
if "GROQ_API_KEY" not in st.secrets:
    st.error("Please add your GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

api_key = st.secrets["GROQ_API_KEY"]

# Initialize Groq client with httpx client to avoid proxy issues on Streamlit Cloud
client = Groq(
    api_key=api_key,
    http_client=httpx.Client() 
)

# Custom CSS for UI
st.markdown("""
    <style>
    .success-box { background-color: #d4edda; padding: 20px; border-radius: 5px; border-left: 4px solid #28a745; margin-bottom: 10px; }
    .warning-box { background-color: #fff3cd; padding: 20px; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 10px; }
    .error-box { background-color: #f8d7da; padding: 20px; border-radius: 5px; border-left: 4px solid #dc3545; margin-bottom: 10px; }
    .info-box { background-color: #d1ecf1; padding: 20px; border-radius: 5px; border-left: 4px solid #17a2b8; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("📄 KYC Document Analyzer")
st.markdown("*Powered by Groq - Llama 3.2 Vision*")

# File upload section
st.header("Step 1: Upload Document")
uploaded_file = st.file_uploader(
    "Upload an image (JPG, JPEG, PNG) or PDF file",
    type=["jpg", "jpeg", "png", "pdf"]
)

if uploaded_file:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.info(f"**File:** {uploaded_file.name}\n\n**Size:** {uploaded_file.size / 1024:.2f} KB")
    
    # Handle File Processing
    image = None
    if uploaded_file.type == "application/pdf":
        try:
            from pdf2image import convert_from_bytes
            st.info("Converting PDF page...")
            pdf_pages = convert_from_bytes(uploaded_file.read())
            if pdf_pages:
                image = pdf_pages[0]
        except Exception as e:
            st.error(f"❌ PDF Error: {e}. Ensure 'poppler-utils' is in packages.txt")
            st.stop()
    else:
        image = Image.open(uploaded_file)

    if image:
        # --- TECHNICAL FIX: CONVERT TO RGB BEFORE SAVING ---
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        with col2:
            st.image(image, caption="Uploaded Document", use_container_width=True)
        
        # Prepare Base64 Image
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        base64_image = base64.standard_b64encode(buffered.getvalue()).decode("utf-8")
        
        # Analysis button
        st.header("Step 2: Analyze Document")
        if st.button("🔍 Analyze KYC Document", type="primary", use_container_width=True):
            with st.spinner("Analyzing document with AI..."):
                
                # RESTORED YOUR FULL DETAILED PROMPT
                prompt = """Analyze this document carefully and provide a comprehensive KYC (Know Your Customer) analysis.

IMPORTANT: The following documents are considered VALID KYC documents:
- Passport
- Driving License
- Aadhaar Card
- National ID Card
- Voter ID
- PAN Card
- Bank Check/Cheque
- Any government-issued identification

Please provide your response in a structured JSON format with the following fields:

1. "is_kyc_document": (true/false) - Whether this is a legitimate KYC document or just a random image
2. "document_type": (string) - Identified document type (e.g., "Passport", "Driving License", "Aadhaar Card", "Check", "ID Card", "Other" etc.)
3. "confidence_level": (high/medium/low) - Confidence in the document identification
4. "extracted_details": {
    "person_name": Extracted person's name or null,
    "document_number": ID/License/Passport number or check number if available or null,
    "date_of_birth": if visible or null,
    "issue_date": if visible or null,
    "expiry_date": if visible or null,
    "issuing_authority": e.g., "RTO", "Passport Office", "UIDAI" etc. or null,
    "additional_info": Any other relevant KYC information
}
5. "image_quality_assessment": {
    "clarity": (excellent/good/fair/poor),
    "blurring_detected": (true/false),
    "cropping_issues": (true/false),
    "distortion_detected": (true/false),
    "lighting_quality": (excellent/good/fair/poor),
    "contrast": (high/medium/low),
    "overall_usability": (Suitable/Acceptable/Poor),
    "quality_notes": Specific observations about image quality
}
6. "kyc_verification_readiness": (Ready/Conditional/Not Ready)
7. "recommendations": (list) - Any recommendations for document re-submission
8. "risk_flags": (list) - Any red flags detected

Return ONLY valid JSON."""

                try:
                    # Use llama-3.2-11b-vision-preview (Official Groq Vision Model)
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                    }
                                ]
                            }
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"}
                    )
                    
                    analysis_result = json.loads(response.choices[0].message.content)
                    
                    # --- DISPLAY RESULTS ---
                    st.header("Step 3: Analysis Results")
                    
                    col_res1, col_res2, col_res3 = st.columns(3)
                    with col_res1:
                        if analysis_result.get("is_kyc_document"):
                            st.markdown(f'<div class="success-box"><strong>✅ Valid KYC</strong><br>Type: {analysis_result.get("document_type")}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-box"><strong>❌ Invalid Document</strong><br>Type: {analysis_result.get("document_type")}</div>', unsafe_allow_html=True)
                    
                    with col_res2:
                        st.markdown(f'<div class="info-box"><strong>Confidence</strong><br>{analysis_result.get("confidence_level", "").upper()}</div>', unsafe_allow_html=True)
                    
                    with col_res3:
                        readiness = analysis_result.get("kyc_verification_readiness", "")
                        status_class = "success-box" if readiness == "Ready" else "warning-box" if readiness == "Conditional" else "error-box"
                        st.markdown(f'<div class="{status_class}"><strong>Status</strong><br>{readiness}</div>', unsafe_allow_html=True)

                    # Extracted Details
                    st.subheader("👤 Extracted Details")
                    extracted = analysis_result.get("extracted_details", {})
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        st.write(f"**Name:** {extracted.get('person_name')}")
                        st.write(f"**ID Number:** {extracted.get('document_number')}")
                        st.write(f"**DOB:** {extracted.get('date_of_birth')}")
                    with d_col2:
                        st.write(f"**Expiry:** {extracted.get('expiry_date')}")
                        st.write(f"**Authority:** {extracted.get('issuing_authority')}")

                    # Quality & Risks
                    if analysis_result.get("risk_flags"):
                        st.subheader("🚩 Risk Flags")
                        for flag in analysis_result["risk_flags"]:
                            st.warning(flag)

                    with st.expander("View Full Raw Analysis"):
                        st.json(analysis_result)

                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
