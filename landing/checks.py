"""System checks that surface unconfirmed business details.

Registered in landing/apps.py so they run on every ``manage.py check`` and
``manage.py check --deploy``, which is what stops a placeholder from reaching
production silently.
"""
from django.core.checks import Warning as CheckWarning
from django.core.checks import register

from .company import REQUIRED_BEFORE_PUBLISH, COMPANY, Unknown

W001 = 'landing.W001'


@register('legal')
def check_company_details(app_configs, **kwargs):
    missing = [k for k in REQUIRED_BEFORE_PUBLISH if isinstance(COMPANY.get(k), Unknown)]
    if not missing:
        return []
    return [
        CheckWarning(
            'Legal pages contain unconfirmed business details.',
            hint=(
                'These keys in landing/company.py are still placeholders and render as '
                '"[[NEEDS CONFIRMATION: ...]]" in the published legal pages: '
                + ', '.join(missing)
                + '. A registered mailing address is required by GDPR Art. 13 and CASL; '
                'a named Privacy Officer is required by PIPEDA Principle 1.'
            ),
            id=W001,
        )
    ]
