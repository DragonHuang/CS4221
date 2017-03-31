from django import forms

class UploadFileForm(forms.Form):
    File = forms.FileField()
    
    Database = forms.ChoiceField(
        choices = (
            ('psql', "PostgreSQL"), 
            ('mysql', "MySQL"),
            ('oracle', "Oracle Database"),
            ('mssql', "Microsoft Database")
        ),
        widget = forms.RadioSelect,
        initial = 'psql',
    )
    Options = forms.MultipleChoiceField(
        choices = (
            ('1', "Smart Parsing"), 
            ('2', 'Comfirmation before finishing')
        ),
        initial = '1',
        widget = forms.CheckboxSelectMultiple,
        help_text = "<strong>Note:</strong> blablablabla.",
    )


class ConfirmForm(forms.Form):
    Tables = forms.CharField(widget=forms.TextInput(attrs={'id': 'data'}))