from django.shortcuts import render,redirect,get_object_or_404  
from django.contrib.auth import authenticate,login, logout
from django.http import HttpResponseRedirect,HttpResponseNotFound,JsonResponse,HttpResponse
from django.urls import reverse
from .models import User,Profile,TrainingModule,TraineeProgress,TrainingDocuments
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from.forms import profileupdateform,UserProfileForm,TrainingModuleForm,TraineeProgressFilterForm,TrainingDocumentsForm,TraineeProgressForm
from PyPDF2 import PdfReader
import os
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
from xhtml2pdf import pisa
from io import BytesIO
import openpyxl

# Create your views here.
def index(request):
    return render(request,'Training/layout.html')
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

# def trainee_progress_summary(request):
#     form = TraineeProgressFilterForm(request.GET or None)
#     completed_modules = TraineeProgress.objects.all()

#     if form.is_valid():
#         trainee = form.cleaned_data.get('trainee')
#         training_module = form.cleaned_data.get('training_module')
#         start_date = form.cleaned_data.get('start_date')
#         end_date = form.cleaned_data.get('end_date')

#         if trainee:
#             completed_modules = completed_modules.filter(trainee=trainee)
#         if training_module:
#             completed_modules = completed_modules.filter(training_module=training_module)
#         if start_date and end_date:
#             completed_modules = completed_modules.filter(date__range=[start_date, end_date])

#         total_modules = completed_modules.aggregate(total_modules=Sum('completed_modules'))['total_modules'] or 0
#         total_exams = completed_modules.aggregate(total_exams=Sum('completed_exams'))['total_exams'] or 0

#         context = {
#             'form': form,
#             'completed_modules': completed_modules,
#             'total_modules': total_modules,
#             'total_exams': total_exams,
#         }
#         return render(request, 'Training/trainee_progress_summary.html', context)

#     # If the form is not valid, return the form with empty data
#     return render(request, 'Training/trainee_progress_summary.html', {'form': form})
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
    message = 'hi phillipe '  # Replace with the recipient's email
    
    recipient_list = User.objects.values_list('email', flat=True).distinct()

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

# def attendance(request):
    
#         html_string = render(request, 'Training/training_attendance_sheet.html')
#         pdf_file = HTML(string=html_string).write_pdf()
#         response = HttpResponse(pdf_file, content_type='application/pdf')
#         response['Content-Disposition'] = 'inline; filename="attendance_sheet.pdf"'
#         return response

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

def generate_report(request):
    # Create a workbook and select the active worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Report'

    # Define column headers
    headers = [
        'STAFF NO.', 'EMPLOYEE NAME', 'Team', 'Facility', 'Designation', 'Trainings Taken', 'Date', 'Exams', 'Date'
    ]
    sheet.append(headers)

    # Get all profiles and their training progress
    profiles = Profile.objects.all()
    for profile in profiles:
        trainee_progress = TraineeProgress.objects.filter(trainee=profile.user)
        total_trainings = trainee_progress.count()
        # total_exams = trainee_progress.aggregate(total_exams=models.Sum('completed_exams'))['total_exams'] or 0
        for progress in trainee_progress:
            sheet.append([
                profile.staffnumber,
                profile.name,
                profile.team,
                profile.facility,
                profile.designation,
                total_trainings,
                progress.date.strftime('%Y-%m-%d'),
                # total_exams,
                progress.date.strftime('%Y-%m-%d')
            ])

    # Create the response object
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="training_report.xlsx"'
    workbook.save(response)
    return response

def dashboard(request):
    now = timezone.now()
    current_year = now.year

    # Data for top-right
    team_data = Profile.objects.annotate(
        trainees_count=Count('user'),
        trainings_count=Count('user__traineeprogress__training_module'),
        exams_count=Count('user__traineeprogress__completed_exams')
    ).values('team', 'trainees_count', 'trainings_count', 'exams_count')

    # Data for yearly report
    planned_trainings = TrainingModule.objects.filter(created_at__year=current_year).count()
    completed_trainings = TraineeProgress.objects.filter(date__year=current_year).count()

    # Data for facilities
    facilities = Profile.objects.annotate(
        planned_trainings=Count('user__traineeprogress__training_module'),
        completed_trainings=Count('user__traineeprogress')
    ).values('facility', 'planned_trainings', 'completed_trainings')

    # Data for bar graph (top-left)
    trainings_per_team = Profile.objects.annotate(
        count=Count('user__traineeprogress__training_module')
    ).values('team', 'count')

    # Data for previous months
    previous_months = TraineeProgress.objects.filter(date__lt=timezone.now()).values(
        'date__month'
    ).annotate(
        planned_trainings=Count('training_module'),
        actual_trainings=Count('training_module'),
        exams_done=Count('completed_exams')
    )

    context = {
        'team_data': team_data,
        'planned_trainings': planned_trainings,
        'completed_trainings': completed_trainings,
        'facilities': facilities,
        'trainings_per_team': trainings_per_team,
        'previous_months': previous_months
    }

    return render(request, 'Training/dashboard.html', context)
def update_planned_trainings(request):
    if request.method == 'POST':
        team_id = request.POST.get('team')
        planned_trainings = int(request.POST.get('planned_trainings'))  

        # Assuming you have a way to store planned trainings, for example in the Profile model
        team_profile = Profile.objects.get(id=team_id)
        team_profile.planned_trainings = planned_trainings  # Adjust according to your model structure
        team_profile.save()

        return redirect('dashboard')  # Redirect back to the dashboard or wherever appropriate

    # If GET request or other, return something else or handle accordingly
    return HttpResponse("Invalid request", status=400)