# home/wagtail_hooks.py
import csv
from django.http import HttpResponse
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from .models import FormularioSubmission, FormularioPage

# Adicionar item no menu do admin do Wagtail
@hooks.register('register_admin_menu_item')
def register_csv_export_menu():
    return MenuItem(
        'Exportar Submissões', 
        reverse('wagtail_csv_export'), 
        icon_name='download',
        order=200
    )

# Registrar URLs no admin do Wagtail
@hooks.register('register_admin_urls')
def register_csv_urls():
    return [
        path('export-csv/', csv_export_view, name='wagtail_csv_export'),
        path('export-csv/<int:page_id>/', download_csv, name='download_csv'),
    ]

def csv_export_view(request):
    """
    Página para escolher qual formulário exportar
    """
    from django.shortcuts import render
    
    # Pegar formulários do usuário
    formularios = FormularioPage.objects.live()
    if not request.user.is_superuser:
        formularios = formularios.filter(owner=request.user)
    
    # Contar submissões para cada formulário
    formularios_data = []
    for form in formularios:
        count = FormularioSubmission.objects.filter(page=form).count()
        formularios_data.append({
            'form': form,
            'count': count,
            'last_submission': FormularioSubmission.objects.filter(page=form).first()
        })
    
    return render(request, 'wagtailadmin/csv_export.html', {
        'formularios': formularios_data,
    })

def download_csv(request, page_id):
    """
    Download do CSV para um formulário específico
    """
    page = get_object_or_404(FormularioPage, id=page_id)
    submissions = FormularioSubmission.objects.filter(page=page).order_by('-submit_time')
    
    # Criar resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="submissoes_{page.slug}_{page.id}.csv"'
    
    # BOM para Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    if not submissions.exists():
        writer.writerow(['Nenhuma submissão encontrada para este formulário'])
        return response
    
    # Coletar todos os campos únicos
    all_fields = set()
    for submission in submissions:
        if submission.form_data:
            all_fields.update(submission.form_data.keys())
    
    sorted_fields = sorted(all_fields)
    
    # Cabeçalho
    header = ['Data/Hora', 'Nome', 'Email', 'CPF', 'Telefone', 'IP'] + sorted_fields
    writer.writerow(header)
    
    # Dados
    for submission in submissions:
        row = [
            submission.submit_time.strftime('%d/%m/%Y %H:%M'),
            submission.nome_completo or '',
            submission.email or '',
            submission.cpf or '',
            submission.telefone or '',
            submission.user_ip or '',
        ]
        
        # Adicionar campos do formulário
        for field in sorted_fields:
            value = submission.form_data.get(field, '') if submission.form_data else ''
            
            # Converter listas em string
            if isinstance(value, list):
                value = '; '.join(str(v) for v in value)
            elif isinstance(value, dict):
                value = str(value)
            
            row.append(value or '')
        
        writer.writerow(row)
    
    return response