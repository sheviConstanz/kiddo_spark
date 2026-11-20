"""Presentation content for the five areas in the reference Alivios B2B."""
from .models import Organization


Area = Organization.ReliefArea
AREA_CONTENT = {
    Area.ACCOUNTING: ('list', 'ks-mint', 'SII, F29, boletas y orden financiero.', 'tax'),
    Area.LEGAL: ('briefcase', 'ks-lilac', 'Contratos, datos y protocolos infantiles.', 'contracts'),
    Area.MAINTENANCE: ('store', 'ks-peach', 'Tatamis, canchas, piscinas y climatización.', 'maintenance'),
    Area.INSURANCE: ('shield', 'ks-cream', 'Accidentes, responsabilidad civil y prevención.', 'insurance'),
    Area.MARKETING: ('chart', 'ks-mint', 'Contenido, campañas y visibilidad del centro.', 'media'),
}

REFERENCE_AREAS = {
    'Contabilidad': Area.ACCOUNTING, 'Legal': Area.LEGAL, 'Mantención': Area.MAINTENANCE,
    'Seguros': Area.INSURANCE, 'Marketing': Area.MARKETING,
}

DIAGNOSTIC_QUESTIONS = {
    Area.LEGAL: 'Contratos y consentimientos de las familias',
    Area.ACCOUNTING: 'Declaraciones y orden tributario',
    Area.MAINTENANCE: 'Mantención preventiva de los espacios',
}
