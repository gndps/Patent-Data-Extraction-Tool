import re
import pandas as pd
import datetime
import pytz
from .pdf_util import convert_pdf_to_txt

import logging

logger = logging.getLogger(__name__)

# read pdf and convert to text

def convert_patent_pdf(filename):
    pdf_filename = filename
    pdf_text = convert_pdf_to_txt(pdf_filename)

    # pdf text cleaning
    pdf_text_processed = re.sub('\n', ' ', pdf_text)
    pdf_text_processed = re.sub('\s+', ' ', pdf_text_processed)

    # attriburte extraction regex
    app_no_regex = r'\(21\)\sApplication No\.\s*([\d]+)'
    applicant_regex = r'\(71\)\s*Name of Applicant\s*\:\s*([\d]+(.(?!72\)))*)'

    # extract attributes
    logger.info('extracting attributes..')
    application_nos = re.findall(app_no_regex, pdf_text_processed)
    applicants = re.findall(applicant_regex, pdf_text_processed)

    logger.info('exporting csv file')

    df = pd.DataFrame({'application_no' : application_nos, 'name of applicants' : applicants})

    # export file and make available for download
    datetime_timestamp = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y_%H:%M:%S")
    csv_filename = ('hello/static/uploads/patent_applications_data_' + datetime_timestamp + '.csv')
    df.to_csv(csv_filename)
    return csv_filename
