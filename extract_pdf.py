import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

if __name__ == "__main__":
    pdf_path = "DigitizationSolution_VirSoftech_07Nov2025.pdf"
    text = extract_text_from_pdf(pdf_path)
    
    # Save to text file
    with open("document_content.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("PDF content extracted successfully!")
