from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.conf import settings

from .forms import UploadFileForm
from .savefile import handle_uploaded_file

# Create your views here.
def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'ddl/upload.html') 


def finish(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
   return HttpResponse("Finish")


def todo(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
   return HttpResponse("todo")

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            ER = handle_uploaded_file(request.FILES['File'])
            print '\n\n\n\n'
            print ER
            print '\n\n\n\n'
            # print(request.FILES['File'])
            check_values = request.POST.getlist('Options')
            # print(check_values)
            if u'1' in check_values:
                if u'2' in check_values:
                    return HttpResponseRedirect('/ddl/finish')
                else:
                    return HttpResponseRedirect('/ddl/todo')
            else:
                if u'2' in check_values:
                    return HttpResponseRedirect('/ddl/todo')
                else:
                    return HttpResponseRedirect('/ddl/todo')
                
    else:
        form = UploadFileForm()
    return render(request, 'ddl/upload.html', {'form': form})