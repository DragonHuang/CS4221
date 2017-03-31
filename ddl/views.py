import pickle
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.conf import settings

from .forms import UploadFileForm
from .forms import ComfirmForm
from .parse import parseXML

from ddlgenerator.DDLGenerator import DDLGenerator

# Create your views here.
def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    return HttpResponseRedirect('/ddl/upload') 


def finish(request):
    file = open('IO/DDL', 'rb')
    DDL = pickle.load(file)
    file.close()

    ddlHtml = ""
    indent = ""

    for ddl in DDL:
        for line in ddl.splitlines():
            if line[-2:] == ");":
                indent = indent[0:-4]
            ddlHtml += indent + line + "###";
            if line[-2:] == " (":
                indent += "****"
            

        ddlHtml += "###";

    return render(request, 'ddl/finish.html',
            {
                'result':str(ddlHtml).rstrip()
            })


def todo(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    return HttpResponse("todo")

def comfirm(request):
    file = open('IO/ER', 'rb')
    ER = pickle.load(file)
    file.close()
    print(ER)
    form = ComfirmForm()
    return render(request, 'ddl/comfirm.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            ER = parseXML(request.FILES['File'])
            
            check_values = request.POST.getlist('Options')
            ddlObject = DDLGenerator()
            if u'1' in check_values:
                smart = True
            else:
                smart = False
            
            if u'2' in check_values:
                ER = ddlObject.fill_missing_type(ER, smart, 'psql')

                with open('IO/ER', 'wb') as output:
                    pickle.dump(ER, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                return HttpResponseRedirect('/ddl/comfirm')
            else:
                ER = ddlObject.fill_missing_type(ER, smart, 'psql')
                DDL = ddlObject.generate_ddl(ER, "psql")
                print(DDL)
                with open('IO/DDL', 'wb') as output:
                    pickle.dump(DDL, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                return HttpResponseRedirect('/ddl/finish')
                
    else:
        form = UploadFileForm()
    return render(request, 'ddl/upload.html', {'form': form})