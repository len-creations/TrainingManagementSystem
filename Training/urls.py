from django.urls import path
from django.conf.urls import handler404
from Training import views
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
# from .views import TraineeProgressView

urlpatterns = [
    path("",views.index,name="index"),
    path("login",views.login_view, name="login"),
    path("Register",views.register,name="register"),
    path("logout",views.logout_view, name="logout"),
     path('create_profile/', views.create_profile, name='create_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path("success",views.success_page, name="success_page"),
    path("Profile_pic",views.profile_Pic,name='profile_Pic'),
    #training resources urls
    path('training-modules/create/', views.training_module_create, name='training_module_create'),
    path('training-modules/', views.training_module_list, name='training_module_list'),
    path('training-modules/<int:pk>/', views.training_module_detail, name='training_module_detail'),
    path('categories/',views.category_list, name='category_list'),
    path('category/<str:category>/', views.category_detail, name='category_detail'),
    path('update-module-status/',views.update_module_status, name='update_module_status'),
    path('get-module-status/',views.get_module_status, name='get_module_status'),
    path('trainee_progress_summary/', views.trainee_progress_summary, name='trainee_progress_summary'),
    path('upload/',views.upload_document,name='upload_document'),
    path('documents/',views.document_list,name='document_list'),
    # path('trainee-progress/',TraineeProgressView.as_view(), name='trainee_progress'),

    path('send-email/', views.send_test_email, name='send_email'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset.html'), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset.html'), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset.html'), name='password_reset_complete'),
    path('test-token/',views.test_token_view, name='test_token'),
]   
#custom handler for 404 errors
handler404 = 'Training.views.custom_404_view'