from django.contrib import admin
from django.urls import path
from main_app import views
urlpatterns = [
    # path("", views.index, name="main_app"),
    path('', views.upload_urine_strip, name='upload_urine_strip'),
]
