from django import forms


RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        max_length=1000,
    )
