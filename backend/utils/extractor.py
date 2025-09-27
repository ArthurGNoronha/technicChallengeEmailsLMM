import PyPDF2

def extractPdf(file_stream):
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    
def extractTxt(file_stream):
    try:
        return file_stream.read().decode('utf-8')
    except Exception as e:
        print(f"Error extracting text from TXT: {e}")
        return None
    
def extractText(file):
    filename = file.filename
    if filename.endswith('.pdf'):
        return extractPdf(file)
    elif filename.endswith('.txt'):
        return extractTxt(file)
    else:
        print("Unsupported file type")
        return None