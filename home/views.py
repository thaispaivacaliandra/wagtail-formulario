# home/views.py
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import FormularioSubmission

@staff_member_required
def get_submission_data(request, submission_id):
    """
    View para retornar dados da submissão em JSON
    """
    submission = get_object_or_404(FormularioSubmission, id=submission_id)
    
    return JsonResponse({
        'form_data': submission.form_data or {},
        'submit_time': submission.submit_time.strftime('%d/%m/%Y %H:%M'),
        'page_title': submission.page.title,
        'user_ip': submission.user_ip,
    })


# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('admin/get-submission-data/<int:submission_id>/', 
        views.get_submission_data, 
        name='get_submission_data'),
]