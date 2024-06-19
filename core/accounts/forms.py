import phonenumbers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from accounts.models import User, Account
from django.core.exceptions import ValidationError


class PhoneNumberInput(forms.CharField):
    def validate(self, value):
        try:
            parse_number = phonenumbers.parse(value, 'KZ')

            if not phonenumbers.is_valid_number(parse_number):
                raise ValidationError('Номер телефона должен быть в формате: +7XXXXXXXXXX')
            formatted_number = phonenumbers.format_number(parse_number, phonenumbers.PhoneNumberFormat.E164)

            return formatted_number

        except phonenumbers.phonenumberutil.NumberParseException:

            raise ValidationError('Invalid phone number format')


class RegisterForm(UserCreationForm):
    
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-2",
            }
        ),
        help_text=password_validation.password_validators_help_text_html(),
        label="Пароль",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-2",
            }
        ),
        strip=False,
        help_text="Enter the same password as before, for verification.",
        label="Повторите пароль",
    )
    phone = PhoneNumberInput(max_length=12,
                             widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': '+7XXXXXXXXXX '}))
    
    def clean_iin_bin(self):
        iin = self.cleaned_data.get('iin_bin', '')
        if not iin.isdigit() or len(iin) != 12:
            raise ValidationError("ИИН/БИН должен быть из 12 цифр.")
        if User.objects.filter(iin_bin=iin).exists():
            raise ValidationError("Пользователь с таким ИИН/БИН уже существует.")
        return iin

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password1', 'password2', 'iin_bin',
            'phone'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
            'iin_bin': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
        }


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserUpdateForm(forms.ModelForm):
    phone = PhoneNumberInput(max_length=12,
                             widget=forms.TextInput(attrs={'class': "form-control"}))

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }


class PasswordChangeForm(forms.ModelForm):
    password = forms.CharField(label="Новый пароль", strip=False,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(label="Подтвердите пароль",
                                       widget=forms.PasswordInput(attrs={'class': 'form-control'}), strip=False)
    old_password = forms.CharField(label="Старый пароль", strip=False,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают!')
        return password_confirm

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.instance.check_password(old_password):
            raise forms.ValidationError('Старый пароль неправильный!')
        return old_password


    def save(self, commit=True):
        user = self.instance
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ['password', 'password_confirm', 'old_password']


class AccountRegisterForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['city', 'address', 'postal_code']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
