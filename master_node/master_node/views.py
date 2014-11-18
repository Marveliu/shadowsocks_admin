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
from master_node.models import *
from django.contrib import auth
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _

from django.shortcuts import render
from django import http

# Create your views here.


    
    
def index(request):
    return render_to_response('index.html', 
                                        {
                                           # 'user':request.user,
                                        },
                                        context_instance=RequestContext(request,)
                            )


class EditPassForm(forms.Form):
    username = forms.CharField(max_length=100,label=u'用户名')
    oldpass = forms.CharField(max_length=100,label=u'旧密码')
    newpass = forms.CharField(max_length=100,label=u'新密码')
    newpass2 = forms.CharField(max_length=100,label=u'重复新密码')

    def clean_oldpass(self):        
        username = self.cleaned_data['username']
        oldpass = self.cleaned_data['oldpass']
        if auth.authenticate(username=username, password=oldpass) == None:
            raise forms.ValidationError(u"原始密码错误!")
        return oldpass
    def clean_newpass(self):        
        newpass = self.cleaned_data['newpass']
        if len(newpass)<5:
            raise forms.ValidationError(u"密码太短了，请大于5位!")
        return newpass
        
    def clean_newpass2(self):
        newpass = self.cleaned_data.get('newpass','')
        newpass2 = self.cleaned_data['newpass2']
        if newpass =='':    
            return newpass2

        if newpass !=newpass2:
            raise forms.ValidationError(u"两次密码不一致!")
        return newpass2

def logout(request):
    auth.logout(request)
    # Redirect to a success page.
    messages.success(request,message='退出成功。')
    return HttpResponseRedirect("/")
        
@login_required
def profile(request):
    if request.method == 'POST':
        form = EditPassForm(request.POST)
        if form.is_valid() :
            cd = form.cleaned_data
            # 由于 form 鉴定用户的时候省事了，直接使用了表单提交的 username
            # 这里为了安全，再次鉴定并生成 user 对象。
            # 不在专门处理对方伪造 username 的情况了，直接程序出错。
            passuser = auth.authenticate(username=request.user.username, password=cd['oldpass']) 
            passuser.set_password(cd['newpass'])
            passuser.save()
            messages.success(request,message='密码修改成功')
            
        return render_to_response('registration/profile.html', 
                                        {
                                            'profile':get_profile(request.user),
                                            'form':form
                                        },
                                        context_instance=RequestContext(request,)
                            )
    return render_to_response('registration/profile.html', 
                                        {
                                            'profile':get_profile(request.user),
                                        },
                                        context_instance=RequestContext(request,)
                            )





class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    username = forms.RegexField(label=_("Username"), max_length=30,widget=forms.TextInput(attrs={'class':"form-control",'placeholder':"30 个英文字符或更少."}),
        regex=r'^[\w.@+-]+$',
        help_text="必选. 30 个英文字符或更少.",
        error_messages={
            'invalid': "This value may contain only letters, numbers and "
                         "@/./+/-/_ characters."})
    email = forms.RegexField(label="Email", max_length=30,widget=forms.TextInput(attrs={'class':"form-control",'placeholder':"Email"}),
        regex=r'^[^@]+@[^@]+\.[^@]+$',
        help_text="必选.",
        error_messages={
            'invalid': "格式错误，请重新输入."})
    password1 = forms.CharField(label=_("Password"),widget=forms.PasswordInput(attrs={'class':"form-control",'placeholder':"Password"}))
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class':"form-control",'placeholder':"Password"}),
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username","email",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            u'用户名已经被使用了，请更换。',
            code='duplicate_username',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                u'两次密码不相同，请重试。',
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        #user.email = self.email
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
                            
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
                              end_date=datetime.now()+timedelta(days=30))
            profile.save()
            up_user()  # 新建用户后同步ss服务器
            messages.success(request,message=u'注册成功，请登录。')
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", {
        'form': form,
    },
                                        context_instance=RequestContext(request,))

def nodes(request):
    nodes = Node.objects.all()
    return render_to_response("nodes.html", {
        'nodes': nodes,
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



