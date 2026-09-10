#!/usr/bin/env python
"""Browser-based accessibility audit.

Complements `manage.py test`, which covers markup, contrast tokens and cookie
posture but cannot exercise a real browser. This adds:

  * axe-core against every public page, at desktop and mobile widths
  * keyboard operation of each interactive widget
  * horizontal-overflow / reflow checks (WCAG 1.4.10)
  * confirmation that the billing toggle works with the API blocked

Not part of the default test run: it needs a browser and a running server.

    pip install playwright && playwright install chromium
    python manage.py runserver 127.0.0.1:8399
    python tools/browser_audit.py [base-url]

Exits non-zero if anything fails, so it can gate a release.
"""
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8399'
AXE_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js'
PAGES = ['/', '/legal/privacy/', '/legal/terms/', '/legal/cookies/',
         '/legal/refunds/', '/legal/accessibility/']

AXE_RUN = r"""async () => {
    const r = await axe.run(document, {runOnly: {type: 'tag', values: [
        'wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
    return r.violations.map(v => ({
        id: v.id, impact: v.impact, help: v.help,
        nodes: v.nodes.slice(0, 3).map(n => n.target.join(' ') + ' :: ' + (n.failureSummary || '').slice(0, 160))
    }));
}"""

OVERFLOW = r"""() => {
    const de = document.documentElement;
    return [de.scrollWidth, de.clientWidth];
}"""

passed = failed = 0


def check(label, ok, detail=''):
    global passed, failed
    if ok:
        passed += 1
        print(f'  PASS  {label}')
    else:
        failed += 1
        print(f'  FAIL  {label} {detail}')


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('playwright is not installed: pip install playwright && playwright install chromium')

    axe_src = urllib.request.urlopen(AXE_CDN, timeout=60).read().decode('utf-8')

    with sync_playwright() as p:
        browser = p.chromium.launch()

        print('== axe-core ==')
        for path in PAGES:
            for width in (1280, 390):
                # bypass_csp is only so axe can be injected. The real policy is
                # asserted in landing/tests_legal.py::SecurityHeaderTests.
                ctx = browser.new_context(viewport={'width': width, 'height': 900}, bypass_csp=True)
                page = ctx.new_page()
                page.goto(BASE + path, wait_until='load')
                page.add_script_tag(content=axe_src)
                violations = page.evaluate(AXE_RUN)
                check(f'{path} @ {width}px', not violations)
                for v in violations:
                    print(f"        [{v['impact']}] {v['id']}: {v['help']}")
                    for node in v['nodes']:
                        print(f'          {node}')
                page.close()
                ctx.close()

        print('== reflow ==')
        for width, label in ((320, '320px (WCAG 1.4.10)'), (390, '390px'), (640, '1280px at 200% zoom')):
            page = browser.new_page(viewport={'width': width, 'height': 900})
            page.goto(BASE + '/', wait_until='load')
            scroll_w, client_w = page.evaluate(OVERFLOW)
            check(f'no horizontal overflow at {label}', scroll_w <= client_w + 1,
                  f'scrollWidth={scroll_w} clientWidth={client_w}')
            page.close()

        print('== keyboard ==')
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        # The billing toggle must not depend on the pricing API resolving.
        page.route('**/api/**', lambda route: route.abort())
        page.goto(BASE + '/', wait_until='load')

        page.keyboard.press('Tab')
        check('skip link is first in the tab order',
              'skip-link' in page.evaluate('() => document.activeElement.className'))
        page.keyboard.press('Enter')
        check('skip link moves focus to <main>',
              page.evaluate('() => document.activeElement.id') == 'main')

        question = page.locator('.faq-question').first
        answer = page.locator('#' + question.get_attribute('aria-controls'))
        check('FAQ answer starts hidden', answer.is_hidden())
        question.click()
        check('FAQ reports expanded state', question.get_attribute('aria-expanded') == 'true')
        check('FAQ answer becomes visible', answer.is_visible())

        title = page.locator('.showcase-title')
        page.locator('[data-showcase="next"]').click()
        check('carousel updates its live caption', title.inner_text() == 'Document Review',
              repr(title.inner_text()))
        check('carousel marks the current dot',
              page.locator('.showcase-dot[aria-current="true"]').get_attribute('data-step') == '1')
        page.locator('.showcase-dot').nth(1).focus()
        page.keyboard.press('ArrowRight')
        check('carousel responds to arrow keys', title.inner_text() == 'E-Sign', repr(title.inner_text()))

        amount = page.locator('.pricing-amount').first
        check('monthly price is server-rendered', amount.inner_text() == '$15', repr(amount.inner_text()))
        page.locator('#billingToggle [data-billing="annual"]').click()
        check('annual price switches with the API blocked', amount.inner_text() == '$12',
              repr(amount.inner_text()))
        page.locator('#planFamilyToggle [data-family="individual"]').focus()
        page.keyboard.press('ArrowRight')
        check('plan family switches by arrow key', page.locator('#plans-organization').is_visible())
        page.close()

        print('== mobile menu ==')
        page = browser.new_page(viewport={'width': 390, 'height': 800})
        page.goto(BASE + '/', wait_until='load')
        btn = page.locator('#mobileMenuBtn')
        btn.click()
        check('menu opens and reports it', btn.get_attribute('aria-expanded') == 'true')
        check('menu label becomes Close menu', btn.get_attribute('aria-label') == 'Close menu')
        page.keyboard.press('Escape')
        check('Escape closes the menu', btn.get_attribute('aria-expanded') == 'false')
        check('focus returns to the trigger',
              page.evaluate('() => document.activeElement.id') == 'mobileMenuBtn')
        page.close()

        print('== reduced motion ==')
        page = browser.new_page(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
        page.goto(BASE + '/', wait_until='load')
        check('smooth scrolling is disabled',
              page.evaluate('() => getComputedStyle(document.documentElement).scrollBehavior') == 'auto')
        page.close()

        browser.close()

    print(f'\n{passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
