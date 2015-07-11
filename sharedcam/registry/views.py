from django.shortcuts import render
from django.template import RequestContext
#from socketio import socketio_manage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
#from jumpchat.socketio_ns import V1Namespace
import string
import random
import logging
#from .models import Room
from datetime import date
from django.conf import settings
#import jumpchat.utils
import json
import os

@csrf_exempt
def reg_remove(request):
    import ShareCamReg
    q = request.GET
    params = {'room': '', 'type': 'random', 'serverName': settings.JUMPCHAT_SERVER, 'apiKey': settings.API_KEY  }
    jsonStr = ShareCamReg.regRemove(request, params, q)
    return HttpResponse(jsonStr, content_type="application/json")

@csrf_exempt
def reg_connect(request):
    import ShareCamReg
    q = request.GET
    params = {'room': '', 'type': 'random', 'serverName': settings.JUMPCHAT_SERVER, 'apiKey': settings.API_KEY  }
    url = ShareCamReg.regConnect(request, params, q)
    return HttpResponseRedirect(url)

@csrf_exempt
def reg_query(request):
    import ShareCamReg
    q = request.GET
    params = {'room': '', 'type': 'random', 'serverName': settings.JUMPCHAT_SERVER, 'apiKey': settings.API_KEY  }
    jsonStr = ShareCamReg.regQuery(request, params, q)
    return HttpResponse(jsonStr, content_type="application/json")

@csrf_exempt
def reg_config(request):
    q = request.GET
    config = {'type': 'random', 'serverName': settings.JUMPCHAT_SERVER }
    if "name" in q:
        name = q['name']
        path = "registry/config/%s.json" % (name,)
        config['name'] = name
        try:
            cfg = json.loads(file(path).read())
            for key in cfg:
                config[key] = cfg[key]
            config['configPath'] = path
        except:
            pass
    jsonStr = json.dumps(config)
    return HttpResponse(jsonStr, content_type="application/json")

@csrf_exempt
def reg(request):
    import ShareCamReg
    template_name='reg.html'
    params = {'room': '', 'type': 'random', 'serverName': settings.JUMPCHAT_SERVER, 'apiKey': settings.API_KEY  }
    jsonStr = ShareCamReg.reg(request, params)
    return HttpResponse(jsonStr, content_type="application/json")

# Post version of reg
@csrf_exempt
def regp(request):
    import ShareCamReg
    params = {'room': '', 'type': 'random', 'serverName': settings.JUMPCHAT_SERVER, 'apiKey': settings.API_KEY  }
    jsonStr = ShareCamReg.regp(request, params)
#    jsonStr = json.dumps({'return_code': 'failed'})
    return HttpResponse(jsonStr, content_type="application/json")
