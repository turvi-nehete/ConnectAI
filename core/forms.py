from django import forms
from .models import Client


class ClientForm(forms.ModelForm):

    class Meta:

        model = Client

        fields = [
            "comp_name",
            "contactname",
            "c_mail",
            "phone_no",
            "city",
            "state",
            "country",
            "customer_type",
            "comp_type",
            "is_active",
        ]

        widgets = {

            "comp_name": forms.TextInput(attrs={
    "class": "form-control",
    "id": "comp_name",
    "placeholder": "Company Name"
}),

           "contactname": forms.TextInput(attrs={
    "class": "form-control",
    "id": "contactname"
}),

"c_mail": forms.EmailInput(attrs={
    "class": "form-control",
    "id": "c_mail"
}),

"phone_no": forms.TextInput(attrs={
    "class": "form-control",
    "id": "phone_no"
}),

"city": forms.TextInput(attrs={
    "class": "form-control",
    "id": "city"
}),

"state": forms.TextInput(attrs={
    "class": "form-control",
    "id": "state"
}),

"country": forms.TextInput(attrs={
    "class": "form-control",
    "id": "country"
}),

"customer_type": forms.Select(attrs={
    "class": "form-select",
    "id": "customer_type"
}),

"comp_type": forms.Select(attrs={
    "class": "form-select",
    "id": "comp_type"
}),

"is_active": forms.CheckboxInput(attrs={
    "class": "form-check-input",
    "id": "is_active"
}),
        }