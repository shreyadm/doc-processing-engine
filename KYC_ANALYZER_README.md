# KYC Document Analyzer - Usage Guide

## Overview

The **KYC Document Analyzer** is a Streamlit application powered by Groq's LLAMA 3.2 Vision model. It analyzes document images and PDFs to identify KYC documents, extract relevant information, and assess image quality.

## Features

### 1. Document Upload

- Supports image formats: **JPG, JPEG, PNG**
- Supports document format: **PDF** (converts to image for analysis)
- Displays uploaded document preview

### 2. Document Identification

- Determines if the image is a **legitimate KYC document** or random image
- Identifies document type:
  - Passport
  - Driving License
  - Aadhaar Card
  - Check/Cheque
  - National ID Card
  - Voter ID
  - PAN Card
  - Other ID documents

### 3. KYC Details Extraction

Extracts the following information (when available):

- **Person's Name**: Full name on the document
- **Document Number**:
  - License/Passport number
  - Aadhaar number
  - Check number
  - ID number
- **Date of Birth**: If visible on document
- **Issue Date**: Document issuance date
- **Expiry Date**: Document expiration date
- **Issuing Authority**: Government body or bank
- **Additional Information**:
  - Bank name (for checks)
  - Account holder name
  - Other relevant KYC details

### 4. Image Quality Assessment

Evaluates document quality across multiple dimensions:

- **Clarity**: Sharpness and focus quality (Excellent/Good/Fair/Poor)
- **Lighting Quality**: Document illumination (Excellent/Good/Fair/Poor)
- **Contrast**: Color/grayscale contrast levels (High/Medium/Low)
- **Blurring Detection**: Whether image has motion or focus blur
- **Cropping Issues**: Whether document edges are cut off
- **Perspective Distortion**: Angled or skewed document
- **Overall Usability**: Suitability for KYC verification (Suitable/Acceptable/Poor)

### 5. Verification Readiness

Provides assessment on document suitability:

- **Ready**: Document is suitable for KYC verification
- **Conditional**: Document may be accepted with additional verification
- **Not Ready**: Document needs to be resubmitted

### 6. Recommendations & Risk Flags

- **Recommendations**: Specific actions needed for document improvement
- **Risk Flags**: Any suspicious or problematic observations

## Installation & Setup

### Prerequisites

- Python 3.8+
- Groq API Key (get it from [https://console.groq.com](https://console.groq.com))

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variable

Create a `.env` file in the project root directory:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 3: Run the Application

**Option A: Using the Batch File (Windows)**

```bash
run_kyc_analyzer.bat
```

**Option B: Using Command Line**

```bash
streamlit run kyc_analyzer_app.py
```

The app will launch in your default browser at `http://localhost:8501`

## How to Use

1. **Upload a Document**:
   - Click the file uploader
   - Select an image or PDF file

2. **Preview Document**:
   - Your document will be displayed in the sidebar

3. **Analyze**:
   - Click the "🔍 Analyze KYC Document" button
   - Wait for the AI analysis to complete (typically 10-30 seconds)

4. **Review Results**:
   - Document classification (valid KYC or not)
   - All extracted details
   - Image quality assessment
   - Verification readiness status
   - Recommendations and risk flags

5. **Export**:
   - View raw JSON data using the "View Raw Analysis JSON" expander
   - Take screenshots of results as needed

## Supported KYC Documents

### Government-Issued ID Documents

✅ Passport  
✅ Driving License  
✅ Aadhaar Card  
✅ Voter ID  
✅ National ID Card  
✅ PAN Card  
✅ Passport Copy/Scan

### Financial Documents

✅ Bank Check/Cheque  
✅ Bank Statement  
✅ Passbook

### Other Documents

❌ Random Images (flowers, animals, etc.)  
❌ Screenshots of documents  
❌ Completely illegible documents

## Quality Guidelines

For best results, ensure:

- **Clear Focus**: Document is in sharp focus, not blurry
- **Good Lighting**: Well-lit, no shadows or reflection glare
- **Complete Document**: All edges and corners visible, not cropped
- **Straight Angle**: Document photographed straight on, not at an angle
- **High Resolution**: Minimum 300x300 pixels
- **Good Contrast**: Text clearly visible
- **No Obstruction**: No fingers, markers, or other objects covering document

## Technical Details

### Model Used

- **Groq LLAMA 3.2 90B Vision Preview**
- Fast processing with high accuracy
- Real-time analysis

### Processing Steps

1. Image/PDF upload
2. Base64 encoding for API transmission
3. Vision model analyzes document content
4. JSON response parsing
5. Structured display of results

### Response Time

- Typically 10-30 seconds per document
- Depends on image size and complexity

## Troubleshooting

### Error: "GROQ_API_KEY not found"

**Solution**: Ensure `.env` file exists and contains your API key

```
GROQ_API_KEY=your_actual_key_here
```

### Error: "pdf2image library not found"

**Solution**: Install required packages

```bash
pip install pdf2image pymupdf
```

On Windows, you may also need to install poppler. See: https://github.com/Belval/pdf2image

### Image not uploading

**Solution**: Ensure file format is supported (jpg, jpeg, png, pdf)

### Analysis takes too long

**Solution**: Check internet connection and Groq API availability

### "Failed to parse analysis response"

**Solution**: Try with a different/clearer document image

## Example Use Cases

1. **Bank KYC Verification**
   - Customer submits identity document
   - System extracts details and verifies document quality
   - Automatically flags issues that need manual review

2. **Document Quality Control**
   - Batch processing of uploaded documents
   - Identify poor quality submissions
   - Request document resubmission before manual verification

3. **Information Extraction**
   - Automatically extract DOB, ID numbers, names
   - Populate forms with extracted data
   - Reduce manual data entry errors

## API Costs

Each analysis call uses Groq's API. Check your Groq account dashboard for:

- Current usage
- API credits/billing
- Rate limits

## Privacy & Security

⚠️ **Note**: Document images are sent to Groq's API for analysis.

- Do not use with highly sensitive personal documents if concerned about data transmission
- Use only with documents that need KYC verification
- Ensure compliance with local privacy regulations

## Future Enhancements

Potential improvements:

- Multi-page PDF support (analyze all pages)
- Batch processing (analyze multiple documents)
- Export results to CSV/PDF
- Document confidence scoring
- Fraud detection features
- OCR text extraction
- Document template matching

## Support

For issues or questions:

1. Check Groq API status: https://console.groq.com
2. Verify API key permissions
3. Check internet connection
4. Review error messages in the app

## License & Credits

**Built with**:

- [Streamlit](https://streamlit.io/)
- [Groq API](https://groq.com/)
- [LLAMA 3.2 Vision Model](https://www.llama.com/)
- [Pillow](https://python-pillow.org/)
- [pdf2image](https://github.com/Belval/pdf2image)
