import os
import docx
import PyPDF2

UPLOAD_FOLDER = 'uploads/resumes'

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + '\n'
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text

def extract_text(file_path):
    ext = file_path.split('.')[-1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    else:
        return ""

def clean_and_tokenize(text):
    words = text.lower().replace('\n', ' ').replace('-', ' ').replace('_', ' ')
    tokens = [word.strip('.,;()[]') for word in words.split()]
    return set(tokens)

def calculate_score(resume_text, job_description):
    resume_words = clean_and_tokenize(resume_text)
    job_words = clean_and_tokenize(job_description)
    matched = job_words.intersection(resume_words)
    if not job_words:
        return 0
    return int((len(matched) / len(job_words)) * 100)

def process_resumes(job_description):
    resumes = []
    files = os.listdir(UPLOAD_FOLDER)

    for f in files:
        file_path = os.path.join(UPLOAD_FOLDER, f)
        resume_text = extract_text(file_path)
        score = calculate_score(resume_text, job_description)

        resumes.append({
            "Filename": f,
            "Candidate Name": f.split('.')[0].replace('_', ' ').title(),
            "Overall Rank": score
        })

    return resumes
