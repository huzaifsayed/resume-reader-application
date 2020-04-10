import PyPDF2
from PIL import Image
import camelot
from pprint import pprint


def get_font_table_shape_from_pdf(path):

    image_count = 0

    # Extracting Image Count using PyPDF2
    with open(path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        cond_scan_reader = PyPDF2.PdfFileReader(pdf_file)

        # Extracting Images
        for i in range(0, cond_scan_reader.getNumPages()):
            page0 = cond_scan_reader.getPage(i)
            if '/XObject' in page0['/Resources']:
                xObject = page0['/Resources']['/XObject'].getObject()
                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        image_count +=1
            else:
                print("No image found.")

    print(image_count)

    pdf = PyPDF2.PdfFileReader(path)
    fonts = set()
    embedded = set()
    for page in pdf.pages:
        obj = page.getObject()
        f, e = walk(obj['/Resources'], fonts, embedded)
        fonts = fonts.union(f)
        embedded = embedded.union(e)

    unembedded = fonts - embedded
    clean_fonts = [remove_cruft(s) for s in fonts]
    font_style = ', '.join(sorted(list(clean_fonts)))
    print(fonts)

    return {
                'font_style': font_style, 
                # 'font_size': font_size, 
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