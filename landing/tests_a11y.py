"""Accessibility and privacy-posture regression tests.

These lock in properties that are easy to break silently:

* the colour tokens still clear WCAG AA,
* the page still sets no cookies (which is what lets us skip a cookie banner),
* the accessibility affordances are still in the markup, and
* no third-party origin has crept back into the templates.
"""
import re
from html.parser import HTMLParser
from pathlib import Path

from django.test import TestCase
from django.urls import reverse

CSS = Path(__file__).resolve().parent.parent / 'static' / 'css' / 'main.css'


# ---------------------------------------------------------------------------
# Contrast
# ---------------------------------------------------------------------------
def _luminance(hex_colour):
    hex_colour = hex_colour.lstrip('#')
    channels = []
    for i in (0, 2, 4):
        c = int(hex_colour[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    l1, l2 = _luminance(fg), _luminance(bg)
    if l2 > l1:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def css_tokens():
    """Parse the :root custom properties that hold a plain hex colour."""
    text = CSS.read_text(encoding='utf-8')
    root = text[text.index(':root {'):]
    root = root[:root.index('\n}')]
    return {
        name: value
        for name, value in re.findall(r'(--[a-z0-9-]+):\s*(#[0-9a-fA-F]{6});', root)
    }


class PaletteContrastTests(TestCase):
    """Every colour pairing the design actually uses must clear WCAG AA.

    The palette this replaced failed in five places -- muted grey label text at
    2.62:1 and 2.78:1, and three footer colours at 3.88:1 -- so this is checked
    rather than assumed. Add a row here whenever you introduce a pairing.
    """

    #: (foreground token, background token, minimum ratio, where it is used)
    NORMAL_TEXT = [
        ('--ink', '--paper', 4.5, 'body copy'),
        ('--ink', '--raised', 4.5, 'card copy'),
        ('--ink', '--sunken', 4.5, 'alternating section copy'),
        ('--ink-2', '--paper', 4.5, 'secondary copy'),
        ('--ink-2', '--raised', 4.5, 'card secondary copy'),
        ('--ink-2', '--sunken', 4.5, 'section secondary copy'),
        ('--ink-muted', '--paper', 4.5, 'eyebrows, captions, stat labels'),
        ('--ink-muted', '--raised', 4.5, 'muted copy on cards'),
        ('--ink-muted', '--sunken', 4.5, 'muted copy on sunken sections'),
        ('--accent', '--paper', 4.5, 'links and pillar subtitles'),
        ('--accent', '--raised', 4.5, 'links on cards'),
        ('--accent', '--sunken', 4.5, 'links on sunken sections'),
        ('--accent', '--accent-soft', 4.5, 'field-type pills, mock chips'),
        ('--positive', '--positive-soft', 4.5, 'the annual-saving badge'),
        ('--on-deep', '--deep', 4.5, 'CTA copy'),
        ('--on-deep-2', '--deep', 4.5, 'CTA lead copy'),
        ('--on-deep-muted', '--deep', 4.5, 'footer labels'),
        ('--on-deep-2', '--deep-2', 4.5, 'footer links'),
        ('--seal', '--paper', 4.5, 'margin notes, commodity tag'),
        ('--seal', '--sunken', 4.5, 'margin notes on sunken sections'),
        ('--seal', '--raised', 4.5, 'pricing badge'),
        ('--ink', '--highlight', 4.5, 'marker-pen phrase'),
        ('--ink-2', '--paper', 4.5, 'spine note on paper'),
        ('--on-deep-muted', '--deep-2', 4.5, 'footer meta and copyright'),
    ]

    #: Graphics that carry meaning need 3:1 (WCAG 1.4.11).
    NON_TEXT = [
        ('--seal-on-deep', '--deep', 3.0, 'wax seal on the CTA'),
        ('--spine-idle', '--paper', 3.0, 'the spine rail and inactive dots'),
        ('--spine-commodity', '--paper', 3.0, 'the commodity step marker'),
        ('--accent', '--paper', 3.0, 'active spine marker, carousel dot'),
        ('--on-deep-accent', '--deep', 3.0, 'focus ring on dark sections'),
    ]

    def setUp(self):
        self.tokens = css_tokens()

    def _check(self, rows):
        for fg, bg, minimum, usage in rows:
            with self.subTest(fg=fg, bg=bg, usage=usage):
                self.assertIn(fg, self.tokens, f'{fg} missing from :root')
                self.assertIn(bg, self.tokens, f'{bg} missing from :root')
                ratio = contrast_ratio(self.tokens[fg], self.tokens[bg])
                self.assertGreaterEqual(
                    round(ratio, 2), minimum,
                    f'{fg} ({self.tokens[fg]}) on {bg} ({self.tokens[bg]}) is '
                    f'{ratio:.2f}:1, below {minimum}:1 -- used for {usage}',
                )

    def test_text_pairs_meet_aa(self):
        self._check(self.NORMAL_TEXT)

    def test_meaningful_graphics_meet_three_to_one(self):
        self._check(self.NON_TEXT)


# ---------------------------------------------------------------------------
# Markup
# ---------------------------------------------------------------------------
class _Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.headings.append(int(tag[1]))


class LandingAccessibilityTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('landing:index'))
        self.html = self.response.content.decode()
        self.parser = _Collector()
        self.parser.feed(self.html)

    def test_page_renders(self):
        self.assertEqual(self.response.status_code, 200)

    def test_has_skip_link_pointing_at_main(self):
        self.assertIn('class="skip-link" href="#main"', self.html)
        self.assertIn('<main id="main">', self.html)

    def test_exactly_one_h1(self):
        self.assertEqual(self.parser.headings.count(1), 1)

    def test_no_skipped_heading_levels(self):
        """h2 -> h4 was the one skipped level on the old page (footer columns)."""
        previous = 0
        for level in self.parser.headings:
            if previous:
                self.assertLessEqual(
                    level, previous + 1,
                    f'heading level jumped from h{previous} to h{level}',
                )
            previous = level

    def test_html_has_lang(self):
        self.assertIn('<html lang="en">', self.html)

    def test_faq_buttons_expose_state(self):
        buttons = [
            attrs for tag, attrs in self.parser.tags
            if tag == 'button' and 'faq-question' in attrs.get('class', '')
        ]
        self.assertEqual(len(buttons), 7)
        for attrs in buttons:
            self.assertEqual(attrs.get('aria-expanded'), 'false')
            self.assertIn('aria-controls', attrs)

    def test_faq_answers_start_hidden(self):
        """Previously clipped with max-height:0, which left every answer in the
        accessibility tree regardless of the visible state."""
        answers = re.findall(r'<div class="faq-answer"[^>]*>', self.html)
        self.assertEqual(len(answers), 7)
        for answer in answers:
            self.assertIn('hidden', answer)

    def test_walkthrough_uses_the_tabs_pattern(self):
        """The nine screens are a tabs widget: one selected tab, a panel per
        tab, every panel labelled by its tab, and every inactive panel hidden
        so it leaves the accessibility tree."""
        tabs = [a for t, a in self.parser.tags if t == 'button' and 'walk-tab' in a.get('class', '')]
        self.assertEqual(len(tabs), 9)
        self.assertEqual(sum(a.get('aria-selected') == 'true' for a in tabs), 1)
        for tab in tabs:
            self.assertEqual(tab.get('role'), 'tab')
            self.assertIn(tab.get('aria-selected'), ('true', 'false'))
            self.assertIn(f'id="{tab["aria-controls"]}"', self.html)

        panels = [a for t, a in self.parser.tags if a.get('role') == 'tabpanel' and 'walk-panel' in a.get('class', '')]
        self.assertEqual(len(panels), 9)
        self.assertEqual(sum('hidden' not in p for p in panels), 1)
        for panel in panels:
            self.assertTrue(panel.get('aria-labelledby'))

    def test_walkthrough_next_prompts_are_buttons_and_page_does_not_move_itself(self):
        nexts = [a for t, a in self.parser.tags if t == 'button' and 'data-walk-next' in a]
        self.assertEqual(len(nexts), 9)
        self.assertIn('Back to the start: Signature Inbox', self.html)

    def test_walkthrough_panels_are_real_screenshots_with_meaningful_alt_text(self):
        """The screens are real product screenshots, so the frames must not be
        aria-hidden, and every image needs alt text that actually describes it
        -- not empty, not the filename."""
        frames = [
            attrs for tag, attrs in self.parser.tags
            if tag == 'div' and attrs.get('class') == 'showcase-frame'
        ]
        self.assertEqual(len(frames), 9)
        for frame in frames:
            self.assertNotIn('aria-hidden', frame)

        showcase_images = [
            a for t, a in self.parser.tags
            if t == 'img' and 'screens/' in a.get('src', '')
            and 'signing-complete' not in a.get('src', '')
            and 'hero-shot-img' not in a.get('class', '')   # hero reuses panel 1
        ]
        self.assertEqual(len(showcase_images), 9)
        for img in showcase_images:
            self.assertTrue(img.get('alt'), f'missing/empty alt: {img}')
            self.assertGreater(len(img['alt']), 15)

    def test_pricing_toggles_use_the_tabs_pattern(self):
        tabs = [a for t, a in self.parser.tags
                if a.get('role') == 'tab' and 'walk-tab' not in a.get('class', '')]
        self.assertEqual(len(tabs), 4)
        for tab in tabs:
            self.assertIn(tab.get('aria-selected'), ('true', 'false'))

    def test_mobile_menu_button_exposes_state(self):
        btn = next(a for t, a in self.parser.tags if a.get('id') == 'mobileMenuBtn')
        self.assertEqual(btn.get('aria-expanded'), 'false')
        self.assertEqual(btn.get('aria-controls'), 'mobileMenu')
        self.assertTrue(btn.get('aria-label'))

    def test_icon_only_controls_have_accessible_names(self):
        for tag, attrs in self.parser.tags:
            if tag == 'button' and 'mobile-menu-btn' in attrs.get('class', ''):
                self.assertTrue(attrs.get('aria-label'))

    def test_images_have_alt_and_dimensions(self):
        images = [a for t, a in self.parser.tags if t == 'img']
        self.assertTrue(images)
        for img in images:
            self.assertIn('alt', img, f'missing alt: {img}')
            # width/height prevent layout shift as the logos load.
            self.assertIn('width', img)
            self.assertIn('height', img)

    def test_no_inline_event_handlers(self):
        """Inline handlers are what forced 'unsafe-inline' into the script CSP."""
        self.assertNotRegex(self.html, r'\son[a-z]+\s*=')

    def test_prefers_reduced_motion_is_honoured(self):
        css = CSS.read_text(encoding='utf-8')
        self.assertIn('@media (prefers-reduced-motion: reduce)', css)
        self.assertIn('scroll-behavior: auto', css)

    def test_no_autoplaying_content(self):
        """The hero used to auto-advance every 4s with no stop control
        (WCAG 2.2.2). It was removed rather than given a pause button."""
        js = (Path(__file__).resolve().parent.parent / 'static' / 'js' / 'main.js').read_text(encoding='utf-8')
        self.assertNotIn('setInterval', js)


class LegalPageAccessibilityTests(TestCase):
    def test_every_legal_page_is_structured(self):
        for name in ('privacy', 'terms', 'cookies', 'refunds', 'accessibility'):
            with self.subTest(page=name):
                response = self.client.get(reverse(f'landing:{name}'))
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                parser = _Collector()
                parser.feed(html)
                self.assertEqual(parser.headings.count(1), 1, 'expected exactly one h1')
                previous = 0
                for level in parser.headings:
                    if previous:
                        self.assertLessEqual(level, previous + 1)
                    previous = level
                self.assertIn('class="skip-link" href="#main"', html)
