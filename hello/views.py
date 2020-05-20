from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Greeting
from .forms import PatentForm
from .src.patent_extractor import convert_patent_pdf

import logging
import os

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
    csv_filepath = convert_patent_pdf(filepath)
    if os.path.exists(csv_filepath):
        logger.info('csv file path exists')
        with open(csv_filepath, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='text/csv')
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(csv_filepath)
            logger.info('returning csv response')
            return response
    else:
        logger.info('csv file doesnt path exists')
        return loadFreshPage(request)

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
    with open('hello/static/uploads/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    logger.info('File upload complete')
    return ('hello/static/uploads/' + f.name)


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
