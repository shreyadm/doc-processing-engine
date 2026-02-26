import os
import streamlit as st
import base64
from groq import Groq
# from dotenv import load_dotenv
from PIL import Image
import io
import json, httpx

# load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="KYC Document Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

api_key = st.secrets["GROQ_API_KEY"]
# Initialize Groq client
client = Groq(
    api_key=api_key,
    http_client=httpx.Client() 
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .success-box {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 20px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 20px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 20px;
        border-radius: 5px;
        border-left: 4px solid #17a2b8;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 KYC Document Analyzer")

# File upload section
st.header("Step 1: Upload Document")
uploaded_file = st.file_uploader(
    "Upload an image (JPG, JPEG, PNG) or PDF file",
    type=["jpg", "jpeg", "png", "pdf"],
    help="Supported formats: JPG, JPEG, PNG, PDF"
)

if uploaded_file:
    # Display uploaded file info
    col1, col2 = st.columns([1, 3])
    with col1:
        st.info(f"**File:** {uploaded_file.name}\n\n**Size:** {uploaded_file.size / 1024:.2f} KB")
    
    # Handle PDF files
    if uploaded_file.type == "application/pdf":
        try:
            from pdf2image import convert_from_bytes
            
            st.info("Converting PDF to image...")
            pdf_pages = convert_from_bytes(uploaded_file.read())
            
            if pdf_pages:
                # Use first page for analysis
                image = pdf_pages[0]
                st.write(f"PDF has {len(pdf_pages)} page(s). Analyzing first page...")
        except ImportError:
            st.error("❌ pdf2image library not found. Install it with: pip install pdf2image pillow")
            st.stop()
    else:
        # Handle image files
        image = Image.open(uploaded_file)
    
    # Display the uploaded image
    with col2:
        st.image(image, caption="Uploaded Document", use_column_width=True)

    # Convert image to RGB mode (removes transparency so it can be saved as JPEG)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    # Convert image to base64 for API
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    base64_image = base64.standard_b64encode(buffered.getvalue()).decode("utf-8")
    
    # Analysis button
    st.header("Step 2: Analyze Document")
    if st.button("🔍 Analyze KYC Document", type="primary", use_container_width=True):
        with st.spinner("Analyzing document with AI..."):
            # Prepare the prompt for KYC analysis
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
    - "person_name": Extracted person's name or null
    - "document_number": ID/License/Passport number or check number if available or null
    - "date_of_birth": if visible or null
    - "issue_date": if visible or null
    - "expiry_date": if visible or null
    - "issuing_authority": e.g., "RTO", "Passport Office", "UIDAI" etc. or null
    - "additional_info": Any other relevant KYC information (e.g., bank name for checks, account holder name, check amount, etc.)
}
5. "image_quality_assessment": {
    - "clarity": (excellent/good/fair/poor) - Overall clarity of the document
    - "blurring_detected": (true/false) - Whether any blurring is present
    - "cropping_issues": (true/false) - Whether document appears cropped
    - "distortion_detected": (true/false) - Whether perspective or other distortions exist
    - "lighting_quality": (excellent/good/fair/poor) - Lighting conditions
    - "contrast": (high/medium/low) - Contrast level
    - "overall_usability": (Suitable/Acceptable/Poor) - Overall usability for KYC verification
    - "quality_notes": Specific observations about image quality
}
6. "kyc_verification_readiness": (Ready/Conditional/Not Ready) - Whether the document is suitable for KYC verification
7. "recommendations": (list) - Any recommendations for document re-submission or actions needed
8. "risk_flags": (list) - Any red flags or concerns detected

Return ONLY valid JSON. Do not include any markdown formatting or code blocks."""

            try:
                # Call Groq API with vision capabilities
                response = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                
                response_text = response.choices[0].message.content
                
                # Parse JSON response
                try:
                    analysis_result = json.loads(response_text)
                except json.JSONDecodeError:
                    # Try to extract JSON from response if it contains extra text
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        analysis_result = json.loads(json_match.group())
                    else:
                        st.error("❌ Failed to parse analysis response")
                        st.stop()
                
                # Display Results
                st.header("Step 3: Analysis Results")
                
                # Document Classification
                st.subheader("📋 Document Classification")
                doc_type = analysis_result.get("document_type", "Unknown")
                is_kyc = analysis_result.get("is_kyc_document", False)
                confidence = analysis_result.get("confidence_level", "Unknown")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if is_kyc:
                        st.markdown(f'<div class="success-box"><strong>✅ Valid KYC Document</strong><br><br>Type: <strong>{doc_type}</strong></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box"><strong>❌ Not a KYC Document</strong><br><br>Detected as: <strong>{doc_type}</strong></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="info-box"><strong>Confidence Level</strong><br><br><strong>{confidence.upper()}</strong></div>', unsafe_allow_html=True)
                
                with col3:
                    readiness = analysis_result.get("kyc_verification_readiness", "Unknown")
                    if readiness == "Ready":
                        color = "success-box"
                        emoji = "✅"
                    elif readiness == "Conditional":
                        color = "warning-box"
                        emoji = "⚠️"
                    else:
                        color = "error-box"
                        emoji = "❌"
                    st.markdown(f'<div class="{color}"><strong>{emoji} Verification Status</strong><br><br><strong>{readiness}</strong></div>', unsafe_allow_html=True)
                
                # Extracted Details
                st.subheader("👤 Extracted Details")
                extracted = analysis_result.get("extracted_details", {})
                
                details_col1, details_col2 = st.columns(2)
                with details_col1:
                    st.write("**Basic Information:**")
                    if extracted.get("person_name"):
                        st.write(f"📝 **Name:** {extracted.get('person_name')}")
                    if extracted.get("date_of_birth"):
                        st.write(f"📅 **Date of Birth:** {extracted.get('date_of_birth')}")
                    if extracted.get("document_number"):
                        st.write(f"🔢 **Document Number:** {extracted.get('document_number')}")
                
                with details_col2:
                    st.write("**Document Dates:**")
                    if extracted.get("issue_date"):
                        st.write(f"📅 **Issue Date:** {extracted.get('issue_date')}")
                    if extracted.get("expiry_date"):
                        st.write(f"📅 **Expiry Date:** {extracted.get('expiry_date')}")
                    if extracted.get("issuing_authority"):
                        st.write(f"🏛️ **Issuing Authority:** {extracted.get('issuing_authority')}")
                
                if extracted.get("additional_info"):
                    st.write("**Additional Information:**")
                    st.write(extracted.get("additional_info"))
                
                # Image Quality Assessment
                st.subheader("🎨 Image Quality Assessment")
                quality = analysis_result.get("image_quality_assessment", {})
                
                qual_col1, qual_col2, qual_col3, qual_col4 = st.columns(4)
                
                with qual_col1:
                    clarity = quality.get("clarity", "Unknown")
                    st.metric("Clarity", clarity.upper())
                
                with qual_col2:
                    lighting = quality.get("lighting_quality", "Unknown")
                    st.metric("Lighting", lighting.upper())
                
                with qual_col3:
                    contrast = quality.get("contrast", "Unknown")
                    st.metric("Contrast", contrast.upper())
                
                with qual_col4:
                    usability = quality.get("overall_usability", "Unknown")
                    st.metric("Usability", usability.upper())
                
                # Quality Issues
                quality_issues = []
                if quality.get("blurring_detected"):
                    quality_issues.append("🫂 Blurring detected")
                if quality.get("cropping_issues"):
                    quality_issues.append("✂️ Document appears cropped")
                if quality.get("distortion_detected"):
                    quality_issues.append("📐 Perspective distortion detected")
                
                if quality_issues:
                    st.warning("**Quality Issues Detected:**")
                    for issue in quality_issues:
                        st.write(f"• {issue}")
                
                if quality.get("quality_notes"):
                    st.info(f"**Quality Notes:** {quality.get('quality_notes')}")
                
                # Recommendations
                recommendations = analysis_result.get("recommendations", [])
                if recommendations:
                    st.subheader("💡 Recommendations")
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
                
                # Risk Flags
                risk_flags = analysis_result.get("risk_flags", [])
                if risk_flags:
                    st.subheader("🚩 Risk Flags")
                    for flag in risk_flags:
                        st.warning(f"⚠️ {flag}")
                
                # Raw JSON for reference
                with st.expander("📊 View Raw Analysis JSON"):
                    st.json(analysis_result)
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.write("Please check your GROQ_API_KEY and try again.")


