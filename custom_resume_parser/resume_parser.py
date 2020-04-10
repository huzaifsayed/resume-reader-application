#######################################################
# Imports
#######################################################
import io
import re
import os
import docx2txt
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import spacy
from spacy.matcher import Matcher
import pandas as pd
from nltk.corpus import stopwords


#######################################################
# Extracting Docx File
#######################################################

def extract_text_from_doc(doc_path):
    temp = docx2txt.process(doc_path)
    total_lines_docx = temp.count('\n')
    text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
    full_text = ' '.join(text)
    return ' '.join(text), total_lines_docx


#######################################################
# Reading PDF File
#######################################################

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        # iterate over all pages of PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # creating a resoure manager
            resource_manager = PDFResourceManager()
            
            # create a file handle
            fake_file_handle = io.StringIO()
            
            # creating a text converter object
            converter = TextConverter(
                                resource_manager, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )

            # creating a page interpreter
            page_interpreter = PDFPageInterpreter(
                                resource_manager, 
                                converter
                            )

            # process current page
            page_interpreter.process_page(page)
            
            # extract text
            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()


#######################################################
# Extracting Name
#######################################################

# load pre-trained model
nlp = spacy.load('en_core_web_sm')
# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    for entity in nlp_text.ents:
        if entity.label_ == 'PERSON':
            return entity.text


#######################################################
# Extracting Mobile Number
#######################################################

def extract_mobile_number(text):
    phone = re.findall(re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'), text)
    
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number

#######################################################
# Extracting Email
#######################################################

def extract_email(email):
    email = re.findall(re.compile(r'[\w\.-]+@[\w\.-]+'), email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return Non

#######################################################
# Extracting Linkedin URL
#######################################################

def extract_linkedin_url(url):
    url = re.findall(re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'), url)
    if url:
        try:
            for index, item in enumerate(url):
                if 'linkedin' in item:
                    return url[index].split()[index].strip(';')
            return Non
        except IndexError:
            return Non

#######################################################
# Extracting Skills
#######################################################


# load pre-trained model
nlp = spacy.load('en_core_web_sm')

def extract_skills(resume_text):
    nlp_text = nlp(resume_text)
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    # reading the csv file
    data = pd.read_csv("custom_resume_parser/skills.csv") 
    # extract values
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    # check for bi-grams and tri-grams (example: machine learning)
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    print(skillset)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

#######################################################
# Extracting Education
#######################################################

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

# Grad all general stop words
STOPWORDS = set(stopwords.words('english'))

# Education Degrees
EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S', 
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
        ]

def extract_education(resume_text):
    nlp_text = nlp(resume_text)
    # Sentence Tokenizer
    nlp_text = [sent.string.strip() for sent in nlp_text.sents]
    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index + 1]
    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return education


#######################################################
# Extracting Education
#######################################################

class CustomResumeParser:

    def get_extracted_data(path):

        file_name, file_extension = os.path.splitext(path)

        if file_extension == '.docx':
            # calling above function and extracting text - DOCX
            text_docx, total_lines_docx = extract_text_from_doc(path)

            # Details from docx file
            name = extract_name(text_docx)
            mobile_number = extract_mobile_number(text_docx)
            email = extract_email(text_docx)
            linkedin_url = extract_linkedin_url(text_docx)
            skills = extract_skills(text_docx)
            education = extract_education(text_docx)
            skills_str = ', '.join(skills)
            education_str = ', '.join(education)

            # Return in Dictionary Form - Docx.
            return {
                    'name': name, 
                    'mobile_number': mobile_number, 
                    'email': email,
                    'linkedin_url': linkedin_url,
                    'skills': skills_str,
                    'education': education_str,
                    'doc_total_lines': total_lines_docx,
                    'doc_total_characters': len(text_docx),
                    'doc_total_words': len(text_docx.split()),
                }
            

        elif file_extension == '.pdf':
            # calling above function and extracting text - PDF
            text_pdf = ''
            for page in extract_text_from_pdf(path):
                text_pdf += ' ' + page

            # Details from pdf file
            name = extract_name(text_pdf)
            mobile_number = extract_mobile_number(text_pdf)
            email = extract_email(text_pdf)
            linkedin_url = extract_linkedin_url(text_pdf)
            skills = extract_skills(text_pdf)
            education = extract_education(text_pdf)
            skills_str = ', '.join(skills)
            education_str = ', '.join(education)

            # Return in Dictionary Form - PDF.
            return {
                    'name': name, 
                    'mobile_number': mobile_number, 
                    'email': email,
                    'linkedin_url': linkedin_url,
                    'skills': skills_str,
                    'education': education_str,
                    'doc_total_lines': text_pdf.count('\n'),
                    'doc_total_characters': len(text_pdf),
                    'doc_total_words': len(text_pdf.split()),
                }




