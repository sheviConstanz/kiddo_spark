from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class User(AbstractUser):
    email = models.EmailField('correo', unique=True)
    credits = models.PositiveIntegerField('Sparks', default=0)
    points = models.PositiveIntegerField('puntos', default=0)
    provider_applicant = models.BooleanField('solicitante de alta de proveedor', default=False, editable=False)

    class Meta(AbstractUser.Meta):
        constraints = [models.UniqueConstraint(Lower('email'), name='unique_user_email_casefold')]
        permissions = [('operate_platform', 'Puede operar el catálogo y las solicitudes de la plataforma')]

    @property
    def role(self):
        if self.is_superuser:
            return 'superadmin'
        if self.is_staff:
            return 'admin' if self.has_perm('core.operate_platform') else 'provider'
        return 'applicant' if self.provider_applicant else 'client'

    @property
    def role_label(self):
        return {
            'superadmin': 'Superadministrador',
            'admin': 'Administrador de plataforma',
            'provider': 'Proveedor',
            'applicant': 'Proveedor en incorporación',
            'client': 'Cliente',
        }[self.role]


class Named(models.Model):
    name = models.CharField('nombre', max_length=140, unique=True)
    active = models.BooleanField('activo', default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class City(Named):
    PILOT = ('Viña del Mar', 'Valparaíso', 'Quilpué', 'Villa Alemana')

    class Meta:
        verbose_name = 'comuna'


class Category(Named):
    class Meta:
        verbose_name = 'categoría'


class Organization(models.Model):
    class ReliefArea(models.TextChoices):
        ACCOUNTING = 'accounting', 'Contabilidad y tributación'
        LEGAL = 'legal', 'Legal y cumplimiento'
        MAINTENANCE = 'maintenance', 'Mantención'
        INSURANCE = 'insurance', 'Seguros y prevención'
        MARKETING = 'marketing', 'Marketing y audiovisual'

    origin_key = models.CharField(max_length=180, null=True, blank=True, unique=True, editable=False)
    KINDS = [('provider', 'Academia / proveedor'), ('company', 'Empresa'), ('school', 'Colegio'), ('ally', 'Aliado de apoyo')]
    name = models.CharField('nombre', max_length=160)
    kind = models.CharField('tipo', max_length=16, choices=KINDS, default='provider')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='comuna')
    description = models.TextField('descripción', blank=True)
    email = models.EmailField('correo de contacto')
    phone = models.CharField('teléfono', max_length=32, blank=True)
    contact_first_name = models.CharField('nombre del contacto', max_length=80, blank=True)
    contact_last_name = models.CharField('apellido del contacto', max_length=80, blank=True)
    website = models.URLField('sitio web o red social', blank=True)
    specialty = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, verbose_name='categoría del centro')
    relief_area = models.CharField('área de apoyo B2B', max_length=16, choices=ReliefArea.choices, blank=True)
    relief_focus = models.CharField('especialidad del aliado', max_length=160, blank=True)
    relief_topics = models.CharField('servicios del aliado, separados por punto y coma', max_length=320, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='registered_organizations')
    administrators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='organizations', verbose_name='administradores')
    approved = models.BooleanField('aprobado', default=False)
    active = models.BooleanField('activo', default=True)

    @property
    def review_stage_label(self):
        return ProviderReviewEvent.Status(self.review_stage).label

    @property
    def relief_topic_list(self):
        return [topic.strip() for topic in self.relief_topics.split(';') if topic.strip()]

    def __str__(self):
        return self.name


class ProviderReviewEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Solicitud recibida'
        REVIEWING = 'reviewing', 'En revisión'
        OBSERVED = 'observed', 'Requiere corrección'
        REJECTED = 'rejected', 'Rechazada'
        APPROVED = 'approved', 'Aprobada'

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='review_events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=12, choices=Status.choices)
    note = models.TextField(blank=True, max_length=1600)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pk']


class Activity(models.Model):
    origin_key = models.CharField(max_length=180, null=True, blank=True, unique=True, editable=False)
    name = models.CharField('nombre', max_length=160)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='activities', verbose_name='centro')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='categoría')
    description = models.TextField('descripción')
    age_min = models.PositiveSmallIntegerField('edad mínima', default=5, validators=[MaxValueValidator(18)])
    age_max = models.PositiveSmallIntegerField('edad máxima', default=14, validators=[MaxValueValidator(18)])
    sparks = models.PositiveIntegerField('Sparks por reserva', default=4, validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField('valor referencial CLP (demo)', default=0)
    icon = models.CharField('símbolo', max_length=12, default='✨')
    active = models.BooleanField('publicada', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(age_max__gte=models.F('age_min')), name='activity_age_order'), models.CheckConstraint(condition=Q(sparks__gte=1), name='activity_positive_sparks')]

    def __str__(self):
        return self.name


class Schedule(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT, related_name='schedules', verbose_name='actividad')
    starts_at = models.DateTimeField('fecha y hora')
    capacity = models.PositiveIntegerField('capacidad', validators=[MinValueValidator(1)])
    available = models.PositiveIntegerField('cupos disponibles')
    active = models.BooleanField('habilitado', default=True)
    cancelled_at = models.DateTimeField('cancelado el', null=True, blank=True, editable=False)
    cancellation_reason = models.CharField('motivo de cancelación', max_length=500, blank=True, editable=False)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(available__lte=models.F('capacity')), name='schedule_capacity'), models.CheckConstraint(condition=Q(capacity__gte=1), name='schedule_positive_capacity')]

    def __str__(self):
        return f'{self.activity} · {self.starts_at:%d/%m/%Y %H:%M}'


class Plan(Named):
    origin_key = models.CharField(max_length=180, null=True, blank=True, unique=True, editable=False)
    sparks = models.PositiveIntegerField('Sparks', validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField('valor referencial CLP', default=0)
    description = models.TextField('descripción', blank=True)


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    sparks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    class Status(models.TextChoices):
        RESERVED = 'reserved', 'Reservado'
        CANCELLED = 'cancelled', 'Cancelado'

    STATUS = Status.choices
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, related_name='bookings')
    sparks = models.PositiveIntegerField()
    amount = models.PositiveIntegerField('monto referencial CLP')
    status = models.CharField(max_length=12, choices=STATUS, default=Status.RESERVED)
    attendance_recorded = models.BooleanField('asistencia registrada', default=False, editable=False)
    points_awarded = models.BooleanField('puntos acreditados', default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'schedule'], condition=Q(status='reserved', attendance_recorded=False),
                name='one_active_booking',
            ),
            models.CheckConstraint(condition=Q(status__in=('reserved', 'cancelled')), name='booking_valid_status'),
        ]

    def __str__(self):
        return f'KS-{self.pk} · {self.schedule.activity}'


class Notification(models.Model):
    class Kind(models.TextChoices):
        RESERVED = 'reserved', 'Reserva registrada'
        BOOKING_RECEIVED = 'booking_received', 'Nueva reserva en tu centro'
        BOOKING_CANCELLED = 'booking_cancelled', 'Reserva cancelada'
        SCHEDULE_CANCELLED = 'schedule_cancelled', 'Horario cancelado'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, null=True, blank=True)
    kind = models.CharField(max_length=18, choices=Kind.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        indexes = [models.Index(fields=['recipient', 'read_at'], name='notification_recipient_read')]


class Movement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='movements')
    delta = models.IntegerField('Sparks')
    description = models.CharField('concepto', max_length=180)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.PROTECT)
    membership = models.ForeignKey(Membership, null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)


class ServiceRequest(models.Model):
    KINDS = [
        ('agreement', 'Convenio empresa / colegio'), ('demo', 'Demostración corporativa'),
        ('advice', 'Asesoría'), ('quote', 'Cotización'), ('diagnosis', 'Orientación inicial'),
    ]
    RELIEF_KINDS = ('advice', 'quote', 'diagnosis')
    RELIEF_TOPICS = [
        ('orientation', 'Ayuda para definir mi necesidad'),
        ('tax', 'Formalización y SII'),
        ('contracts', 'Contratos con apoderados'),
        ('safety', 'Protocolos de seguridad infantil'),
        ('maintenance', 'Mantención preventiva'),
        ('insurance', 'Seguro de accidentes'),
        ('media', 'Producción audiovisual'),
        ('other', 'Otra necesidad'),
    ]
    RELIEF_CHANNELS = [
        ('video', 'Videollamada'), ('phone', 'Teléfono'), ('in_person', 'Presencial'),
    ]
    STATUS = [('pending', 'Pendiente'), ('reviewing', 'En revisión'), ('approved', 'Aprobada'), ('rejected', 'Rechazada'), ('completed', 'Completada')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='service_requests')
    kind = models.CharField('tipo', max_length=16, choices=KINDS)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, blank=True, verbose_name='aliado destinatario')
    entity_name = models.CharField('empresa, colegio o centro solicitante', max_length=160)
    contact_name = models.CharField('nombre del contacto ficticio', max_length=140, blank=True)
    contact_email = models.EmailField('correo del contacto ficticio', blank=True)
    potential_families = models.PositiveIntegerField('familias potenciales (estimación demo)', null=True, blank=True)
    subject = models.CharField('asunto', max_length=180)
    message = models.TextField('necesidad / mensaje')
    preferred_date = models.DateField('fecha preferida', null=True, blank=True)
    preferred_time = models.TimeField('hora preferida', null=True, blank=True)
    preferred_city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True, verbose_name='comuna preferida')
    relief_topic = models.CharField('problema o servicio', max_length=16, choices=RELIEF_TOPICS, blank=True)
    relief_channel = models.CharField('canal preferido', max_length=16, choices=RELIEF_CHANNELS, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'SOL-{self.pk} · {self.subject}'


class RequestEvent(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.PROTECT, related_name='events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=12, choices=ServiceRequest.STATUS)
    note = models.TextField('observación')
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name='review')
    rating = models.PositiveSmallIntegerField('calificación', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('opinión', max_length=1600)
    response = models.TextField('respuesta del centro', blank=True, max_length=1600)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name='review_rating_range')]


class Settlement(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='settlements')
    amount = models.PositiveIntegerField('saldo referencial demo')
    created_at = models.DateTimeField(auto_now_add=True)


class Withdrawal(models.Model):
    STATUS = [('pending', 'Pendiente'), ('paid', 'Completada (simulada)'), ('rejected', 'Rechazada')]
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='withdrawals')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField('monto CLP demo', validators=[MinValueValidator(1)])
    status = models.CharField(max_length=12, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class BankAccount(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.PROTECT)
    bank = models.CharField('banco ficticio', max_length=100)
    account_type = models.CharField('tipo de cuenta demo', max_length=100)
    last_four = models.CharField('últimos cuatro dígitos ficticios', max_length=4)


class Campaign(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT, related_name='campaigns', verbose_name='actividad')
    name = models.CharField('nombre', max_length=160)
    daily_budget = models.PositiveIntegerField('presupuesto diario CLP demo', validators=[MinValueValidator(1000)])
    active = models.BooleanField('activa', default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=40)
    target = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'activity'], name='unique_favorite')]
