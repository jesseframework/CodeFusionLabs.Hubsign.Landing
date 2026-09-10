"""Business identity, in one place.

The footer, the privacy policy, the terms and the cookie policy all have to
state the same company details. Keeping them here means they cannot drift.

Anything not yet confirmed is a ``Unknown`` instance rather than a plausible
guess. Those render as a loud inline marker in the page and are reported by
``manage.py check`` (see landing/checks.py), so an unconfirmed detail cannot be
published unnoticed. Publishing a placeholder is recoverable; publishing an
invented corporate address in a privacy policy is not.

Jurisdiction note: HubSign-Pricing-Plan.md section 6 ("Legal check required")
records that Future Edge Technology Inc. is an Ontario company, which is what
sets the governing law in templates/legal/terms.html and the privacy framework
(PIPEDA + Quebec Law 25) in templates/legal/privacy.html.
"""


class Unknown:
    """A business detail that has not been confirmed yet.

    Renders as a visible marker so it is obvious in the page, and is truthy so
    templates do not silently skip the surrounding markup.
    """

    def __init__(self, what):
        self.what = what

    def __str__(self):
        return f'[[NEEDS CONFIRMATION: {self.what}]]'

    def __bool__(self):
        return True

    @property
    def unresolved(self):
        return True


def _known(value):
    return not isinstance(value, Unknown)


COMPANY = {
    # --- Confirmed ---
    'legal_name': 'Future Edge Technology Inc.',
    'short_name': 'Future Edge Technology',
    'product': 'HubSign',
    'site_domain': 'hubsign.io',
    'app_domain': 'app.hubsign.io',
    'docs_url': 'https://docs.hubsign.io',
    'jurisdiction': 'Ontario, Canada',
    'governing_law': 'the Province of Ontario and the federal laws of Canada applicable therein',
    'courts': 'the courts of the Province of Ontario',
    'sales_email': 'sales@hubsign.io',
    'support_email': 'support@hubsign.io',

    # --- Not confirmed: see the module docstring ---
    # Required by PIPEDA (openness / individual access), GDPR Art. 13, and CASL
    # (a physical mailing address must appear in any commercial electronic message).
    'registered_address': Unknown('registered mailing address'),
    'corporation_number': Unknown('Ontario corporation number'),
    # PIPEDA Principle 1 requires a named, reachable accountable individual.
    'privacy_officer': Unknown('name/title of the designated Privacy Officer'),
    'privacy_email': Unknown('privacy contact address, e.g. privacy@hubsign.io'),
    # The published number is a Michigan (810) area code on an Ontario company.
    'phone_display': '+1 810-626-EDGE',
    'phone_tel': '+18106263343',
    'phone_note': Unknown('whether the +1 810 (Michigan) number is correct for an Ontario entity'),
}

# Detail keys that must be resolved before the legal pages are published.
REQUIRED_BEFORE_PUBLISH = (
    'registered_address',
    'corporation_number',
    'privacy_officer',
    'privacy_email',
)


def unresolved_details():
    """Return ``(key, Unknown)`` pairs still needing confirmation."""
    return [(k, v) for k, v in COMPANY.items() if isinstance(v, Unknown)]


def is_publishable():
    """True when every detail the legal pages depend on has been filled in."""
    return all(_known(COMPANY[k]) for k in REQUIRED_BEFORE_PUBLISH)
