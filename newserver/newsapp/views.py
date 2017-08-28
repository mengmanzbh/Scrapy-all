# -*- coding: UTF-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from pymongo import MongoClient
import re
from django import forms
from newsapp.models import Account
from django.http import HttpResponseRedirect
from django.contrib import auth
import threading
import time
from bson import json_util as jsonb
from django.core.mail import send_mail
import pika
from django.shortcuts import render
# Create your views here.


def data(request):
    client = MongoClient()
    client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
    db = client.admin
    content = db.sina.find({},{"content":1,"_id":0}).sort([("_id",-1)]).limit(1)
    print(type(content))
    jsondata = jsonb.dumps(content)
    dicdata = jsonb.loads(jsondata)
    print(type(dicdata))
    return HttpResponse(dicdata)

class UserForm(forms.Form):
    username = forms.CharField(label='账号',max_length=50)
    password = forms.CharField(label='密码',widget=forms.PasswordInput())

def index(request):
    client = MongoClient()
    client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
    db = client.admin
    res = db.sina.find({},{"source":1,"time":1,"content":1,"_id":0}).sort([("_id",-1)]).limit(15)
    return render(request, 'index.html', {'TutorialList': res})

def search(request):
    keyword = request.GET['keyword']
    print(keyword)
    client = MongoClient()
    client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
    db = client.admin
    if keyword.strip()== "":
       res = db.sina.find({},{"source":1,"time":1,"content":1,"_id":0}).sort([("_id",-1)]).limit(5)
    else:
       res = db.sina.find({'content':{'$regex':keyword}})
    return render(request, 'index.html', {'TutorialList': res})

def regist(request):
    if request.method == 'POST':
        userform = UserForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            res = Account.objects.get_or_create(username=username,password=password)
            # User.save()
            if res[1]:
                return HttpResponseRedirect("/login")
            else:
                info = "注册失败，请重新注册"
                return render_to_response('fail.html',{'info':info})
    else:
        userform = UserForm()
    # return render_to_response('regist.html',{'userform':userform})
    return render(request, 'regist.html', {'userform':userform})

def update(request):
    content = request.POST['content']
    email = request.POST['email']
    phone = request.POST['phone']
    getusername = request.session['username']
    getpassword = request.session['password']
    user = Account.objects.get(username = getusername,password = getpassword)
    print(user)
    user.content = request.POST['content']
    user.email = email
    user.phone = phone
    user.save()
    # return HttpResponse('关键词定制成功')
    return render(request, 'success.html')

def login(request):
    if request.method == 'POST':
        userform = UserForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            user = Account.objects.filter(username__exact=username,password__exact=password)
            if user:
                request.session['password'] = password
                request.session['username'] = username
                #查询最新数据显示
                client = MongoClient()
                client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
                db = client.admin
                newsdata = db.sina.find({},{"source":1,"time":1,"content":1,"_id":0}).sort([("_id",-1)]).limit(1)

                if user[0].isadministrator == '1':
                    alluser = Account.objects.all()
                    return render(request, 'adminview.html', {'alluser':alluser,'newsdata':newsdata,'username':request.session['username'],'content':user[0].content,'email':user[0].email,'phone':user[0].phone})
                else:
                    return render(request, 'userview.html', {'newsdata':newsdata,'username':request.session['username'],'content':user[0].content,'email':user[0].email,'phone':user[0].phone})
            else:
                info = "用户名或者密码错误，请重新登陆"
                return render_to_response('fail.html',{'info':info})
    else:
        userform = UserForm()
    return render_to_response('login.html',{'userform':userform})

def logout(request):
        del request.session['username']
        del request.session['password']
        return HttpResponseRedirect("/")

#查找总数，判断是否最新记录  
def searchToralCount():
    client = MongoClient()
    client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
    db = client.admin
    totalCount = db.sina.find().count()
    return totalCount

#验证单个关键词函数
def keywordSearch(user,keyword):
    print(keyword)
    client = MongoClient()
    client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
    db = client.admin
    if keyword.strip()== "":
        pass
    else:
        #查找数据库最新记录
        totalCount = searchToralCount()
        res = db.sina.find({"count":totalCount},{"content":1,"_id":0})
        jsondata = jsonb.dumps(res)
        strdata = str(jsonb.loads(jsondata))
        res = strdata.find(keyword)
        if res == -1:
            print("不存在%s:%s关键词"%(user.username,keyword))
        else:
            print("查找到%s:%s关键词"%(user.username,keyword))
            theme = "你的关键词：%s,有了最新消息,请查收" % (keyword)
            send_mail(theme, strdata[14:-3], '15800536717@sina.cn', [user.email])
            print('发邮箱，将改用户添加到记录里面，用作判断')
            print(user.email)
            uodateAccountList(user.email)
    # return strdata[14:-3]
#发邮箱之后更新记录的accountList  
def uodateAccountList(email):
    client = MongoClient()
    client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
    db = client.admin
    totalCount = db.sina.find().count()
    olddata = findAccountList()
    newsdata = olddata+'+'+email
    content = db.sina.update({"count":totalCount},{"$set":{"accountList":newsdata}})
    return content
def findAccountList():
    client = MongoClient()
    client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
    db = client.admin
    totalCount = db.sina.find().count()
    accountList = db.sina.find({"count":totalCount},{"accountList":1,"_id":0})
    accountListdata = jsonb.dumps(accountList)
    accountListdataStr = str(jsonb.loads(accountListdata))
    return accountListdataStr[18:-3]
def userTest(request):
    userList = Account.objects.all()
    AccountList = findAccountList()
    print("AccountList:%s"%(AccountList))
    for user in userList:
         keyword = user.content
         print('------------------------------------------')
         print(user.email)
         #在改调记录里面查找是否有这个用户，有就代表已经发过了
         issended = AccountList.find(user.email)
         if issended == -1:
            print("没有发过邮箱")
            ismore = keyword.find("+")
            #是否包含多个关键词
            if ismore == -1:
                print("只有一个关键词")
                keyword = user.content
                keywordSearch(user,keyword)
            else:
                print("包含多个关键词")
                keywordList = keyword.split("+")
                print(keywordList)
                for k in keywordList:
                    keywordSearch(user,k)
         else:
            print("已经发过邮箱")


    return HttpResponse(AccountList)
def user():
    userList = Account.objects.all()
    AccountList = findAccountList()
    print("AccountList:%s"%(AccountList))
    for user in userList:
         keyword = user.content
         print('------------------------------------------')
         print(user.email)
         #在改调记录里面查找是否有这个用户，有就代表已经发过了
         issended = AccountList.find(user.email)
         if issended == -1:
            print("没有发过邮箱")
            ismore = keyword.find("+")
            #是否包含多个关键词
            if ismore == -1:
                print("只有一个关键词")
                keyword = user.content
                keywordSearch(user,keyword)
            else:
                print("包含多个关键词")
                keywordList = keyword.split("+")
                print(keywordList)
                for k in keywordList:
                    keywordSearch(user,k)
         else:
            print("已经发过邮箱")
