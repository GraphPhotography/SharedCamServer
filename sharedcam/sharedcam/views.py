from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render_to_response, render
from django.template import RequestContext
from django.db import connection, transaction
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
import json
import hashlib
from django.utils import timezone
from datetime import datetime
from django.db.models import Max
from django.utils.dateformat import format
from django.contrib.auth import logout as auth_logout

from models import *
from forms import *


def index(request):
    photos = HashPhoto.objects.all().exclude(hidden=True).order_by('-date_uploaded')
    if photos:
        newest_photo_hash = photos[0].hexdigest
    else:
        newest_photo_hash = None

    return render_to_response('index.html', locals(), RequestContext(request))

def login(request):
    return render_to_response('login.html', locals(), RequestContext(request))

def logout(request):
    auth_logout(request)
    return redirect('index')

def photos(request):
    photos = HashPhoto.objects.all().order_by('-date_uploaded')
    description = "All photos sorted by date"
    if photos:
        newest_photo_hash = photos[0].hexdigest
    else:
        newest_photo_hash = None
    return render_to_response('photos.html', locals(), RequestContext(request))

def photos_by_tag(request, tag):
    photos = HashPhoto.objects.filter(tags__text=tag).exclude(hidden=True).order_by('-date_uploaded')
    description = "Photos of #" + tag + ""
    if photos:
        newest_photo_hash = photos[0].hexdigest
    else:
        newest_photo_hash = None
    return render_to_response('photos.html', locals(), RequestContext(request))

def photo(request, hash):
    photo = HashPhoto.objects.get(hexdigest=hash)
    return render_to_response('single_photo.html', locals(), RequestContext(request))

def recent_content(request, hash=None):
    if hash:
        hp = HashPhoto.objects.get(hexdigest=hash)
        photos = HashPhoto.objects.filter(date_uploaded__gt=hp.date_uploaded).exclude(hidden=True).order_by('-date_uploaded')
    else:
        photos = HashPhoto.objects.exclude(hidden=True).order_by('-date_uploaded')

    if request.GET.get('tag'):
        tag = request.GET.get('tag')
        photos = photos.filter(tags__text=tag)


    if photos:
        max_photo = photos[0]
        newest_photo_hash = max_photo.hexdigest

    if request.GET.get('json'):
        json_photos = [p.simple() for p in photos]
        return JsonResponse(json_photos, safe=False)
    else:
        return render_to_response('grid.html', locals(), RequestContext(request))

def flag(request):
    res = None
    if request.POST.get('content_id'):
        content_id = request.POST.get('content_id')
        print "django got instruction to flag content id", content_id
        
        content = HashPhoto.objects.get(hexdigest=content_id)
        content.hidden = True
        content.save()
        res = {"content_id": content_id, "flagged": content.hidden}

    return JsonResponse(res, safe=False)

def testphoto_page(request):
    form_result = "Nothing happened with the form"

    if request.method == 'POST':
        form_result = "post: "

        form = HashPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form_result += " photo form saved from manual upload"
            form.save(request.POST)
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = HashPhotoForm()

    server = "http://" + settings.DEPLOY_SERVER

    hashphotos = HashPhoto.objects.order_by('-date_uploaded')
    return render_to_response('testphoto.html', locals(), RequestContext(request))

@csrf_exempt
def process_photo(request):
    # curl -F "photo=@7468481122_e1466490fa_m.jpg" -F "tag_string=jpeg" 127.0.0.1:8000/add
    response_data = {}
    form_result = "Nothing happened with the form"

    if request.method == 'POST':
        form_result = "post: "

        form = HashPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form_result += " photo form saved "
            new_photo = form.save(request.POST)
            base_url = request.build_absolute_uri().replace("/add", "")
            response_data["hash"] = new_photo.hexdigest
            response_data["path"] = new_photo.url()
            response_data["viewing_url"] = base_url + reverse('sharedcam.views.photo', args=(new_photo.hexdigest,))
            response_data["url"] = base_url + new_photo.url()
        else:
            form_result = "form is invalid"

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HashPhotoForm()

    response_data["form_result"] = form_result
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def fake_sharecams(request):
    response_data = [
        {  
            "state": 1, 
            "lastTime": 1429047188.507, 
            "room": "rm1234", 
            "name": "bobby",
            "tags": ["ftmason", "iatfest", "robot"]
        },
        {  
            "state": 1, 
            "lastTime": 1429049188.507, 
            "room": "rm5678", 
            "name": "GildaTheGuide",
            "tags": ["cats", "robot"]
        },
        ]
    return HttpResponse(json.dumps(response_data), content_type="application/json")