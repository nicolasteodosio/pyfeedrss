from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class AddFeedForm(forms.Form):
    url = forms.URLField()
    alias = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-addFeedForm"
        self.helper.form_method = "post"

        self.helper.add_input(Submit("submit", "Submit"))
