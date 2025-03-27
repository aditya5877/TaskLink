# MyApp/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, WorkerReview

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    middle_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=True)
    age = forms.IntegerField(min_value=18, required=True)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=True)
    mobile_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    location = forms.CharField(max_length=100, required=True)
    is_worker = forms.BooleanField(required=False, label="Register as a worker")
    worker_type = forms.CharField(max_length=50, required=False)
    experience = forms.IntegerField(min_value=0, required=False)
    police_verification = forms.BooleanField(required=False, label="Do you have police verification?")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'age', 'gender', 'mobile_number', 'email',
                  'location', 'is_worker', 'worker_type', 'experience', 'police_verification', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        is_worker = cleaned_data.get('is_worker')
        worker_type = cleaned_data.get('worker_type')
        experience = cleaned_data.get('experience')
        if is_worker and not worker_type:
            raise forms.ValidationError("Please specify your worker type if registering as a worker.")
        if is_worker and experience is None:
            raise forms.ValidationError("Please provide your experience if registering as a worker.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.middle_name = self.cleaned_data['middle_name']
        user.last_name = self.cleaned_data['last_name']
        user.age = self.cleaned_data['age']
        user.gender = self.cleaned_data['gender']
        user.mobile_number = self.cleaned_data['mobile_number']
        user.email = self.cleaned_data['email']
        user.location = self.cleaned_data['location']
        user.is_worker = self.cleaned_data['is_worker']
        user.worker_type = self.cleaned_data['worker_type']
        user.experience = self.cleaned_data['experience']
        user.police_verification = self.cleaned_data['police_verification']
        if commit:
            user.save()
        return user

class WorkerReviewForm(forms.ModelForm):
    class Meta:
        model = WorkerReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.Select(choices=[(i, f"{i} stars") for i in range(1, 6)])
        }