/**
 * HubSign Landing - Main JavaScript
 * Everything that happens around the signature.
 */

// =============================================================================
// MOBILE MENU
// =============================================================================

function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('active');
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu?.classList.contains('active') &&
        !mobileMenu.contains(e.target) &&
        !e.target.closest('.mobile-menu-btn')) {
        mobileMenu.classList.remove('active');
    }
});

// =============================================================================
// SMOOTH SCROLL
// =============================================================================

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Close mobile menu if open
                const mobileMenu = document.getElementById('mobileMenu');
                if (mobileMenu?.classList.contains('active')) {
                    mobileMenu.classList.remove('active');
                }
            }
        });
    });
}

// =============================================================================
// HEADER SCROLL EFFECT
// =============================================================================

function initHeaderScroll() {
    const header = document.querySelector('.header');
    if (!header) return;

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 50) {
            header.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        } else {
            header.style.boxShadow = 'none';
        }
    });
}

// =============================================================================
// SHOWCASE CAROUSEL
// =============================================================================

function initShowcase() {
    const panels = Array.from(document.querySelectorAll('.showcase-panel'));
    const dots = Array.from(document.querySelectorAll('.showcase-dot'));
    const prevBtn = document.querySelector('.showcase-nav--prev');
    const nextBtn = document.querySelector('.showcase-nav--next');
    const stepNumEl = document.querySelector('.showcase-step-num');
    const titleEl = document.querySelector('.showcase-title');
    const blurbEl = document.querySelector('.showcase-blurb');
    if (!panels.length) return;

    let active = 0;

    function render() {
        panels.forEach((panel, i) => panel.classList.toggle('active', i === active));
        dots.forEach((dot, i) => dot.classList.toggle('active', i === active));
        const panel = panels[active];
        if (stepNumEl) stepNumEl.textContent = String(active + 1);
        if (titleEl) titleEl.textContent = panel.dataset.title || '';
        if (blurbEl) blurbEl.textContent = panel.dataset.blurb || '';
    }

    function goTo(i) {
        active = ((i % panels.length) + panels.length) % panels.length;
        render();
    }

    dots.forEach((dot, i) => dot.addEventListener('click', () => goTo(i)));
    if (prevBtn) prevBtn.addEventListener('click', () => goTo(active - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goTo(active + 1));
}

// =============================================================================
// FAQ ACCORDION
// =============================================================================

function initFaqAccordion() {
    document.querySelectorAll('.faq-item').forEach(item => {
        const question = item.querySelector('.faq-question');
        if (!question) return;
        question.addEventListener('click', () => {
            item.classList.toggle('open');
        });
    });
}

// =============================================================================
// PRICING: plan-family tab + monthly/annual toggle
// =============================================================================

function applyPricingTiers(tiers, isAnnual) {
    tiers.forEach(tier => {
        const card = document.querySelector('[data-tier="' + tier.id + '"]');
        if (!card) return;
        const amountEl = card.querySelector('.pricing-amount');
        if (!amountEl) return;
        const price = isAnnual ? tier.price_annually : tier.price_monthly;
        amountEl.textContent = '$' + price;
    });
}

function initPricingFamilyToggle() {
    const toggle = document.getElementById('planFamilyToggle');
    if (!toggle) return;

    const groups = document.querySelectorAll('[data-family-group]');

    toggle.addEventListener('click', (e) => {
        const btn = e.target.closest('.pill-toggle-btn');
        if (!btn) return;
        const family = btn.dataset.family;

        toggle.querySelectorAll('.pill-toggle-btn').forEach(b => {
            b.classList.toggle('active', b === btn);
        });
        groups.forEach(group => {
            group.hidden = group.dataset.familyGroup !== family;
        });
    });
}

function initBillingToggle() {
    const toggle = document.getElementById('billingToggle');
    if (!toggle) return;

    let pricingTiers = null;

    fetch('/api/pricing/')
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (!data) return;
            pricingTiers = data.tiers;
            // Apply Stripe prices immediately on load (monthly view is default)
            applyPricingTiers(pricingTiers, false);
        })
        .catch(() => {});

    toggle.addEventListener('click', (e) => {
        const btn = e.target.closest('.pill-toggle-btn');
        if (!btn) return;
        const isAnnual = btn.dataset.billing === 'annual';

        toggle.querySelectorAll('.pill-toggle-btn').forEach(b => {
            b.classList.toggle('active', b === btn);
        });

        if (!pricingTiers) return;
        applyPricingTiers(pricingTiers, isAnnual);
    });
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initSmoothScroll();
    initHeaderScroll();
    initShowcase();
    initFaqAccordion();
    initPricingFamilyToggle();
    initBillingToggle();
});
