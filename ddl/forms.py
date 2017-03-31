from django import forms

class UploadFileForm(forms.Form):
    File = forms.FileField()
    Options = forms.MultipleChoiceField(
        choices = (
            ('1', "Smart Parsing"), 
            ('2', 'Comfirmation before finishing')
        ),
        initial = '1',
        widget = forms.CheckboxSelectMultiple,
        help_text = "<strong>Note:</strong> blablablabla.",
    )


class ComfirmForm(forms.Form):
    File = forms.FileField()
    Options = forms.ChoiceField(
        choices = (
            ('1', "Smart Parsing"), 
            ('2', 'Comfirmation before finishing')
        ),
        initial = '1',
        widget = forms.CheckboxSelectMultiple,
        help_text = "<strong>Note:</strong> blablablabla.",
    )
    Options2 = forms.MultipleChoiceField(
        choices = (
            ('1', "Smart Parsing"), 
            ('2', 'Comfirmation before finishing')
        ),
        widget=forms.CheckboxSelectMultiple(),
        label="myLabel",
        required=True, 
        error_messages={'required': 'myRequiredMessage'}
    )
