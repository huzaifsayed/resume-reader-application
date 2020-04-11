import PyPDF2
from PIL import Image


def get_font_table_shape_from_pdf(path):

    image_count = 0
    fonts = set()
    embedded = set()

    # Extracting Image Count using PyPDF2
    with open(path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        cond_scan_reader = PyPDF2.PdfFileReader(pdf_file)

        # Extracting Images
        for i in range(0, cond_scan_reader.getNumPages()):
            page = cond_scan_reader.getPage(i)
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject'].getObject()
                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        image_count +=1

        # Extracting Font
        for page in pdf_reader.pages:
            obj = page.getObject()
            f, e = walk(obj['/Resources'], fonts, embedded)
            fonts = fonts.union(f)
            embedded = embedded.union(e)

    unembedded = fonts - embedded
    clean_fonts = [remove_cruft(s) for s in fonts]
    font_style = ', '.join(sorted(list(clean_fonts)))
    
    font_size = pdf_to_html(path)

    return {
                'font_style': font_style, 
                'font_size': ', '.join(font_size), 
                # 'doc_table': len(document.tables),
                'doc_shapes': image_count,
            }

def remove_cruft(s):
    return s[1:-2]

def walk(obj, fnt, emb):
    if not hasattr(obj, 'keys'):
        return None, None
    fontkeys = set(['/FontFile', '/FontFile2', '/FontFile3'])
    if '/BaseFont' in obj:
        fnt.add(obj['/BaseFont'])
    if '/FontName' in obj:
        if [x for x in fontkeys if x in obj]:
            emb.add(obj['/FontName'])

    for k in obj.keys():
        walk(obj[k], fnt, emb)

    return fnt, emb


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

def pdf_to_html(path):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = HTMLConverter(manager, retstr, laparams=layout)
    filepath = open(path, 'rb')
    interpreter = PDFPageInterpreter(manager, device)

    for page in PDFPage.get_pages(filepath, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    filepath.close()
    device.close()
    retstr.close()
    return text

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

def pdf_to_html(path):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = HTMLConverter(manager, retstr, laparams=layout)
    filepath = open(path, 'rb')
    interpreter = PDFPageInterpreter(manager, device)

    for page in PDFPage.get_pages(filepath, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    filepath.close()
    device.close()
    retstr.close()

    # Write HTML String to file.html
    # f = open("demofile3.html", "wb")
    # f.write(text)
    # f.close()

    font_size = extract_font_table(text)

    return font_size


def extract_font_table(htmlData):
    from bs4 import BeautifulSoup
    import re
    soup = BeautifulSoup(htmlData)
    font_spans = [ data for data in soup.select('span') if 'font-size' in str(data) ]
    font_set = set()
    for i in font_spans:
        fonts_size = re.search(r'(?is)(font-size:)(.*?)(px)',str(i.get('style'))).group(2)
        font_set.add(fonts_size)
    return list(font_set)

