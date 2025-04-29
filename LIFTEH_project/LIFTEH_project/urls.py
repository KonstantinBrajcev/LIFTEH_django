from django.contrib import admin
from django.urls import path
from LIFTEH.views import LoginView, ToView, HomeView, ChartsView, TasksView, DiagnosticView, SwitchView
from LIFTEH import views
from django.conf import settings
from django.conf.urls.static import static
# from django.urls import include

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    #     path('', include('LIFTEH.urls')),

    path('object/add/', views.object_add, name='object_add'),
    #     path('object/add/', ObjectCreateView.as_view(), name='object_add'),
    path('object/edit/<int:pk>/', views.objects_edit, name='object_edit'),
    path('object/delete/<int:pk>/', views.object_delete, name='object_delete'),

    path('object_avr_add/', views.object_avr_add, name='object_avr_add'),

    path('avr/edit/<int:pk>/', views.avr_edit, name='avr_edit'),
    path('avr/add/<int:pk>/', views.avr_add, name='avr_add'),
    path('avr/delete/<int:pk>/', views.avr_delete, name='avr_delete'),

    path('charts/', ChartsView.as_view(), name='charts'),
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('diagnostic/', DiagnosticView.as_view(), name='diagnostic'),
    path('diagnostic/add/', views.diagnostic_add, name='diagnostic_add'),
    path('diagnostic/edit/<int:pk>/',
         views.diagnostic_edit, name='diagnostic_edit'),
    path('diagnostic/delete/<int:pk>/',
         views.diagnostic_delete, name='diagnostic_delete'),

    path('service/add/<int:object_id>/', views.service_add, name='service_add'),

    path('login/', LoginView.as_view(), name='login'),
    path('switch/', SwitchView.as_view(), name='switch'),

    path('to/', ToView.as_view(), name='to'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
