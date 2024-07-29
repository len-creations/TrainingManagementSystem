from django.db import models
from django.contrib.auth import get_user_model
from PyPDF2 import PdfReader
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
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
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
    trainee = models.OneToOneField(User, on_delete=models.CASCADE)
    training_module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField()
    completed_modules = models.PositiveIntegerField(default=0)  # Track completed modules
    completed_exams = models.PositiveIntegerField(default=0)    # Track completed exams
    
    def update_progress(self, module_count, exam_count):
        self.completed_modules = module_count
        self.completed_exams = exam_count
        self.save()

    def __str__(self):
        return f'{self.trainee} - {self.training_module}'