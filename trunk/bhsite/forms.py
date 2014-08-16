from django import forms

class HomeForm(forms.Form):
    expiry = forms.DateTimeField(input_formats=[
        '%Y-%m-%d %H:%M', # '2006-10-25 23:10'
    ])
    amount 	= forms.FloatField()
    rate 	= forms.FloatField()
    address = forms.CharField(max_length=35, required=False)
    select_direction = forms.ChoiceField(choices=[(0, 'Decrease'), (1, 'Increase')])

class SubmitForm(forms.Form):
    expiry = forms.DateTimeField(input_formats=[
        '%Y-%m-%d %H:%M', # '2006-10-25 23:10'
    ])
    amount 	= forms.FloatField()
    rate 	= forms.FloatField()
    address = forms.CharField(max_length=35)
    bh_address = forms.CharField(max_length=35)
    select_direction = forms.ChoiceField(choices=[(0, 'Decrease'), (1, 'Increase')])

class BitcoinRecipient(forms.Form):
    bitcoin_recipient = forms.CharField(max_length=100)


#~ class RegisterForm(BitcoinRecipient):
    #~ email = forms.EmailField()
    #~ password = forms.CharField(widget=forms.PasswordInput)
    #~ password2 = forms.CharField(widget=forms.PasswordInput)

