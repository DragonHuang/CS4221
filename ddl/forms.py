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
    # multicolon_select = forms.MultipleChoiceField(
    #     choices = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')),
    # )
    # radio_buttons = forms.ChoiceField(
    #     choices = (
    #         ('option_one', "Option one is this and that be sure to include why it's great"), 
    #         ('option_two', "Option two can is something else and selecting it will deselect option one")
    #     ),
    #     widget = forms.RadioSelect,
    #     initial = 'option_two',
    # )
