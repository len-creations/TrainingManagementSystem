from django import forms
from .models import User,Profile,TrainingModule
from django.core.validators import FileExtensionValidator

class profileupdateform(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'team', 'facility', 'staffnumber', 'designation', 'email', 'age']

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)  # Pop user_instance from kwargs
        super().__init__(*args, **kwargs)

        readonly_fields = [ 'email']
        for field in readonly_fields:
            self.fields[field].widget.attrs['readonly'] = True

        if user_instance:
            # Prefill the 'email' field with user's email address
            self.fields['email'].initial = user_instance.email

class UserProfileForm(forms.ModelForm):
    MAX_FILE_SIZE_MB = 6

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')
        if profile_pic and profile_pic.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"File size must be less than {self.MAX_FILE_SIZE_MB} MB")
        return profile_pic

    class Meta:
        model = Profile
        fields = ['profile_pic',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].validators.append(
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        )

class TrainingModuleForm(forms.ModelForm):
    class Meta:
        model = TrainingModule
        fields = ['title', 'description', 'file','code','category']

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file:
            if file.size > 20*2024*2024:
                raise forms.ValidationError("File size must be under 20MB.")
            if not file.content_type in ['application/pdf', 'application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
                raise forms.ValidationError("File type is not supported.")
            return file


