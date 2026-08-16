/**
 * HubSign Landing - Main JavaScript
 * Enterprise E-Signatures Made Simple
 */

// =============================================================================
// SLIDER
// =============================================================================

let currentSlide = 0;
const totalSlides = 3;
let autoSlideInterval;

function initSlider() {
    const heroSlides = document.getElementById('heroSlides');
    const dots = document.querySelectorAll('.slider-dot');
    
    if (!heroSlides) return;
    
    function updateSlider() {
        heroSlides.style.transform = `translateX(-${currentSlide * 100}%)`;
        dots.forEach((dot, i) => dot.classList.toggle('active', i === currentSlide));
    }
    
    window.nextSlide = function() {
        currentSlide = (currentSlide + 1) % totalSlides;
        updateSlider();
        resetAutoSlide();
    };
    
    window.prevSlide = function() {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        updateSlider();
        resetAutoSlide();
    };
    
    window.goToSlide = function(i) {
        currentSlide = i;
        updateSlider();
        resetAutoSlide();
    };
    
    function startAutoSlide() {
        autoSlideInterval = setInterval(window.nextSlide, 5000);
    }
    
    function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        startAutoSlide();
    }
    
    startAutoSlide();
}

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
// PRICING TOGGLE
// =============================================================================

function applyPricingTiers(tiers, isAnnual) {
    tiers.forEach(tier => {
        const card = document.querySelector('[data-tier="' + tier.id + '"]');
        if (!card) return;
        const amountEl = card.querySelector('.pricing-amount');
        const periodEl = card.querySelector('.pricing-period');
        const billingEl = card.querySelector('.pricing-billing-amount');
        const saveEl = card.querySelector('.pricing-save');
        const addonEls = card.querySelectorAll('.pricing-addon-amount');
        if (!amountEl) return;
        const price = isAnnual ? tier.price_annually : tier.price_monthly;
        if (price === 0) {
            amountEl.textContent = '$0';
            if (periodEl) periodEl.textContent = '';
            if (billingEl) billingEl.textContent = '';
            if (saveEl) saveEl.textContent = '';
        } else {
            amountEl.textContent = '$' + price;
            if (periodEl) periodEl.textContent = '/mo';
            if (isAnnual) {
                if (billingEl) billingEl.textContent = 'Billed $' + (price * 12) + '/yr';
                const savings = tier.price_monthly > 0
                    ? Math.round((1 - tier.price_annually / tier.price_monthly) * 100)
                    : 0;
                if (saveEl) saveEl.textContent = savings > 0 ? 'Save ' + savings + '%' : '';
            } else {
                if (billingEl) billingEl.textContent = '';
                if (saveEl) saveEl.textContent = '';
            }
        }
        addonEls.forEach((el, i) => {
            const addon = tier.addons && tier.addons[i];
            if (!addon) return;
            const addonPrice = isAnnual ? addon.price_annually : addon.price_monthly;
            el.textContent = '$' + addonPrice + addon.unit_suffix;
        });
    });
}

function initPricingToggle() {
    const toggle = document.querySelector('.toggle-switch');
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

    toggle.addEventListener('click', function() {
        this.classList.toggle('annual');
        const isAnnual = this.classList.contains('annual');

        const labels = document.querySelectorAll('.pricing-toggle span');
        labels.forEach((label, index) => {
            label.classList.toggle('active', (index === 0 && !isAnnual) || (index === 1 && isAnnual));
        });

        if (!pricingTiers) return;
        applyPricingTiers(pricingTiers, isAnnual);
    });
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initSlider();
    initSmoothScroll();
    initHeaderScroll();
    initPricingToggle();
});
