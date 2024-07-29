from django.shortcuts import render,redirect,get_object_or_404  
from django.contrib.auth import authenticate,login, logout
from django.http import HttpResponseRedirect,HttpResponseNotFound,JsonResponse
from django.urls import reverse
from .models import User,Profile,TrainingModule,TraineeProgress
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from.forms import profileupdateform,UserProfileForm,TrainingModuleForm
from PyPDF2 import PdfReader
import os
from django.views.decorators.csrf import csrf_exempt


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
    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        trainee_id = request.POST.get('trainee_id')
        completed = request.POST.get('completed') == 'true'
         
        module = get_object_or_404(TrainingModule, id=module_id)
        trainee = get_object_or_404(User, id=trainee_id)


        trainee_progress, created = TraineeProgress.objects.get_or_create(
            trainee=trainee,
            training_module=module
        )
        print(module)
        if completed:
            trainee_progress.completed_modules += 1
        else:
            trainee_progress.completed_modules -= 1

        trainee_progress.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)