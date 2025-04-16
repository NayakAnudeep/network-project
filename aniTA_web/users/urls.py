from django.urls import path
from .views import register, login, logout

app_name = "users"

urlpatterns = [
    path('register/', register, name = "register"),
    path('login/', login, name = "login"),
    path('logout/', logout, name = "logout"),
    path('submissions/create/', views.create_submission, name='create_submission'),
    path('submissions/<str:submission_id>/', views.get_submission, name='get_submission'),
    path('submissions/<str:submission_id>/consistency/', views.check_consistency, name='check_consistency'),
    path('submissions/<str:submission_id>/similar/', views.find_similar, name='find_similar'),
]
