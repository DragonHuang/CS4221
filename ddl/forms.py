from django import forms

class UploadFileForm(forms.Form):
    File = forms.FileField()
    Options = forms.MultipleChoiceField(
        choices = (
            ('1', "Smart Parsing"), 
            ('2', 'Comformation before finishing')
        ),
        initial = '1',
        widget = forms.CheckboxSelectMultiple,
        help_text = "<strong>Note:</strong> blablablabla.",
    )