from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import Http404
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Greeting
from .forms import PatentForm
from .src.patent_extractor import convert_patent_pdf
from .src.pdf_util import get_filename_without_extension

import logging
import os
import datetime
import pytz
import json

import requests
from background_task import background

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    logger.info('teste ererrror')
    return HttpResponse('Hello from Python!')
    # return simple_upload(request)
    # return render(request, "index.html")

def testcall(request):
   #Get the variable text
   text = request.POST['text']
   #Do whatever with the input variable text
   response = text + ":)"
   #Send the response
   return HttpResponse(response)

def teapot(request):
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>')

def upload(request):
    if request.method == 'POST':
        logger.info('uploading file and starting pdf conversion')
        patentInfo = PatentForm(request.POST, request.FILES)
        if patentInfo.is_valid():
            filepath = handle_uploaded_file(request.FILES['file'])
            statusInfo = 'File Uploaded. Please Wait, conversion may take a few minutes..'
            statusFlag = 'U'
            uploadComplete = True
            conversionComplete = False
            renderDict = {
                'form' : patentInfo,
                'statusInfo' : statusInfo,
                'statusFlag' : statusFlag,
                'filepath' : filepath
            }
            return render(request,"upload_doc.html", renderDict)
    else:
        return loadFreshPage(request)


def convertFileToCsv(request):
    logger.info('converting pdf to csv...')
    filepath = request.POST['filepath']
    start_page = request.POST['start_page']
    logger.info('======================')
    logger.info('======================')
    logger.info(f'filepath = {filepath}')
    logger.info(f'start_page = {start_page}')
    logger.info('======================')
    logger.info('======================')
    result = convert_patent_pdf(filepath, parts=True, start_page=start_page)
    if result['conversion_status'] == 'Conversion Complete':
        csv_filepath = result['csv_filepath']
        # excel_filepath = result['excel_filepath']
        # if os.path.exists(csv_filepath) and os.path.exists(excel_filepath):
        if os.path.exists(csv_filepath):
            logger.info('csv file path exists')
            with open(csv_filepath, 'r') as fh:
                data = fh.read()
                filename = os.path.basename(csv_filepath)
                # response = HttpResponse(fh.read(), content_type='text/csv')
                # response['Content-Disposition'] = 'inline; filename=' + os.path.basename(csv_filepath)
                logger.info('returning excel response')
                renderDict = {
                    'data' : data,
                    'statusFlag' : 'D',
                    'filename' : filename
                }
                json_data = json.dumps(renderDict)
                return HttpResponse(json_data, content_type="application/json")
        else:
            logger.info('csv file doesnt path exists')
            renderDict = {
                'statusInfo' : 'Some problem occured in downloading file',
                'statusFlag' : 'E',
            }
            json_data = json.dumps(renderDict)
            return HttpResponse(json_data, content_type="application/json")
    else:
        logger.info('loading intermediate page for file conversion..')
        patentInfo = PatentForm()
        statusInfo = result['conversion_status']
        path = result['path']
        start_page = result['start_page']
        uploadComplete = True
        conversionComplete = False
        statusFlag = 'C'
        renderDict = {
            'statusInfo' : statusInfo,
            'statusFlag' : statusFlag,
            'start_page' : start_page,
            'filepath' : path
        }
        json_data = json.dumps(renderDict)
        return HttpResponse(json_data, content_type="application/json")
        # return render(request, "upload_doc.html", renderDict)

def loadFreshPage(request):
    logger.info('loading fresh upload page')
    patentInfo = PatentForm()
    statusInfo = 'Please upload file or paste file url..'
    uploadComplete = False
    conversionComplete = False
    statusFlag = 'S'
    renderDict = {
        'form' : patentInfo,
        'statusInfo' : statusInfo,
        'statusFlag' : statusFlag
    }
    return render(request,"upload_doc.html", renderDict)

def handle_uploaded_file(f):
    datetime_timestamp = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y_%H%M%S")
    filepath = 'hello/static/uploads/'+ get_filename_without_extension(f.name) + '_' + datetime_timestamp + '.pdf'
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    logger.info('File upload complete')
    return (filepath)


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
