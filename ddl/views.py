import pickle
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.conf import settings

from .forms import UploadFileForm
from .forms import ConfirmForm
from .parse import parseXML

from ddlgenerator.DDLGenerator import DDLGenerator

def index(request):
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
    return HttpResponse("todo")

def confirm(request):
    file = open('IO/ER', 'rb')
    ER = pickle.load(file)
    file.close()

    file = open('IO/DB', 'rb')
    database = pickle.load(file)
    file.close()

    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        data = request.POST.get("Tables")
        modify = json.loads(data)
        print ER
        print modify
        for entity in modify:
            for ent in ER['entity']:
                if ent['name'] == entity:
                    for attr in ent['attribute']:
                        if int(attr['id']) < len(modify[entity]):
                            if modify[entity][int(attr['id'])] != None:
                                attr['type'] = str(modify[entity][int(attr['id'])])

        print "\n\n\n"
        print ER
        ddlObject = DDLGenerator()
        DDL = ddlObject.generate_ddl(ER, database)
        with open('IO/DDL', 'wb') as output:
            pickle.dump(DDL, output, pickle.HIGHEST_PROTOCOL)
        output.close()
        return HttpResponseRedirect('/ddl/finish')
    else:
        form = ConfirmForm()
        return render(request, 'ddl/confirm.html',
            {
                'form': form,
                'ER': json.dumps(ER),
                'DB': database
            })

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            ER = parseXML(request.FILES['File'])
            
            check_values = request.POST.getlist('Options')
            Database = request.POST.get('Database')

            ddlObject = DDLGenerator()
            if u'1' in check_values:
                smart = True
            else:
                smart = False
            
            if u'2' in check_values:
                ER = ddlObject.fill_missing_type(ER, smart, Database)

                with open('IO/ER', 'wb') as output:
                    pickle.dump(ER, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                with open('IO/DB', 'wb') as output:
                    pickle.dump(Database, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                return HttpResponseRedirect('/ddl/confirm')
            else:
                ER = ddlObject.fill_missing_type(ER, smart, Database)
                DDL = ddlObject.generate_ddl(ER, Database)
                DDL.append("\n\nIs in BCNF: " + str(ddlObject.Database.drived_fdset().is_bcnf()))
                with open('IO/DDL', 'wb') as output:
                    pickle.dump(DDL, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                return HttpResponseRedirect('/ddl/finish')
                
    else:
        form = UploadFileForm()
    return render(request, 'ddl/upload.html', {'form': form})