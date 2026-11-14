/**
 * HubSign Landing - Main JavaScript
 *
 * Notes for anyone editing this file:
 *
 * - No inline onclick attributes anywhere. Every handler is bound here, which
 *   is what lets the Content-Security-Policy in hubsign/settings.py drop
 *   'unsafe-inline' from script-src.
 *
 * - Anything that changes visible state must also change the matching ARIA
 *   attribute (aria-expanded, aria-selected, aria-current). State that lives
 *   only in a CSS class is invisible to assistive technology.
 *
 * - There is no auto-advancing content on this page. The hero carousel that
 *   used to rotate every 4s with no stop control has been removed rather than
 *   given a pause button (WCAG 2.2.2).
 */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    // =========================================================================
    // MOBILE MENU
    // =========================================================================
    function initMobileMenu() {
        var btn = document.getElementById('mobileMenuBtn');
        var menu = document.getElementById('mobileMenu');
        if (!btn || !menu) return;

        function setOpen(open) {
            btn.setAttribute('aria-expanded', String(open));
            btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
            menu.classList.toggle('is-open', open);
        }

        function close(returnFocus) {
            if (btn.getAttribute('aria-expanded') !== 'true') return;
            setOpen(false);
            if (returnFocus) btn.focus();
        }

        btn.addEventListener('click', function () {
            setOpen(btn.getAttribute('aria-expanded') !== 'true');
        });

        // Escape closes and returns focus to the trigger, so a keyboard user is
        // never stranded inside the menu.
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') close(true);
        });

        menu.addEventListener('click', function (e) {
            if (e.target.closest('a')) close(false);
        });

        document.addEventListener('click', function (e) {
            if (!menu.contains(e.target) && !btn.contains(e.target)) close(false);
        });
    }

    // =========================================================================
    // IN-PAGE LINKS
    // Moves focus as well as the viewport: scrolling alone leaves keyboard and
    // screen-reader users where they started.
    // =========================================================================
    function initInPageLinks() {
        document.addEventListener('click', function (e) {
            var link = e.target.closest('a[href^="#"], a[href^="/#"]');
            if (!link) return;

            var hash = link.getAttribute('href').replace(/^\//, '');
            if (hash === '#') return;

            var target = document.querySelector(hash);
            if (!target) return;   // let the browser navigate normally

            e.preventDefault();
            target.scrollIntoView({
                behavior: reduceMotion.matches ? 'auto' : 'smooth',
                block: 'start'
            });

            // Sections are not focusable by default; tabindex="-1" makes them
            // programmatically focusable without adding them to the tab order.
            if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
            target.focus({ preventScroll: true });

            if (history.replaceState) history.replaceState(null, '', hash);
        });
    }

    // =========================================================================
    // FAQ ACCORDION
    // The answer is genuinely hidden (the `hidden` attribute), not clipped with
    // max-height. The previous version left all seven answers in the
    // accessibility tree at all times, which made the accordion meaningless to
    // screen-reader users -- and truncated any answer over 400px when open.
    // =========================================================================
    function initFaq() {
        document.querySelectorAll('.faq-question').forEach(function (btn) {
            var answer = document.getElementById(btn.getAttribute('aria-controls'));
            if (!answer) return;

            btn.addEventListener('click', function () {
                var open = btn.getAttribute('aria-expanded') === 'true';
                btn.setAttribute('aria-expanded', String(!open));
                answer.hidden = open;
            });
        });
    }

    // =========================================================================
    // SPINE DRAW-ON
    // The hero pipeline inks in once, when it first scrolls into view (~2.7s,
    // well under the 5s WCAG 2.2.2 threshold, and it stops: it is not a loop).
    // Skipped entirely under prefers-reduced-motion, and without JS the spine
    // is simply fully drawn -- .js-draw is only ever added here.
    // =========================================================================
    function initSpineDraw() {
        var spine = document.querySelector('.spine');
        if (!spine || reduceMotion.matches || !('IntersectionObserver' in window)) return;

        spine.classList.add('js-draw');
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                // Two frames, so the hidden starting state is painted before the
                // class change gives the transitions something to run from.
                requestAnimationFrame(function () {
                    requestAnimationFrame(function () { spine.classList.add('is-drawn'); });
                });
                io.disconnect();
            });
        }, { threshold: 0.1 });
        io.observe(spine);
    }

    // =========================================================================
    // SHOWCASE WALKTHROUGH
    // Tabs pattern: aria-selected on the tab, `hidden` on the inactive panels,
    // a roving tabindex, and arrow keys / Home / End. It opens on the second
    // screen (set in the template) because the hero already shows the first.
    // =========================================================================
    function initWalkthrough() {
        var list = document.querySelector('.walk-tabs');
        if (!list) return;
        var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
        if (!tabs.length) return;

        function select(tab, focus) {
            tabs.forEach(function (t) {
                var on = t === tab;
                t.setAttribute('aria-selected', String(on));
                t.tabIndex = on ? 0 : -1;
                var panel = document.getElementById(t.getAttribute('aria-controls'));
                if (panel) panel.hidden = !on;
            });
            if (focus) tab.focus();
        }

        tabs.forEach(function (tab) {
            tab.tabIndex = tab.getAttribute('aria-selected') === 'true' ? 0 : -1;
            tab.addEventListener('click', function () { select(tab, false); });
        });

        // "Next: ..." under each screen. The clicked button's panel is about to
        // be hidden, so focus moves to the new panel's own Next button -- a
        // keyboard user can keep stepping through without hunting for the tabs.
        document.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-walk-next]');
            if (!btn) return;
            var to = Number(btn.getAttribute('data-walk-next')) % tabs.length;
            select(tabs[to], false);
            var panel = document.getElementById(tabs[to].getAttribute('aria-controls'));
            var nextBtn = panel && panel.querySelector('[data-walk-next]');
            if (nextBtn) nextBtn.focus({ preventScroll: true });
        });

        list.addEventListener('keydown', function (e) {
            var i = tabs.indexOf(document.activeElement);
            if (i < 0) return;
            var n = tabs.length, to = -1;
            if (e.key === 'ArrowDown' || e.key === 'ArrowRight') to = (i + 1) % n;
            else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') to = (i - 1 + n) % n;
            else if (e.key === 'Home') to = 0;
            else if (e.key === 'End') to = n - 1;
            if (to < 0) return;
            e.preventDefault();
            select(tabs[to], true);
        });
    }

    // =========================================================================
    // PRICING TABS
    // Both toggles use the tabs pattern: roving selection via aria-selected,
    // arrow-key navigation, and panels switched with the `hidden` attribute so
    // the inactive grid leaves the accessibility tree.
    // =========================================================================
    function initTabs(container, onSelect) {
        if (!container) return;
        var tabs = Array.prototype.slice.call(container.querySelectorAll('[role="tab"]'));
        if (!tabs.length) return;

        function select(tab) {
            tabs.forEach(function (t) {
                var on = t === tab;
                t.setAttribute('aria-selected', String(on));
                t.tabIndex = on ? 0 : -1;
            });
            onSelect(tab);
        }

        tabs.forEach(function (tab) {
            tab.tabIndex = tab.getAttribute('aria-selected') === 'true' ? 0 : -1;
            tab.addEventListener('click', function () { select(tab); });
        });

        container.addEventListener('keydown', function (e) {
            var delta = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
            if (!delta) return;
            e.preventDefault();
            var i = tabs.indexOf(document.activeElement);
            if (i < 0) return;
            var nextTab = tabs[(i + delta + tabs.length) % tabs.length];
            select(nextTab);
            nextTab.focus();
        });
    }

    function initPricing() {
        initTabs(document.getElementById('planFamilyToggle'), function (tab) {
            var family = tab.dataset.family;
            document.querySelectorAll('[data-family-group]').forEach(function (group) {
                group.hidden = group.dataset.familyGroup !== family;
            });
        });

        // Both figures are server-rendered into data- attributes, so switching
        // billing period needs no network call. This previously depended on
        // fetch('/api/pricing/') and could leave monthly prices on screen under
        // an "Annual" label whenever that request was slow or failed.
        initTabs(document.getElementById('billingToggle'), function (tab) {
            var annual = tab.dataset.billing === 'annual';
            document.querySelectorAll('.pricing-amount').forEach(function (el) {
                var value = annual ? el.dataset.annual : el.dataset.monthly;
                if (value !== undefined) el.textContent = '$' + value;
            });
            // The period label must say "billed annually" under Annual -- it used to
            // stay "/ month" next to the annual figure, so a visitor saw e.g. $47 and
            // was actually charged twelve times that up front.
            document.querySelectorAll('.pricing-period').forEach(function (el) {
                var value = annual ? el.dataset.annual : el.dataset.monthly;
                if (value !== undefined) el.textContent = value;
            });
            // The once-a-year total is server-rendered already (no text swap needed,
            // see the template) -- just reveal it under Annual.
            document.querySelectorAll('.pricing-annual-total').forEach(function (el) {
                el.hidden = !annual;
            });
            // Add-on rates switch with the period too; they used to stay at the
            // monthly figure while the headline price showed the annual one.
            document.querySelectorAll('.pricing-addon-amount').forEach(function (el) {
                var value = annual ? el.dataset.annual : el.dataset.monthly;
                if (value !== undefined) el.textContent = '+$' + value + (el.dataset.suffix || '');
            });
        });
    }

    // =========================================================================
    document.addEventListener('DOMContentLoaded', function () {
        initMobileMenu();
        initInPageLinks();
        initFaq();
        initSpineDraw();
        initWalkthrough();
        initPricing();
    });
})();
