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
    // SHOWCASE CAROUSEL
    // =========================================================================
    function initShowcase() {
        var panels = Array.prototype.slice.call(document.querySelectorAll('.showcase-panel'));
        var dots = Array.prototype.slice.call(document.querySelectorAll('.showcase-dot'));
        var prev = document.querySelector('[data-showcase="prev"]');
        var next = document.querySelector('[data-showcase="next"]');
        var stepNum = document.querySelector('.showcase-step-num');
        var title = document.querySelector('.showcase-title');
        var blurb = document.querySelector('.showcase-blurb');
        if (!panels.length) return;

        var active = 0;

        function render() {
            panels.forEach(function (panel, i) {
                panel.classList.toggle('is-active', i === active);
            });
            dots.forEach(function (dot, i) {
                if (i === active) dot.setAttribute('aria-current', 'true');
                else dot.removeAttribute('aria-current');
            });

            var panel = panels[active];
            // The caption sits in an aria-live region, so rewriting it is what
            // announces the change. Without this the arrows are silent.
            if (stepNum) stepNum.textContent = String(active + 1);
            if (title) title.textContent = panel.dataset.title || '';
            if (blurb) blurb.textContent = panel.dataset.blurb || '';
        }

        function goTo(i) {
            active = ((i % panels.length) + panels.length) % panels.length;
            render();
        }

        dots.forEach(function (dot, i) {
            dot.addEventListener('click', function () { goTo(i); });
        });
        if (prev) prev.addEventListener('click', function () { goTo(active - 1); });
        if (next) next.addEventListener('click', function () { goTo(active + 1); });

        // Arrow keys, so the 9 dots do not have to be tabbed through one by one.
        var dotGroup = document.querySelector('.showcase-dots');
        if (dotGroup) {
            dotGroup.addEventListener('keydown', function (e) {
                var delta = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
                if (!delta) return;
                e.preventDefault();
                goTo(active + delta);
                dots[active].focus();
            });
        }
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
        initShowcase();
        initPricing();
    });
})();
