from django import forms


class YandexTokenForm(forms.Form):
    token = forms.CharField(
        label="Yandex Music Token",
        widget=forms.Textarea(attrs={"rows": 4})
    )
