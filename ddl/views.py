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


def error(request):
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
        try:
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
        except ValueError as e:
            print "not JSON value, pass"
        

        print "\n\n\n"
        print ER
        ddlObject = DDLGenerator()
        DDL = ddlObject.generate_ddl(ER, database)

        fdset = ddlObject.Database.drived_fdset()

        bcnf_check = []
        check_bcnf = fdset.check_bcnf()
        bcnf_check.append("$$$$\n<h4>Is in BCNF: </h4>" + str(len(check_bcnf) == 0))
        bcnf_check.append("%%%%Attributes: \n" + fdset.get_attributes_str())
        bcnf_check.append("%%%%Dependencies: \n" + fdset.get_dependencies_str())

        if len(check_bcnf) > 0:
            error_str = [', '.join(d[0][0]) + ' --> ' + ', '.join(d[0][1])+ '\nError: ' + d[1] + '\n' for d in check_bcnf]
            bcnf_check.append("These dependencies are not valid: \n" + '\n'.join(error_str))
        DDL.append('\n\n' + '\n\n'.join(bcnf_check))

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
            try:
                ER = parseXML(request.FILES['File'])
            except Exception as e:
                print e
                print str(e)
                return render(request, 'ddl/error.html',
                    {
                        'TYPE': "XML FORMAT Error",
                        'ERROR': str(e)
                    })
            
            check_values = request.POST.getlist('Options')
            Database = request.POST.get('Database')

            ddlObject = DDLGenerator()
            if u'1' in check_values:
                smart = True
            else:
                smart = False
            
            if u'2' in check_values:
                try:
                    ER = ddlObject.fill_missing_type(ER, smart, Database)
                except Exception as e:
                    print e
                    print str(e)
                    return render(request, 'ddl/error.html',
                        {
                            'TYPE': "XML Content Error",
                            'ERROR': str(e)
                        })

                with open('IO/ER', 'wb') as output:
                    pickle.dump(ER, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                with open('IO/DB', 'wb') as output:
                    pickle.dump(Database, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                return HttpResponseRedirect('/ddl/confirm')
            else:
                try:
                    ER = ddlObject.fill_missing_type(ER, smart, Database)
                    DDL = ddlObject.generate_ddl(ER, Database)
                except Exception as e:
                    return render(request, 'ddl/error.html',
                        {
                            'TYPE': "XML Content Error",
                            'ERROR': str(e)
                        })
                
                fdset = ddlObject.Database.drived_fdset()

                bcnf_check = []
                check_bcnf = fdset.check_bcnf()
                bcnf_check.append("$$$$\n<h4>Is in BCNF: </h4>" + str(len(check_bcnf) == 0))
                bcnf_check.append("%%%%Attributes: \n" + fdset.get_attributes_str())
                bcnf_check.append("%%%%Dependencies: \n" + fdset.get_dependencies_str())

                if len(check_bcnf) > 0:
                    error_str = [', '.join(d[0][0]) + ' --> ' + ', '.join(d[0][1])+ '\nError: ' + d[1] + '\n' for d in check_bcnf]
                    bcnf_check.append("These dependencies are not valid: \n" + '\n'.join(error_str))
                DDL.append('\n\n' + '\n\n'.join(bcnf_check))

                with open('IO/DDL', 'wb') as output:
                    pickle.dump(DDL, output, pickle.HIGHEST_PROTOCOL)
                output.close()
                return HttpResponseRedirect('/ddl/finish')
                
    else:
        form = UploadFileForm()
    return render(request, 'ddl/upload.html', {'form': form})