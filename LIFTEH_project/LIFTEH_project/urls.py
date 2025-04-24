from django.contrib import admin
from django.urls import path, include
from LIFTEH.views import LoginView, ToView, HomeView, ChartsView, TasksView, SwitchView
from LIFTEH import views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('__debug__/', include('debug_toolbar.urls')),

    path('object/add/', views.object_add, name='object_add'),
    path('object/edit/<int:pk>/', views.objects_edit, name='object_edit'),  
    path('object/delete/<int:pk>/', views.object_delete, name='object_delete'),

    path('avr/edit/<int:pk>/', views.avr_edit, name='avr_edit'),
    path('avr/add/<int:pk>/', views.avr_add, name='avr_add'), # ИЗ таблицы ОБЬЕКТЫ
    path('avr/delete/<int:pk>/', views.avr_delete, name='avr_delete'),

    path('object_avr_add/', views.object_avr_add, name='object_avr_add'), # ИЗ таблицы АВР

    path('service/add/<int:object_id>/', views.service_add, name='service_add'),

    path('charts/', ChartsView.as_view(), name='charts'),
    path('tasks/', TasksView.as_view(), name='tasks'),

    path('login/', LoginView.as_view(), name='login'),

    path('to/', ToView.as_view(), name='to'),
    path('admin/', admin.site.urls),

    path('switch/', SwitchView.as_view(), name='switch'),
]
