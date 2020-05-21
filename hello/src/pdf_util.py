import io
import os

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from PyPDF2 import PdfFileReader

import logging

logger = logging.getLogger(__name__)


def convert_pdf_to_txt(path):
    logger.info('converting pdf to text... ALL AT ONCE')

    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)



    fp.close()
    device.close()
    text = retstr.getvalue()
    retstr.close()
    conversion_status = 'Conversion Complete'
    logger.info(conversion_status)
    result = {
        'pdf' : text,
        'conversion_status' : conversion_status
    }
    return text

def convert_pdf_to_txt_in_parts(path, start_page=0):

    page_increment = 2
    finish = False
    total_pages = get_total_pages(path)
    total_pages = 7
    start_page = int(start_page)
    end_page = min(start_page + page_increment, total_pages)
    if end_page == total_pages:
      finish = True

    '''logger.info(f'converting pdf to text in parts ({page_increment} pages at a time)...')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True

    pagenos = set(range(start_page, end_page))

    logger.info(f'loading page nos : {pagenos}')

    for index, page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True)):
        print('+============================+\n\n')
        print(f'page_index : {index + start_page}')
        print('+============================+\n\n')
        interpreter.process_page(page)



    fp.close()
    device.close()
    text = retstr.getvalue()
    retstr.close()
    '''

    text = ''
    with open(path, mode='rb') as f:
      for page_no in range(start_page, end_page):
        reader = PdfFileReader(f)
        page = reader.getPage(page_no)
        text = text + '\n' + page.extractText()

    # create temp file if not exists
    temp_file_path = get_filename_without_extension(path) + '.temp'
    temp_file = open(temp_file_path, 'a+')

    # append value to temp file
    logger.info(f'writing temp file : {temp_file_path}')
    temp_file.write(text)
    temp_file.close()
    logger.info(f'closing temp file.')

    conversion_status = f'Conversion : {round(start_page/total_pages * 100, 2)}%'
    logger.info(f'conversion_status : {conversion_status}')
    result = {}

    if not finish:
        start_page = end_page
        result = {
        'path' : path,
        'start_page' : start_page,
        'conversion_status' : conversion_status
        }
    else:
        conversion_status = 'Conversion Complete'
        logger.info(conversion_status)
        text = ''
        with open(temp_file_path, 'r') as temp_file:
            text = temp_file.read()
        # delete temp file
        os.remove(temp_file_path)
        result = {
          'pdf' : text,
          'conversion_status' : conversion_status
        }

    return result

def get_total_pages(pdf_path):
    pdf = PdfFileReader(open(pdf_path,'rb'))
    return int(pdf.getNumPages())

def get_filename_without_extension(file_path):
    file_basename = os.path.basename(file_path)
    filename_without_extension = file_basename.split('.')[0]
    return filename_without_extension
