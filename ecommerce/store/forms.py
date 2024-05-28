from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Review
from .models import CapturedImage, Customer


class ImageForm(forms.ModelForm):
    class Meta:
        model = CapturedImage
        fields = ['image']



class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    profile_image = forms.ImageField(required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password1','password2', 'profile_image']

    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create a Customer instance associated with this User
            Customer.objects.create(
                user=user,
                name=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}",
                email=self.cleaned_data['email'],
                profile_image=self.cleaned_data.get('profile_image', 'default.jpg') 
            )
        return user

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

