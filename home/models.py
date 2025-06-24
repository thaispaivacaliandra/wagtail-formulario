# models.py
from django.db import models
from django.core.exceptions import ValidationError
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey


class FormularioField(AbstractFormField):
    """
    Modelo para campos do formulário com tipos personalizados
    """
    FIELD_TYPES = [
        ('singleline', 'Texto simples'),
        ('multiline', 'Texto longo (textarea)'),
        ('email', 'Email'),
        ('number', 'Número'),
        ('url', 'URL'),
        ('checkbox', 'Checkbox'),
        ('checkboxes', 'Checkboxes múltiplos'),
        ('dropdown', 'Lista suspensa'),
        ('multiselect', 'Seleção múltipla'),
        ('radio', 'Botões de opção'),
        ('date', 'Data'),
        ('datetime', 'Data e hora'),
        ('hidden', 'Campo oculto'),
        ('cpf', 'CPF'),
        ('telefone', 'Telefone'),
        ('senha', 'Senha'),
    ]

    page = ParentalKey('FormularioPage', on_delete=models.CASCADE, related_name='form_fields')
    field_type = models.CharField(
        verbose_name='Tipo do campo',
        max_length=16,
        choices=FIELD_TYPES,
        default='singleline'
    )
    choices = models.TextField(
        verbose_name="Opções",
        blank=True,
        help_text='Necessário para dropdown, checkboxes, etc. Uma opção por linha.'
    )
    default_value = models.CharField(
        verbose_name="Valor padrão",
        max_length=255,
        blank=True,
        help_text='Valor pré-preenchido (opcional)'
    )
    placeholder = models.CharField(
        verbose_name="Placeholder",
        max_length=255,
        blank=True,
        help_text='Texto de exemplo no campo'
    )
    help_text_field = models.CharField(
        verbose_name="Texto de ajuda",
        max_length=255,
        blank=True,
        help_text='Texto explicativo abaixo do campo'
    )
    section_title = models.CharField(
        verbose_name="Título da seção",
        max_length=255,
        blank=True,
        help_text='Título grande acima da pergunta'
    )
    ordem = models.PositiveIntegerField(
        verbose_name="Ordem",
        default=0,
        help_text='Ordem de exibição do campo'
    )

    panels = [
        FieldPanel('label'),
        FieldPanel('field_type'),
        FieldPanel('required'),
        FieldPanel('section_title'),
        FieldPanel('help_text_field'),
        FieldPanel('placeholder'),
        FieldPanel('choices', 
                  help_text='📋 APENAS para: Dropdown, Radio, Checkboxes. Uma opção por linha.'),
        FieldPanel('default_value', 
                  help_text='🚫 NÃO usar para: Checkboxes múltiplos'),
        FieldPanel('ordem'),
    ]

    def get_choices_list(self):
        """
        Retorna as opções como uma lista
        """
        if not self.choices:
            return []
        
        choices = []
        for line in self.choices.split('\n'):
            line = line.strip()
            if line:
                choices.append(line)
        return choices

    class Meta:
        ordering = ['ordem', 'id']

    def clean(self):
        super().clean()
        if self.field_type in ['dropdown', 'multiselect', 'checkboxes', 'radio']:
            if not self.choices:
                raise ValidationError({
                    'choices': 'Este tipo de campo requer opções.'
                })
        
        # Limpar valor padrão para checkboxes múltiplos
        if self.field_type == 'checkboxes':
            self.default_value = ''


class FormularioPage(AbstractEmailForm):
    """
    Página principal do formulário
    """
    intro = RichTextField(
        verbose_name="Introdução",
        blank=True,
        help_text='Texto de introdução do formulário'
    )
    thank_you_text = RichTextField(
        verbose_name="Texto de agradecimento",
        blank=True,
        help_text='Texto exibido após envio do formulário'
    )
    
    # Configurações visuais
    background_color = models.CharField(
        verbose_name="Cor de fundo",
        max_length=7,
        default="#ffffff",
        help_text='Código hexadecimal da cor (ex: #ffffff)'
    )
    primary_color = models.CharField(
        verbose_name="Cor primária",
        max_length=7,
        default="#2A5E2C",
        help_text='Cor dos botões e elementos principais'
    )
    show_progress_bar = models.BooleanField(
        verbose_name="Mostrar barra de progresso",
        default=True
    )
    form_title = models.CharField(
        verbose_name="Título do formulário",
        max_length=255,
        default="Formulário de Inscrição"
    )
    form_subtitle = models.CharField(
        verbose_name="Subtítulo",
        max_length=255,
        blank=True
    )
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Logo/Imagem de boas-vindas'
    )

    background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Imagem de fundo',
        help_text='Imagem de fundo para o formulário'
    )

    thank_you_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Imagem de agradecimento'
    )

    content_panels = AbstractEmailForm.content_panels + [
        MultiFieldPanel([
            FieldPanel('form_title'),
            FieldPanel('form_subtitle'),
            FieldPanel('logo'),
        ], "Tela de boas-vindas"),
        
        FieldPanel('intro'),
        
        InlinePanel('form_fields', label="Campos do formulário"),
        
        MultiFieldPanel([
            FieldPanel('thank_you_text'),
            FieldPanel('thank_you_image'),
        ], "Tela de agradecimento"),
        
        MultiFieldPanel([
            FieldPanel('background_image'),
            FieldPanel('background_color'),
            FieldPanel('primary_color'),
            FieldPanel('show_progress_bar'),
        ], "Aparência"),
        
        MultiFieldPanel([
            FieldPanel('to_address', classname="col6"),
            FieldPanel('from_address', classname="col6"),
            FieldPanel('subject'),
        ], "Configurações de email"),
    ]

    def get_form_fields(self):
        """
        Retorna os campos do formulário ordenados
        """
        return self.form_fields.all().order_by('ordem', 'id')

    def process_form_submission(self, form):
        """
        Override para salvar dados estruturados
        """
        # Chamar o método pai para enviar email
        result = super().process_form_submission(form)
        
        # Extrair dados específicos
        form_data = form.cleaned_data
        nome_completo = form_data.get('nome_completo', '')
        email = form_data.get('email', '')
        cpf = form_data.get('cpf', '')
        telefone = form_data.get('telefone', '') or form_data.get('celular', '')
        
        # Salvar submissão estruturada
        FormularioSubmission.objects.create(
            page=self,
            form_data=form_data,
            nome_completo=nome_completo,
            email=email,
            cpf=cpf,
            telefone=telefone,
            user_ip=self.get_client_ip(),
            user_agent=self.get_user_agent(),
        )
        
        return result
    
    def get_client_ip(self):
        """Pega o IP do usuário da requisição atual"""
        # Isso será definido no contexto da view
        return getattr(self, '_current_request_ip', None)
    
    def get_user_agent(self):
        """Pega o User Agent da requisição atual"""
        return getattr(self, '_current_request_user_agent', '')

    def serve(self, request, *args, **kwargs):
        """
        Override para capturar dados da requisição
        """
        # Guardar dados da requisição para usar no process_form_submission
        self._current_request_ip = self._get_client_ip(request)
        self._current_request_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return super().serve(request, *args, **kwargs)
    
    def _get_client_ip(self, request):
        """Extrai o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
        
        """
        Gera a classe do formulário dinamicamente baseada nos campos
        """
        from django import forms
        from django.core.validators import validate_email
        import re

        form_class = super().get_form_class()
        
        # Adicionar validadores customizados
        def validate_cpf(value):
            # Remove caracteres não numéricos
            cpf = re.sub(r'[^0-9]', '', value)
            if len(cpf) != 11 or cpf == cpf[0] * 11:
                raise forms.ValidationError('CPF inválido')
            
            # Validação dos dígitos verificadores
            def calculate_digit(cpf, weight):
                sum_result = sum(int(cpf[i]) * weight[i] for i in range(len(weight)))
                remainder = sum_result % 11
                return 0 if remainder < 2 else 11 - remainder

            if int(cpf[9]) != calculate_digit(cpf, list(range(10, 1, -1))):
                raise forms.ValidationError('CPF inválido')
            if int(cpf[10]) != calculate_digit(cpf, list(range(11, 1, -1))):
                raise forms.ValidationError('CPF inválido')

        def validate_telefone(value):
            # Remove caracteres não numéricos
            phone = re.sub(r'[^0-9]', '', value)
            if len(phone) not in [10, 11]:
                raise forms.ValidationError('Telefone deve ter 10 ou 11 dígitos')

        # Aplicar validadores aos campos
        for field in form_class.base_fields.values():
            if hasattr(field, 'clean_name'):
                field_obj = self.form_fields.filter(clean_name=field.clean_name).first()
                if field_obj:
                    if field_obj.field_type == 'cpf':
                        field.validators.append(validate_cpf)
                    elif field_obj.field_type == 'telefone':
                        field.validators.append(validate_telefone)

        return form_class

    class Meta:
        verbose_name = "Formulário Personalizado"
        verbose_name_plural = "Formulários Personalizados"


# Para salvar as submissões com dados estruturados
class FormularioSubmission(models.Model):
    """
    Modelo para armazenar submissões com dados estruturados
    """
    page = models.ForeignKey(FormularioPage, on_delete=models.CASCADE)
    form_data = models.JSONField(verbose_name="Dados do formulário")
    submit_time = models.DateTimeField(auto_now_add=True)
    user_ip = models.GenericIPAddressField(verbose_name="IP do usuário", null=True, blank=True)
    user_agent = models.TextField(verbose_name="User Agent", blank=True)
    
    # Campos específicos que você pode querer indexar
    nome_completo = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    cpf = models.CharField(max_length=14, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = "Submissão do Formulário"
        verbose_name_plural = "Submissões do Formulário"
        ordering = ['-submit_time']

    def __str__(self):
        return f"{self.nome_completo or 'Sem nome'} - {self.submit_time.strftime('%d/%m/%Y %H:%M')}"