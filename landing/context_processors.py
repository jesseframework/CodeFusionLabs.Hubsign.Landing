"""Template context available on every page."""
from .company import COMPANY


def company(request):
    """Business details and the legal-page index.

    Both are needed by the footer, which renders on every page, so they are
    injected globally rather than added to each view's context.
    """
    from .legal import LEGAL_PAGES  # imported lazily: legal.py imports views machinery

    return {
        'company': COMPANY,
        'legal_pages': LEGAL_PAGES,
    }
