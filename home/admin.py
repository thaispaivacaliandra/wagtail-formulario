# home/admin.py
import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import FormularioSubmission

@admin.register(FormularioSubmission)
class FormularioSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'nome_completo', 
        'email', 
        'cpf', 
        'submit_time_formatted', 
        'page_title',
    ]
    list_filter = [
        'page', 
        'submit_time',
    ]
    search_fields = [
        'nome_completo', 
        'email', 
        'cpf', 
        'telefone'
    ]
    readonly_fields = [
        'submit_time', 
        'form_data_formatted', 
        'user_ip', 
        'user_agent'
    ]
    date_hierarchy = 'submit_time'
    list_per_page = 50
    
    # Ações de exportação
    actions = ['export_to_csv']
    
    def submit_time_formatted(self, obj):
        """Formata a data/hora de submissão"""
        return obj.submit_time.strftime('%d/%m/%Y às %H:%M')
    submit_time_formatted.short_description = "Data/Hora"
    
    def page_title(self, obj):
        """Título da página do formulário"""
        return obj.page.title
    page_title.short_description = "Formulário"
    
    def form_data_formatted(self, obj):
        """Exibe os dados do formulário formatados"""
        if not obj.form_data:
            return "Nenhum dado"
            
        html = "<table style='width:100%; border-collapse: collapse;'>"
        for key, value in obj.form_data.items():
            # Formatar listas (checkboxes múltiplos)
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            
            html += f"""
            <tr style='border-bottom: 1px solid #ddd;'>
                <td style='padding: 8px; font-weight: bold; width: 30%;'>{key}:</td>
                <td style='padding: 8px;'>{value}</td>
            </tr>
            """
        html += "</table>"
        return mark_safe(html)
    form_data_formatted.short_description = "Dados do Formulário"
    
    def export_to_csv(self, request, queryset):
        """Exportar submissões selecionadas para CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="submissoes_formulario.csv"'
        
        # BOM para Excel reconhecer UTF-8
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Coletar todos os campos únicos de todas as submissões
        all_fields = set()
        for submission in queryset:
            if submission.form_data:
                all_fields.update(submission.form_data.keys())
        
        # Ordenar campos
        sorted_fields = sorted(all_fields)
        
        # Cabeçalho
        header = ['Data/Hora', 'Formulário', 'Nome', 'Email', 'CPF', 'Telefone', 'IP'] + sorted_fields
        writer.writerow(header)
        
        # Dados
        for submission in queryset:
            row = [
                submission.submit_time.strftime('%d/%m/%Y %H:%M'),
                submission.page.title,
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
        
        self.message_user(request, f'Exportados {queryset.count()} registros para CSV.')
        return response
    
    export_to_csv.short_description = "📥 Exportar selecionados para CSV"
    
    def has_add_permission(self, request):
        """Não permitir adicionar submissões manualmente"""
        return False