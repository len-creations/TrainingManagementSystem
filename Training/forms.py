from django import forms
from .models import User,Profile,TrainingModule,TraineeProgress,PlannedTraining
from django.core.validators import FileExtensionValidator
from .models import TrainingDocuments

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

class TraineeProgressForm(forms.ModelForm):
    trainee = forms.ModelChoiceField(queryset=User.objects.all())
    training_module = forms.ModelChoiceField(queryset=TrainingModule.objects.all())
    
    class Meta:
        model = TraineeProgress
        fields = ['trainee', 'training_module', 'progress', 'completed_modules', 'completed_exams']

    def __init__(self, *args, **kwargs):
        # Allow for an instance to be passed to populate fields with existing data
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['completed_modules'].initial = instance.completed_modules
            self.fields['completed_exams'].initial = instance.completed_exams   
            
class TraineeProgressFilterForm(forms.Form):
    trainee = forms.ModelChoiceField(queryset=User.objects.all(), required=False, label="Trainee")
    training_module = forms.ModelChoiceField(queryset=TrainingModule.objects.all(), required=False, label="Training Module")
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class TrainingDocumentsForm(forms.ModelForm):
    trainee_names = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter trainee names, one per line'}),
        help_text='Enter trainee names, each on a new line.',
        required=True
    )
    training_module_name = forms.CharField(
        max_length=100,
        help_text='Enter the name of the training module.',
        required=True
    )

    class Meta:
        model = TrainingDocuments
        fields = ['documentname', 'document', 'document_domain', 'facility','Trainingdate']

    def clean(self):
        cleaned_data = super().clean()
        trainees = cleaned_data.get('trainee_names')  # Updated field name to match form
        training_module_name = cleaned_data.get('training_module_name')

        if not trainees or not training_module_name:
            raise forms.ValidationError('Both trainees and training module are required.')

        return cleaned_data

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )

class PlannedTrainingForm(forms.ModelForm):
    class Meta:
        model = PlannedTraining
        fields = ['profile', 'training_module', 'team', 'plan']

    
class DateFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))