import re
import pandas as pd
import datetime
import pytz
from .pdf_util import *

import logging
import pyexcel
import csv

logger = logging.getLogger(__name__)

# read pdf and convert to text

def convert_patent_pdf(filename, parts=False, start_page=0):
    pdf_filename = filename
    result = None
    if parts:
        result = convert_pdf_to_txt_in_parts(pdf_filename, start_page)
    else:
        result = convert_pdf_to_txt(pdf_filename)

    if result['conversion_status'] == 'Conversion Complete':

        pdf_text = result['pdf']

        # pdf text cleaning
        pdf_text_processed = re.sub('\n', '', pdf_text)
        pdf_text_processed = re.sub('\s+', ' ', pdf_text_processed)
        pdf_text_processed = re.sub(',', '‚', pdf_text_processed)

        # attriburte extraction regex
        app_no_regex = r'\(21\)\sApplication No\.\s*([\d]+)'
        applicant_regex_old = r'\(71\)\s*Name of Applicant\s*\:\s*([\d]+(.(?!72\)))*)'
        applicant_regex = r'\(71\)\s*Name of Applicant\s*\:\s*[\d]+\)((.(?!2\))(?!72\)))*)'

        # extract attributes
        logger.info('extracting attributes..')
        application_nos = re.findall(app_no_regex, pdf_text_processed)
        applicants = re.findall(applicant_regex, pdf_text_processed)
        applicants = [appl[0] for appl in applicants]

        logger.info('exporting csv file')

        df = pd.DataFrame({'Application No.' : application_nos, 'Name of Applicants' : applicants}).drop_duplicates(subset='Application No.', keep="first")

        # export file and make available for download
        datetime_timestamp = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y_%H%M%S")
        csv_filename = ('hello/static/uploads/patent_applications_data_' + datetime_timestamp + '.csv')
        df.to_csv(csv_filename, index=False, quoting=csv.QUOTE_NONE)
        excel_filename = ('hello/static/uploads/patent_data_' + datetime_timestamp + '.xlsx')
        # sheet = pyexcel.get_sheet(file_name=csv_filename, delimiter=",")
        # sheet.save_as(excel_filename)
        result['csv_filepath'] = csv_filename
        result['excel_filepath'] = excel_filename

    return result
