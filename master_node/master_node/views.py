#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码
import random
import string
from datetime import datetime,timedelta
from django import http
from django import forms
from django.db.models import Q
from django.conf import settings
from master_node.models import *
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator,InvalidPage,EmptyPage
#from django.utils import simplejson 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from master_node.models import *



from django.shortcuts import render
from django import http

# Create your views here.

def GenPassword(length):
    chars=string.ascii_letters+string.digits
    return ''.join([random.choice(chars) for i in range(length)])#

    
    
def index(request):
    return render_to_response('index.html', 
                                        {
                                           # 'user':request.user,
                                        },
                                        context_instance=RequestContext(request,)
                            )
                            
@login_required
def profile(request):
    return render_to_response('registration/profile.html', 
                                        {
                                            'profile':get_profile(request.user),
                                        },
                                        context_instance=RequestContext(request,)
                            )





def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            profile = Profile(user=new_user,
                              sport=8000+new_user.id,
                              spass=GenPassword(10),
                              start_date=datetime.now(),
                              now_date=datetime.now(),
                              end_date=datetime.now()+timedelta(days=10))
            profile.save()
            up_user()  # 新建用户后同步ss服务器
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", {
        'form': form,
    },
                                        context_instance=RequestContext(request,))




def tree(request,id):
    try:
        iid = int(id)
    except: 
        raise http.Http404
    
    p = get_object_or_404(people,id=iid)
    
    
    return render_to_response('tree.html', 
                                        {
                                            'p':p,
                                        },
                                        #context_instance=RequestContext(request,)
                            )

def tree_json(request,id,recursion):
    try:
        iid = int(id)
        recursion = int(recursion)
    except: 
        raise http.Http404
    
    p = get_object_or_404(people,id=iid)
    res = p.recursion_to_dict(recursion)
    
    return HttpResponse(simplejson.dumps(res,ensure_ascii = False))



