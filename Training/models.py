from django.db import models
from django.contrib.auth import get_user_model
from PyPDF2 import PdfReader
from django.utils import timezone
import json
# # Create your models here.
# class User(AbstractUser):
#     pass  # Inherits fields and methods from AbstractUser

# class Trainee(User):
#     # Additional fields specific to Trainee
#     age = models.PositiveIntegerField(default=0)

# class Trainer(User):
#     # Additional fields specific to Trainer
#     bio = models.TextField(blank=True)

# class Manager(User):
#     # Additional fields specific to Manager
#     department = models.CharField(max_length=100)

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="John Doe")
    staffnumber = models.CharField(max_length=100, default='Q0000')
    profile_pic = models.ImageField(upload_to='Training/profile_pics', blank=True, null=True)
    team = models.CharField(max_length=20, default="Team00")
    designation = models.CharField(max_length=60, default="technician")
    facility = models.CharField(max_length=15, default="cargo")
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}, {self.staffnumber}'
    
class TrainingModule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    code=models.CharField(max_length=10)
    category=models.CharField(max_length=10,default="equipment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='Training/uploads/', blank=True, null=True)
    total_pages = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    def update_total_pages(self):
        if self.file:
            with open(self.file.path, 'rb') as f:
                pdf_reader = PdfReader(f)
                self.total_pages = len(pdf_reader.pages)
                self.save()

class TraineeProgress(models.Model):
    trainee = models.ForeignKey(User, on_delete=models.CASCADE)
    training_module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField()
    completed_modules = models.PositiveIntegerField(default=0)
    completed_exams = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('trainee', 'training_module')

    def update_progress(self, module_count, exam_count):
        self.completed_modules = module_count
        self.completed_exams = exam_count
        self.save()

    @staticmethod
    def total_completed_modules(trainee):
        return TraineeProgress.objects.filter(trainee=trainee).aggregate(
            total_modules=models.Sum('completed_modules')
        )['total_modules'] or 0

    @staticmethod
    def total_completed_exams(trainee):
        return TraineeProgress.objects.filter(trainee=trainee).aggregate(
            total_exams=models.Sum('completed_exams')
        )['total_exams'] or 0

    @property
    def trainee_name(self):
        return self.trainee.profile.name if hasattr(self.trainee, 'profile') else "No Name"

    def __str__(self):
        return f'{self.trainee.profile.name} - {self.training_module}'
    

class TrainingDocuments(models.Model):
    trainee_names = models.TextField(blank=True, null=True)  # JSON string to store list of trainee names
    training_module_name = models.CharField(max_length=100, blank=True, null=True)  # Store training module name
    documentname = models.CharField(max_length=100)
    document = models.FileField(upload_to='Training/ATTENDANCE_SHEET/', blank=True, null=True)
    document_domain = models.CharField(max_length=20)
    facility = models.CharField(max_length=10)
    Trainingdate=models.CharField(max_length=50,default='date 000')
    date = models.DateTimeField(auto_now_add=True)
    unique_number = models.CharField(max_length=50, blank=True, null=True)  # For storing unique number

    def set_trainee_names(self, names):
        self.trainee_names = json.dumps(names)

    def get_trainee_names(self):
        return json.loads(self.trainee_names) if self.trainee_names else []

    def save(self, *args, **kwargs):
        # Ensure the date is set
        if not self.pk and self.date is None:
            self.date = timezone.now()  # Ensure you import timezone if using timezone.now()

        # Generate unique_number only if it is not set
        if not self.unique_number:
            date_str = self.date.strftime('%Y%m%d') if self.date else '00000000'
            module_abbr = self.training_module_name[:3].upper() if self.training_module_name else 'XXX'
            
            # Find the latest unique number with the same date and module abbreviation
            last_document = TrainingDocuments.objects.filter(
                date__date=self.date.date(),
                training_module_name=self.training_module_name
            ).order_by('-unique_number').first()
            
            if last_document and last_document.unique_number:
                # Extract the last sequential number
                last_number = int(last_document.unique_number.split('-')[-1])
                next_number = last_number + 1
            else:
                next_number = 1

            # Format the next sequential number with leading zeros
            sequential_str = f"{next_number:04d}"

            # Set the unique number
            self.unique_number = f"{date_str}-{module_abbr}-{sequential_str}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.documentname} - {self.date}'
 