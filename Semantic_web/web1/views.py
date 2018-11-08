from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from web1 import models
from django.views.decorators.cache import cache_page
from django.db.models.signals import post_save

# Create your views here.


def Auth(func):
    def inner(request,*args,**kwargs):
        if request.session.get("is_login",None):
            return func(request, *args, **kwargs)
        else:
            return redirect('/login/')
    return inner

'''cache保存时间为60s'''
@cache_page(60)
def login(request):
    if request.method=='GET':
        return render(request,'login.html')

    if request.method=='POST':
        username=request.POST.get("email")
        pwd=request.POST.get("password")
        try:
            models.Account.objects.filter(user=username).get(password=pwd)
            print("登录成功")
            request.session["username"]=username
            request.session["is_login"]=True

            return redirect('/index/')

        except:
            print("密码错误")
            return render(request,'login.html')

@Auth
def index(request):
    return render(request,'index.html')
    # if request.session.get('is_login',None):
    #     return render(request,'index.html',{'username': request.session['username']})
    # else:
    #     return redirect('/login/')


from django import forms
'''widgets是form的插件'''
from django.forms import widgets
from django.forms import fields

class FM(forms.Form):
    # user=fields.CharField(
    #     error_messages={"required":"用户名不能为空"},
    #     label="用戶名"
    # )

    user=fields.EmailField(
        error_messages={"required": "邮箱不能为空", "invalid": "邮箱不符合规范"},

    )
    password=fields.CharField(
        max_length=16,
        min_length=6,
        error_messages={"required":"密码不能为空","max_length":"长度不能超过16个字符","min_length":"长度不能短于6个字符"},
        label="密码 ",
        widget=widgets.PasswordInput(attrs={"class":"c2"})

    )

    # mail=fields.EmailField(
    #     error_messages={"required":"邮箱不能为空","invalid":"邮箱不符合规范"}
    # )

    # print(user)
    # print(pwd)
    # print(mail)

def sign_up(request):
    if request.method=="GET":
        obj=FM()
        return render(request,'sign_up.html',{"obj":obj})

    if request.method=="POST":
        obj=FM(request.POST)
        r1=obj.is_valid()

        if r1:
            print(obj.cleaned_data.get('user')) #获取user
            # info="新增一条用户数据{}".format(obj.user)
            print(type(obj.cleaned_data))
            # post_save.send(sender="Account",info=obj.cleaned_data)
            print(132)
            try:
                models.Account.objects.create(**obj.cleaned_data)

                return redirect('/temp/')
            except:
                return HttpResponse("输入的邮箱已存在")
            # return HttpResponse("200")
        else:
            # print(obj.errors.as_json())
            print(obj.errors)
            return render(request,'sign_up.html',{"obj":obj})

def temp(request):

    return render(request,'temp.html')


def logout(request):
    request.session["is_login"] = False
    return redirect('/login/')