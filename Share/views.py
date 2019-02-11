# coding=gbk
from django.shortcuts import render
from django.views.generic import View
from .models import Upload
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect,HttpResponse
import random
import string
import json
import os
import datetime


class HomeView(View):
    def get(self,request):
        print("get request come")
        return render(request,"base.html",{})

    def post(self,request):
        print("post request come")
        if request.FILES:
            file = request.FILES.get("file")
            name = file.name
            path='static/file/'+name
            if os.path.exists(path):
                print(str(path)+"  exists.")
                file_exists_code='1234'
                return HttpResponsePermanentRedirect("/my/" + file_exists_code + "/")
            else:
                print(str(path)+"  no exists.")
                size = int(file.size)
                with open('static/file/'+name,'wb')as f :
                    f.write(file.read())
                code = ''.join(random.sample(string.digits, 8))
                from django.utils import timezone
                u = Upload(
                    path = 'static/file/'+name,
                    name=name,
                    Filesize=size,
                    code = code,
                    PCIP=str(request.META['REMOTE_ADDR']),
                    Datatime=timezone.now(),
                )
                print("u values="+str(type(u)))
                print("timezone.now="+str(timezone.now()))
                u.save()
            # ���µ�����һ��urls�ַ���  views���Ե���htmlģ��Ҳ���Ե���urls�ַ���
            return HttpResponsePermanentRedirect("/s/"+code+"/")


class DisplayView(View):
    def get(self,request,code):
        u = Upload.objects.filter(code=str(code))
        if u :
            for i in u :
                i.DownloadDocount +=1
                i.save()
        return render(request,'content.html',{"content":u})


class DisplayView_detail(View):
    def get(self,request,code):
        u = Upload.objects.filter(code=str(code))
        if u :
            return render(request,'content_detail.html',{"content":u})
        else:
            print("code is not exist,ERROR")


class MyView(View):
    def get(self,request):
        IP = request.META['REMOTE_ADDR']
        print("your ip address is " + str(IP))
        # ÿ�μ�������ʾ���еļ�¼ ���ڸ���ip��ַ����
        u = Upload.objects.all()
        # u = Upload.objects.filter(PCIP=str(IP))
        for i in u :
            i.DownloadDocount +=1
            i.save()
        return render(request,'content.html',{"content":u})


class Re_MyView(View):
    def get(self,request,code):
        IP = request.META['REMOTE_ADDR']
        print("your ip address is " + str(IP))
        # ÿ�μ�������ʾ���еļ�¼ ���ڸ���ip��ַ����
        u = Upload.objects.all()
        # u = Upload.objects.filter(PCIP=str(IP))
        return render(request,'content.html',{"content":u,"exists":'true'})


class SearchView(View):
    def get(self,request):
        search_filename = request.GET.get("kw")
        print("search_filename="+str(search_filename))
        # ����ֶ�ģ����ѯ�� �����е��»�����˫�»��ߣ�˫�»���ǰ���ֶ�����˫�»��ߺ������icontains��contains, �������Ƿ��Сд���У������ǻ����˼
        # icontains�����ִ�Сд contains���ִ�Сд
        u = Upload.objects.filter(name__icontains=str(search_filename))
        print("len(u)"+str(len(u)))
        data = {}
        if u :
            for i in range(len(u)):
                u[i].DownloadDocount +=1
                u[i].save()
                data[i]={}
                data[i]['download'] = u[i].DownloadDocount
                data[i]['filename'] = u[i].name
                data[i]['id'] = u[i].id
                data[i]['ip'] = str(u[i].PCIP)
                data[i]['size'] = u[i].Filesize
                data[i]['time'] = str(u[i].Datatime.strftime('%Y-%m-%d %H:%M:%S'))
                data[i]['key'] = u[i].code
        return HttpResponse(json.dumps(data),content_type="application/json")

class delete_file(View):
    def get(self, request,code):
        print("code="+str(code))
        u = Upload.objects.filter(code=str(code))
        file_path=""
        if u:
            file_path=(u[0].path).encode('utf8')
        print("file_path=" + str(file_path))
        self.delete_file(file_path,code)
        IP = request.META['REMOTE_ADDR']
        print("your ip address is " + str(IP))
        # u = Upload.objects.filter(PCIP=str(IP))
        return HttpResponseRedirect(reverse('MY'))
        # return render(request, 'content.html', {"content": u})

    def delete_file(self,file_path,code):
        if os.path.exists(file_path):
            # ɾ���ļ�����ʹ���������ַ�����
            os.remove(file_path)
            print("%s delete completed" % file_path)
            Upload.objects.filter(code=str(code)).delete()
            # os.unlink(my_file)
        else:
            print('no such file:%s' % file_path)



# Create your views here.
