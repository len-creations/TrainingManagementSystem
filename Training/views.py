from django.shortcuts import render,redirect,get_object_or_404  
from django.contrib.auth import authenticate,login, logout
from django.http import HttpResponseRedirect,HttpResponseNotFound,JsonResponse,HttpResponse
from django.urls import reverse
from .models import User,Profile,TrainingModule,TraineeProgress,TrainingDocuments,PlannedTraining,Exam
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from.forms import profileupdateform,UserProfileForm,TrainingModuleForm,TraineeProgressFilterForm,TrainingDocumentsForm,ReportFilterForm,TraineeProgressForm,PlannedTrainingForm,DateFilterForm,ExamForm
from PyPDF2 import PdfReader
import os
import random
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date
from django.db.models import Sum,Count, Avg,Q
from django.views import View
import traceback    
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.core.mail import send_mail  
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from weasyprint import HTML
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from xhtml2pdf import pisa
from io import BytesIO
import openpyxl

# Create your views here.
# def index(request):
#     return render(request,'Training/layout.html')
def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        # Search in Profile
        profile_results = Profile.objects.filter(
            Q(name__icontains=query) | 
            Q(staffnumber__icontains=query) | 
            Q(designation__icontains=query)
        )
        for profile in profile_results:
            results.append({
                'type': 'Profile',
                'name': profile.name,
                'description': profile.designation,
                'url': profile.get_absolute_url(), 
            })

        # Search in TrainingModule
        module_results = TrainingModule.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(code__icontains=query)
        )
        for module in module_results:
            results.append({
                'type': 'Training Module',
                'name': module.title,
                'description': module.description,
                'url': module.get_absolute_url(),  
            })

        # Search in Exam
        exam_results = Exam.objects.filter(
            Q(profile__name__icontains=query) | 
            Q(training_module__title__icontains=query)
        )
        for exam in exam_results:
            results.append({
                'type': 'Exam',
                'name': exam.profile.name,
                'description': f'Exam for {exam.training_module.title} on {exam.date_of_exam}',
                'url': exam.get_absolute_url(),  
            })

        # Search in TrainingDocuments
        document_results = TrainingDocuments.objects.filter(
            Q(trainee_names__icontains=query) |
            Q(training_module_name__icontains=query) |
            Q(documentname__icontains=query)
        )
        for document in document_results:
            results.append({
                'type': 'Document',
                'name': document.documentname,
                'description': document.training_module_name,
                'url': document.get_absolute_url(), 
            })

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'Training/index.html', context)
###########################ACCOUNT REGISTRATION AND PROFILE HANDLING############################
def login_view(request):
    if request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            next_url=request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        
        else:
            return render(request,'Training/login.html',{
                "message": "Invalid username and/or password.",
                "next": request.GET.get("next"),
            })
    else:
        return render(request, "Training/login.html", {"next": request.GET.get("next")})
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password=request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "Training/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "Training/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "Training/register.html")
            
def success_page(request):
    return render(request, 'Training/success.html')

@login_required
def create_profile(request):
    user_instance = request.user

    try:
        profile_instance = Profile.objects.get(user=user_instance)
        messages.info(request, 'Profile already exists. You can update it instead.')
        return redirect('update_profile')  # Redirect to update profile page if it exists
    except Profile.DoesNotExist:
        # No profile exists, so proceed to create one
        if request.method == 'POST':
            form = profileupdateform(request.POST, request.FILES, user_instance=user_instance)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = user_instance
                profile.save()
                messages.success(request, 'Profile created successfully!')
                return redirect('success_page')  # Redirect to a success page or any other page
        else:
            form = profileupdateform(user_instance=user_instance)

    return render(request, 'Training/create_profile.html', {'form': form})
          
@login_required
def update_profile(request):
    # Retrieve or create a Profile instance for the current user
    try:
        profile_instance = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found. Please create a profile first.')
        return redirect('create_profile')  # Redirect to profile creation page or similar

    if request.method == 'POST':
        form = profileupdateform(request.POST, request.FILES, instance=profile_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect("success_page")
    else:
        form =profileupdateform(instance=profile_instance)

    return render(request, 'Training/create_profile.html', {'form': form})


@login_required
def profile_Pic(request):
    # Retrieve or create a Profile instance for the current user
    try:
        profile_instance = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found. Please create a profile first.')
        return redirect('create_profile')  # Redirect to profile creation page or similar

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect("success_page")
    else:
        form =UserProfileForm(instance=profile_instance)

    return render(request, 'Training/create_profile.html', {'form': form})

def custom_404_view(request,exception):
    if "Not Found:" in str(exception):  # Check if the exception message contains "Not Found:"
        return render(request, 'Training/404.html', status=404)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')
####################################################################################ABOUT MODULES AND MODULE HANDLING#########################
def training_module_create(request):
    if request.method == 'POST':
        form = TrainingModuleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('training_module_list')
    else:
        form = TrainingModuleForm()
    return render(request, 'Training/training_module_form.html', {'form': form})

def training_module_delete(request, pk):
    training_module = get_object_or_404(TrainingModule, pk=pk)

    if request.method == 'POST':
        training_module.delete()
        return redirect('show_all')  # Redirect to the list view after deletion

    return render(request, 'Training/training_module_confirm_delete.html', {'training_module': training_module})
def show_all(request):
    training_modules = TrainingModule.objects.all()
    return render(request, 'Training/deletion_view.html', {'training_modules': training_modules})


@login_required
def training_module_list(request):
    training_modules = TrainingModule.objects.all()
    return render(request, 'Training/training_module_list.html', {'training_modules': training_modules})


def training_module_detail(request, pk):
    training_module = get_object_or_404(TrainingModule, pk=pk)

    if training_module.file:
        file_extension = os.path.splitext(training_module.file.name)[1].lower()

        if file_extension == '.pdf':
            with open(training_module.file.path, 'rb') as f:
                pdf_reader = PdfReader(f)
                num_pages = len(pdf_reader.pages)

            if training_module.total_pages != num_pages:
                training_module.total_pages = num_pages
                training_module.save()

    return render(request, 'Training/training_module_detail.html', {
        'training_module': training_module,
        'page_range': range(1, training_module.total_pages + 1) if training_module.total_pages else None
    })

def category_list(request):
    categories = TrainingModule.objects.values_list('category', flat=True).distinct()
    return render(request, 'Training/categories.html', {'categories': categories})

def category_detail(request, category):
    modules = TrainingModule.objects.filter(category__iexact=category)
    return render(request, 'Training/category_detail.html', {
        'category': category,
        'training_modules': modules
    })

    
@csrf_exempt
def update_module_status(request):
    if request.method == "POST":
        try:
            trainee_id = int(request.POST.get('trainee_id'))
            training_module_id = int(request.POST.get('training_module_id'))
            completed_modules = int(request.POST.get('completed_modules', 0))
            completed_exams = int(request.POST.get('completed_exams', 0))
            action = request.POST.get('action')  # 'complete' or 'uncomplete'

            trainee = User.objects.get(id=trainee_id)
            training_module = TrainingModule.objects.get(id=training_module_id)

            # Get the progress record or create a new one
            progress_record, created = TraineeProgress.objects.get_or_create(
                trainee=trainee,
                training_module=training_module,
                defaults={'progress': 0}
            )

            if action == 'complete':
                if progress_record.progress == 0:  # Only increment if not already completed
                    progress_record.completed_modules += completed_modules
                    # progress_record.completed_exams += completed_exams
                    progress_record.progress = 100  # Mark as complete
                    progress_record.save()
                    return JsonResponse({'status': 'success', 'message': 'Module marked as complete.'})
                else:
                    return JsonResponse({'status': 'info', 'message': 'Module already marked as complete.'})

            elif action == 'uncomplete':
                if progress_record.progress == 100:  # Only decrement if already completed
                    progress_record.completed_modules -= completed_modules
                    # progress_record.completed_exams -= completed_exams
                    progress_record.progress = 0  # Mark as incomplete
                    progress_record.save()
                    return JsonResponse({'status': 'success', 'message': 'Module marked as incomplete.'})
                else:
                    return JsonResponse({'status': 'info', 'message': 'Module already marked as incomplete.'})

            return JsonResponse({'status': 'error', 'message': 'Invalid action.'})

        except (User.DoesNotExist, TrainingModule.DoesNotExist) as e:
            return JsonResponse({'status': 'error', 'message': f"Database error: {str(e)}"})
        except Exception as e:
            # Log the full traceback for debugging
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}\n{traceback.format_exc()}'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
@require_GET
def get_module_status(request):
    try:
        trainee_id = int(request.GET.get('trainee_id'))
        training_module_id = int(request.GET.get('training_module_id'))

        trainee = User.objects.get(id=trainee_id)
        training_module = TrainingModule.objects.get(id=training_module_id)

        progress_record = TraineeProgress.objects.filter(
            trainee=trainee,
            training_module=training_module
        ).first()

        if progress_record:
            return JsonResponse({'status': 'success', 'progress': progress_record.progress})
        else:
            return JsonResponse({'status': 'success', 'progress': 0})

    except (User.DoesNotExist, TrainingModule.DoesNotExist) as e:
        return JsonResponse({'status': 'error', 'message': f"Database error: {str(e)}"})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})
 #######################################################reports##################################   
def trainee_summary(request, pk):
    form = DateFilterForm(request.GET or None)
    profile = get_object_or_404(Profile, pk=pk)
    
    # Initialize context with default values
    total_exams = 0
    total_modules = 0
    average_marks = 0
    total_completed_modules = 0
    
    if form.is_valid() and form.cleaned_data:
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if start_date and end_date:
            # Ensure start_date and end_date are datetime objects
            if isinstance(start_date, date) and not isinstance(start_date, datetime):
                start_date = datetime.combine(start_date, datetime.min.time())
            if isinstance(end_date, date) and not isinstance(end_date, datetime):
                end_date = datetime.combine(end_date, datetime.max.time())
                
            # Make aware if necessary
            start_date = timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date
            end_date = timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date
            
            # Filter exams and modules by date range
            exams = Exam.objects.filter(profile=profile, date_of_exam__range=(start_date, end_date))
            modules = TrainingModule.objects.filter(exam__profile=profile, exam__date_of_exam__range=(start_date, end_date)).distinct()
        else:
            # If no date range, get all exams and modules for the profile
            exams = Exam.objects.filter(profile=profile)
            modules = TrainingModule.objects.filter(exam__profile=profile).distinct()
        
        # Calculate summary statistics
        total_exams = exams.count()
        total_modules = modules.count()
        average_marks = exams.aggregate(average_marks=Avg('total_marks'))['average_marks'] or 0
        total_completed_modules = TraineeProgress.total_completed_modules(profile.user)

    context = {
        'profile': profile,
        'form': form,  # Pass the original form so that it retains the input
        'total_exams': total_exams,
        'total_modules': total_modules,
        'average_marks': average_marks,
        'total_completed_modules': total_completed_modules,
    }

    return render(request, 'Training/trainee_summary.html', context)


def trainee_progress_summary(request):
    form = TraineeProgressFilterForm(request.GET or None)
    completed_modules = TraineeProgress.objects.all()

    if form.is_valid():
        trainee = form.cleaned_data.get('trainee')
        training_module = form.cleaned_data.get('training_module')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if trainee:
            completed_modules = completed_modules.filter(trainee=trainee)
        if training_module:
            completed_modules = completed_modules.filter(training_module=training_module)
        
        # Convert dates to datetime and make them timezone-aware
        if start_date and end_date:
            if isinstance(start_date, date) and not isinstance(start_date, datetime):  # Check if it's a date object
                start_date = datetime.combine(start_date, datetime.min.time())
            if isinstance(end_date, date) and not isinstance(end_date, datetime):
                end_date = datetime.combine(end_date, datetime.max.time())
                
            # Ensure they are timezone-aware
            start_date = timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date
            end_date = timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date
            
            completed_modules = completed_modules.filter(date__range=[start_date, end_date])

        total_modules = completed_modules.aggregate(total_modules=Sum('completed_modules'))['total_modules'] or 0
        total_exams = completed_modules.aggregate(total_exams=Sum('completed_exams'))['total_exams'] or 0

        context = {
            'form': form,
            'completed_modules': completed_modules,
            'total_modules': total_modules,
            'total_exams': total_exams,
        }
        return render(request, 'Training/trainee_progress_summary.html', context)

    # If the form is not valid, return the form with empty data
    return render(request, 'Training/trainee_progress_summary.html', {'form': form})


def upload_document(request):
    if request.method == 'POST':
        form = TrainingDocumentsForm(request.POST, request.FILES)
        if form.is_valid():
            trainee_names = form.cleaned_data['trainee_names'].splitlines()
            training_module_name = form.cleaned_data['training_module_name']
            
            # Save the document information
            training_document = form.save(commit=False)
            training_document.training_module_name = training_module_name
            training_document.set_trainee_names(trainee_names)
            training_document.save()
            
            return redirect('success_page')  # Redirect to the list view
    else:
        form = TrainingDocumentsForm()
    return render(request, 'Training/upload_document.html', {'form': form})

def document_list(request):
    query = request.GET.get('query', '')
    
    documents = TrainingDocuments.objects.filter(
        Q(documentname__icontains=query) |
        Q(training_module_name__icontains=query) |
        Q(trainee_names__icontains=query)
    )
    
    return render(request, 'Training/document_list.html', {'documents': documents})

##################
def send_test_email(request):
    subject = 'lodige training'
    message = 'hi domininc '  # Replace with the recipient's email
    
    # recipient_list = User.objects.values_list('email', flat=True).distinct()
    recipient_list =[""]


    sender_name = "LodigeTrainingmanagementsystem"  # Replace with the desired name
    from_email = f"{sender_name} <{settings.DEFAULT_FROM_EMAIL}>"


    try:
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse('Email sent successfully!')
    except ValueError as e:
        return HttpResponse(f'Error: {e}')
    
def test_token_view(request):
    try:
        # Assume you pass the email via query parameter
        email = request.GET.get('email')
        if not email:
            return HttpResponse("No email provided.", status=400)
        
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        
        # Send a test email
        subject = "Password Reset Test"
        email_template_name = "registration/password_reset_email.html"
        context = {
            'email': email,
            'domain': request.get_host(),
            'site_name': 'training managment system',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token,
            'protocol': 'https' if request.is_secure() else 'http',
        }
        email_body = render_to_string(email_template_name, context)
        send_mail(subject, email_body, 'your-email@example.com', [email], fail_silently=False)

        response = f"Sent test email to: {email}<br>Generated token: {token}"
    except User.DoesNotExist:
        response = "User with this email does not exist."
    except Exception as e:
        response = f"An error occurred: {e}"
    
    return HttpResponse(response)


def attendance(request):
    # Render the HTML template to a string
    html_string = render_to_string('Training/training_attendance_sheet.html', {'context_variable': 'value'})
    
    # Create a BytesIO buffer to hold the PDF data
    buffer = BytesIO()
    
    # Convert HTML to PDF and write it to the buffer
    pdf_status = pisa.CreatePDF(BytesIO(html_string.encode('UTF-8')), dest=buffer)
    
    # Get the PDF data from the buffer
    pdf_file = buffer.getvalue()
    buffer.close()
    
    # Create an HTTP response with the PDF data
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="attendance_sheet.pdf"'
    
    return response

def report_filter_view(request):
    form = ReportFilterForm(request.GET or None)
    if request.method == 'GET' and form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Construct the URL with query parameters
        url = reverse('generate_report')
        query_params = f"?start_date={start_date.isoformat()}" if start_date else ""
        query_params += f"&end_date={end_date.isoformat()}" if end_date else ""
        return HttpResponseRedirect(f"{url}{query_params}")

    return render(request, 'Training/report_filter_form.html', {'form': form})

def generate_report(request):
    start_date_str = request.GET.get('start_date', None)
    end_date_str = request.GET.get('end_date', None)
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Create a workbook and select the active worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Report'

    # Define column headers
    headers = [
        'STAFF NO.', 'EMPLOYEE NAME', 'Team', 'Facility', 'Designation', 'Trainings Taken', 'Date', 'Exams', 'Date'
    ]
    sheet.append(headers)

    profiles = Profile.objects.all()
    employee_latest_progress = {}

    for profile in profiles:
        progress_queryset = TraineeProgress.objects.filter(trainee=profile.user)
        if start_date and end_date:
            progress_queryset = progress_queryset.filter(date__range=(start_date, end_date))

        latest_progress = progress_queryset.order_by('-date').first()
        
        if latest_progress:
            if profile.staffnumber not in employee_latest_progress:
                total_trainings = progress_queryset.count()
                
                # Calculate the total number of completed exams
                total_exams = progress_queryset.aggregate(total_exams=models.Sum('completed_exams'))['total_exams'] or 0

                employee_latest_progress[profile.staffnumber] = {
                    'name': profile.name,
                    'team': profile.team,
                    'facility': profile.facility,
                    'designation': profile.designation,
                    'total_trainings': total_trainings,
                    'total_exams': total_exams,
                    'latest_progress_date': latest_progress.date
                }

    for staffnumber, details in employee_latest_progress.items():
        sheet.append([
            staffnumber,
            details['name'],
            details['team'],
            details['facility'],
            details['designation'],
            details['total_trainings'],
            details['latest_progress_date'].strftime('%Y-%m-%d'),
            details['total_exams'],
            details['latest_progress_date'].strftime('%Y-%m-%d')
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="training_report.xlsx"'
    workbook.save(response)
    return response

def update_planned_trainings(request):
    if request.method == 'POST':
        form = PlannedTrainingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect back to the dashboard or wherever appropriate
    else:
        form = PlannedTrainingForm()

    return render(request, 'Training/update_planned_trainings.html', {'form': form})

def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def dashboard(request):
    now = timezone.now()
    current_year = now.year

    # Initialize the form with the GET parameters (if any)
    form = DateFilterForm(request.GET)
    start_date = None
    end_date = None

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

    # Base queryset for filtering
    trainee_progress_queryset = TraineeProgress.objects.all()

    if start_date:
        trainee_progress_queryset = trainee_progress_queryset.filter(date__gte=start_date)
    if end_date:
        trainee_progress_queryset = trainee_progress_queryset.filter(date__lte=end_date)

    # Data for top-right - Aggregating by team
    team_data = Profile.objects.values('team').annotate(
        planned_trainings=Sum('planned_trainings__plan'),
        completed_trainings=Count('user__traineeprogress'),
        exams_count=Count('user__traineeprogress__completed_exams')
    ).order_by('team')

    # Data for yearly report
    planned_trainings = PlannedTraining.objects.count()
    completed_trainings = trainee_progress_queryset.filter(date__year=current_year).count()

    # Data for facilities
    facilities = Profile.objects.values('facility').annotate(
        total_planned_trainings=Sum('planned_trainings__plan'),
        completed_trainings=Count('user__traineeprogress')
    ).order_by('facility')

    # Data for bar graph (top-left)
    trainings_per_team = Profile.objects.values('team').annotate(
        planned_trainings_count=Sum('planned_trainings__plan'),
        completed_trainings_count=Sum('user__traineeprogress__training_module__plannedtraining__plan')  # Adjust based on your data model
    ).order_by('team')

    team_labels = [entry['team'] for entry in trainings_per_team]
    planned_data = [entry['planned_trainings_count'] for entry in trainings_per_team]
    completed_data = [entry['completed_trainings_count'] for entry in trainings_per_team]
    colors = [generate_random_color() for _ in team_labels]

    # Data for previous months
    previous_months = trainee_progress_queryset.values(
        'date__month'
    ).annotate(
        planned_trainings=Sum('training_module__plannedtraining__plan'),
        actual_trainings=Count('training_module'),
        exams_done=Count('completed_exams')
    ).order_by('date__month')
    yearly_stats = trainee_progress_queryset.values(
        'date__year'
    ).annotate(
        planned_trainings=Sum('training_module__plannedtraining__plan'),
        actual_trainings=Count('training_module'),
        exams_done=Count('completed_exams')
    ).order_by('date__year')

    context = {
        'form': form,
        'team_data': team_data,
        'planned_trainings': planned_trainings,
        'completed_trainings': completed_trainings,
        'facilities': facilities,
        'trainings_per_team': trainings_per_team,
        'previous_months': previous_months,
        'planned_data': planned_data,
        'completed_data': completed_data,
        'yearly_stats': yearly_stats,
        'colors': colors 
    }

    return render(request, 'Training/dashboard.html', context)

####################exams#####################
def update_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')
    else:
        form =ExamForm()

    return render(request, 'Training/exam_form.html', {'form': form}) 

