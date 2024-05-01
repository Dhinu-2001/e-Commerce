import re
from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        # Check for consecutive three same letters
        if any(first_name[i] == first_name[i+1] == first_name[i+2] for i in range(len(first_name)-2)):
            raise forms.ValidationError("First name cannot contain consecutive three same letters.")
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("First name cannot contain digits.")
        if '.' in first_name:
            raise forms.ValidationError("First name cannot contain dots.")
        if len(first_name) <= 2:
            raise forms.ValidationError("First name must be longer than 2 characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Check for consecutive three same letters
        if any(last_name[i] == last_name[i+1] == last_name[i+2] for i in range(len(last_name)-2)):
            raise forms.ValidationError("Last name cannot contain consecutive three same letters.")
        if any(char.isdigit() for char in last_name):
            raise forms.ValidationError("Last name cannot contain digits.")
        if '.' in last_name:
            raise forms.ValidationError("Last name cannot contain dots.")
        if len(last_name) <= 2:
            raise forms.ValidationError("Last name must be longer than 2 characters.")
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        elif len(phone_number) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        elif len(set(phone_number)) == 1 and phone_number[0] == '0':  # Compare as a string
            raise forms.ValidationError("Phone number can't contain only 0s.")
        return phone_number
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Password requires minimum 8 characters")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        # Check if password contains at least one digit
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one numeric character.")
        # Check if password contains at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        # Check if password contains at least one lowercase letter
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        # Check if password contains at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character.")
        # Check for whitespaces in the password
        if ' ' in password:
            raise forms.ValidationError("Password cannot contain whitespaces.")
        
        return password
        
    def clean_confirmpassword(self):
        password = self.cleaned_data.get('password')
        print(password)
        confirmpassword = self.cleaned_data.get('confirmpassword')
        print(confirmpassword)
        if password is None:
        # Password did not pass the previous validation, no need to compare
            return confirmpassword
        # Check if passwords match
        if password != confirmpassword:
            raise forms.ValidationError("Passwords do not match.")
        return confirmpassword

    def __init__(self, *args, **kwargs):
        super(RegistrationForm,self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']= 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']= 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder']= 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder']= 'Enter Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'account_form register'
                