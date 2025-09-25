from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from LIFTEH.views import LoginView, ToView, HomeView, ChartsView, TasksView, DiagnosticView, map_view, get_objects
from LIFTEH import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test


urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('admin/', admin.site.urls),

    path('to/', ToView.as_view(), name='to'),

    path('object/add/', views.object_add, name='object_add'),
    path('object/edit/<int:pk>/', views.objects_edit, name='object_edit'),
    path('object/delete/<int:pk>/', views.object_delete, name='object_delete'),

    path('object_avr_add/', views.object_avr_add, name='object_avr_add'),

    path('avr/edit/<int:pk>/', views.avr_edit, name='avr_edit'),
    path('avr/add/<int:pk>/', views.avr_add, name='avr_add'),
    path('avr/delete/<int:pk>/', views.avr_delete, name='avr_delete'),

    path('diagnostic/', DiagnosticView.as_view(), name='diagnostic'),
    path('diagnostic/add/', views.diagnostic_add, name='diagnostic_add'),
    path('diagnostic/edit/<int:pk>/',
         views.diagnostic_edit, name='diagnostic_edit'),
    path('diagnostic/delete/<int:pk>/',
         views.diagnostic_delete, name='diagnostic_delete'),

    path('service/add/<int:object_id>/', views.service_add, name='service_add'),

    path('problems/', views.problems_view, name='problems'),
    path('problems/add/', views.add_problem, name='add_problem'),
    path('problems/<int:problem_id>/update_status/',
         views.update_problem_status, name='update_problem_status'),
    path('problems/<int:problem_id>/edit/',
         views.edit_problem, name='edit_problem'),
    path('problems/<int:problem_id>/delete/',
         views.delete_problem, name='delete_problem'),

    path('charts/', ChartsView.as_view(), name='charts'),
    path('tasks/', user_passes_test(lambda u: u.is_superuser)
         (TasksView.as_view()), name='tasks'),
    path('tasks/', TasksView.as_view(), name='tasks'),

    path('map/', map_view, name='map'),
    path('api/objects', get_objects, name='get_objects'),
    path('get-objects/', views.get_objects, name='get_objects'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
