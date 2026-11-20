from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone
from .models import User, Organization, ProviderReviewEvent, Activity, Category, City, Schedule, Plan, ServiceRequest, Review, Campaign, BankAccount


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {'username': 'Nombre de usuario', 'first_name': 'Nombre', 'last_name': 'Apellido', 'email': 'Correo'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este correo ya está registrado.')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'kind', 'city', 'description', 'email', 'phone']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['kind'].disabled = True


class ProviderForm(forms.ModelForm):
    demo_acknowledged = forms.BooleanField(label='Acepto participar en la demostración con datos ficticios.')

    class Meta:
        model = Organization
        fields = ['name', 'city', 'specialty', 'description', 'contact_first_name', 'contact_last_name', 'email', 'phone', 'website']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}
        labels = {'name': 'Nombre de la academia, taller o club'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.filter(active=True, name__in=City.PILOT).order_by('name')
        self.fields['specialty'].queryset = Category.objects.filter(active=True).order_by('name')
        for field in ('specialty', 'phone', 'contact_first_name', 'contact_last_name'):
            self.fields[field].required = True

    def clean_website(self):
        website = self.cleaned_data['website']
        if website:
            URLValidator(schemes=['http', 'https'])(website)
        return website


class ProviderCorrectionForm(ProviderForm):
    revision = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


class ProviderDecisionForm(forms.Form):
    revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    status = forms.ChoiceField(label='Decisión')
    note = forms.CharField(label='Motivo o indicaciones para el solicitante', max_length=1600, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, next_states, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [('', 'Selecciona una opción')] + [
            (status, label) for status, label in ProviderReviewEvent.Status.choices if status in next_states
        ]


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'organization', 'category', 'description', 'age_min', 'age_max', 'sparks', 'price', 'icon', 'active']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        from .access import organizations
        self.fields['organization'].queryset = organizations(user).filter(kind='provider', approved=True, active=True)


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['activity', 'starts_at', 'capacity', 'active']
        widgets = {'starts_at': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'})}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        from .access import activities
        self.fields['activity'].queryset = activities(user)
        if self.instance.pk and self.instance.active:
            self.fields['active'].disabled = True
            self.fields['active'].help_text = 'Para retirar este horario, usa Cancelar horario desde Horarios y cupos.'
        if not self.instance.pk:
            self.fields['activity'].queryset = self.fields['activity'].queryset.filter(
                organization__kind='provider', organization__approved=True, organization__active=True,
            )

    def clean(self):
        data = super().clean()
        occupied = self.instance.capacity - self.instance.available if self.instance.pk else 0
        if data.get('capacity', 0) < occupied:
            self.add_error('capacity', 'No puedes reducir la capacidad por debajo de las plazas ocupadas.')
        if self.instance.pk and self.instance.bookings.exists():
            if data.get('activity') != self.instance.activity or data.get('starts_at') != self.instance.starts_at:
                raise ValidationError('Un horario con reservas conserva su actividad y fecha. Crea otro horario.')
        if not self.instance.pk and data.get('starts_at') and data['starts_at'] <= timezone.now():
            self.add_error('starts_at', 'Elige una fecha futura.')
        if data.get('capacity'):
            self.instance.available = data['capacity'] - occupied
        return data


class ScheduleCancellationForm(forms.Form):
    reason = forms.CharField(
        label='Motivo de la cancelación', max_length=500,
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='El motivo aparecerá en el aviso para los clientes con una reserva vigente.',
    )


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'sparks', 'price', 'description', 'active']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'active']


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'active']


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['kind', 'organization', 'entity_name', 'contact_name', 'contact_email', 'potential_families', 'subject', 'message', 'preferred_date', 'preferred_time']
        widgets = {'message': forms.Textarea(attrs={'rows': 5}), 'preferred_date': forms.DateInput(attrs={'type': 'date'}), 'preferred_time': forms.TimeInput(attrs={'type': 'time'})}

    def __init__(self, *args, agreements_only=False, **kwargs):
        super().__init__(*args, **kwargs)
        if agreements_only:
            self.fields['kind'].choices = [('agreement', dict(ServiceRequest.KINDS)['agreement'])]
            self.fields['kind'].widget = forms.HiddenInput()
            del self.fields['organization']
            return
        self.fields['organization'].queryset = Organization.objects.filter(kind='ally', approved=True, active=True)
        self.fields['kind'].choices = [(key, label) for key, label in ServiceRequest.KINDS if key not in {'quote', 'diagnosis'}]
        self.fields['organization'].help_text = 'Selecciona un aliado solo para asesorías o cotizaciones.'

    def clean(self):
        data = super().clean()
        if data.get('kind') == 'advice' and not data.get('organization'):
            self.add_error('organization', 'Selecciona el aliado destinatario.')
        if data.get('kind') != 'advice' and data.get('organization'):
            self.add_error('organization', 'Los convenios y demos se envían a la administración general.')
        if data.get('preferred_date') and data['preferred_date'] < timezone.localdate():
            self.add_error('preferred_date', 'La fecha no puede estar en el pasado.')
        return data


class ReliefRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            'entity_name', 'relief_topic', 'message', 'preferred_city',
            'relief_channel', 'preferred_date', 'preferred_time', 'contact_name', 'contact_email',
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Cuéntanos qué necesita tu centro.'}),
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }
        labels = {
            'entity_name': 'Nombre de tu centro', 'message': 'Describe tu necesidad',
            'preferred_date': 'Fecha preferida para conversar',
            'preferred_time': 'Hora preferida',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['relief_topic'].required = True
        self.fields['relief_channel'].required = True
        self.fields['preferred_city'].queryset = City.objects.filter(active=True, name__in=City.PILOT).order_by('name')
        for name in ('preferred_date', 'preferred_time', 'preferred_city', 'contact_name', 'contact_email'):
            self.fields[name].label += ' (opcional)'

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data['preferred_date']
        if preferred_date and preferred_date < timezone.localdate():
            raise ValidationError('La fecha no puede estar en el pasado.')
        return preferred_date


class TransitionForm(forms.Form):
    status = forms.ChoiceField(label='Nuevo estado', choices=ServiceRequest.STATUS)
    note = forms.CharField(label='Observación para el solicitante', widget=forms.Textarea(attrs={'rows': 3}))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 4})}


class ResponseForm(forms.Form):
    response = forms.CharField(label='Respuesta del centro', max_length=1600, widget=forms.Textarea(attrs={'rows': 3}))


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'activity', 'daily_budget', 'active']

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        from .access import activities
        self.fields['activity'].queryset = activities(user).filter(active=True)


class WithdrawalForm(forms.Form):
    amount = forms.IntegerField(label='Monto ficticio a solicitar (CLP)', min_value=1)


class BankForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank', 'account_type', 'last_four']

    def clean_last_four(self):
        value = self.cleaned_data['last_four']
        if len(value) != 4 or not value.isascii() or not value.isdigit():
            raise ValidationError('Ingresa exactamente cuatro dígitos ficticios.')
        return value
