/**
 * HubSign Landing Page JavaScript
 * Handles slider, modal, mobile menu, and API interactions
 */

// ============================================
// Slider Functionality
// ============================================
let currentSlide = 0;
const totalSlides = 3;
let autoSlideInterval;

function getSliderElements() {
    return {
        slides: document.getElementById('heroSlides'),
        dots: document.querySelectorAll('.slider-dot')
    };
}

function updateSlider() {
    const { slides, dots } = getSliderElements();
    if (!slides) return;
    
    slides.style.transform = `translateX(-${currentSlide * 100}%)`;
    dots.forEach((dot, i) => dot.classList.toggle('active', i === currentSlide));
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateSlider();
    resetAutoSlide();
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateSlider();
    resetAutoSlide();
}

function goToSlide(i) {
    currentSlide = i;
    updateSlider();
    resetAutoSlide();
}

function startAutoSlide() {
    autoSlideInterval = setInterval(nextSlide, 5000);
}

function resetAutoSlide() {
    clearInterval(autoSlideInterval);
    startAutoSlide();
}

// ============================================
// Mobile Menu
// ============================================
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('active');
    }
}

// ============================================
// Modal Functionality
// ============================================
const modalState = {
    currentStep: 0,
    subdomain: '',
    email: ''
};

function getModalElements() {
    return {
        overlay: document.getElementById('modalOverlay'),
        steps: [
            document.getElementById('modalStep0'),
            document.getElementById('modalStep1'),
            document.getElementById('modalStep2'),
            document.getElementById('modalStep3'),
            document.getElementById('modalStep4'),
            document.getElementById('modalStep5')
        ]
    };
}

function showModalStep(stepIndex) {
    const { steps } = getModalElements();
    steps.forEach((step, i) => {
        if (step) {
            step.classList.toggle('hidden', i !== stepIndex);
        }
    });
    modalState.currentStep = stepIndex;
}

function openModal() {
    const { overlay } = getModalElements();
    if (overlay) {
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        resetModal();
    }
}

function closeModal() {
    const { overlay } = getModalElements();
    if (overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(resetModal, 200);
    }
}

function closeModalOnOverlay(e) {
    const { overlay } = getModalElements();
    if (e.target === overlay) {
        closeModal();
    }
}

function resetModal() {
    showModalStep(0);
    modalState.subdomain = '';
    modalState.email = '';
    
    // Clear form inputs
    const inputs = ['subdomain', 'sharedEmail', 'signupEmail', 'signupName', 'signupCompany'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
}

// Step Navigation
function goToStep0() {
    showModalStep(0);
}

function goToSubdomainStep() {
    showModalStep(1);
    setTimeout(() => {
        const input = document.getElementById('subdomain');
        if (input) input.focus();
    }, 100);
}

function goToSharedStep() {
    showModalStep(2);
    setTimeout(() => {
        const input = document.getElementById('sharedEmail');
        if (input) input.focus();
    }, 100);
}

function goToSignupStep() {
    showModalStep(3);
    setTimeout(() => {
        const input = document.getElementById('signupEmail');
        if (input) input.focus();
    }, 100);
}

// ============================================
// Form Submissions with API Integration
// ============================================

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Subdomain validation and redirect
async function submitSubdomain(e) {
    e.preventDefault();
    
    const subdomainInput = document.getElementById('subdomain');
    const subdomain = subdomainInput.value.trim().toLowerCase();
    
    // Basic validation
    if (!subdomain || subdomain.length < 2) {
        subdomainInput.focus();
        return;
    }
    
    // Validate subdomain format
    const subdomainRegex = /^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$/;
    if (!subdomainRegex.test(subdomain)) {
        subdomainInput.setCustomValidity('Invalid subdomain format');
        subdomainInput.reportValidity();
        return;
    }
    
    modalState.subdomain = subdomain;
    
    // Show redirecting step
    const displaySubdomain = document.getElementById('displaySubdomain');
    if (displaySubdomain) {
        displaySubdomain.textContent = `${subdomain}.hubsign.io`;
    }
    showModalStep(5);
    
    try {
        // Validate subdomain exists via API
        const response = await fetch('/api/v1/tenant/validate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ subdomain: subdomain })
        });
        
        const data = await response.json();
        
        if (data.valid && data.redirect_url) {
            // Redirect to tenant subdomain
            window.location.href = data.redirect_url;
        } else {
            // Show error - subdomain not found
            alert(data.message || 'Organization not found. Please check your subdomain.');
            showModalStep(1);
        }
    } catch (error) {
        console.error('Error validating subdomain:', error);
        // Fallback: redirect anyway (for demo/development)
        window.location.href = `https://${subdomain}.hubsign.io`;
    }
}

// Shared instance login
async function submitSharedLogin(e) {
    e.preventDefault();
    
    const emailInput = document.getElementById('sharedEmail');
    const email = emailInput.value.trim();
    
    if (!email || !isValidEmail(email)) {
        emailInput.focus();
        return;
    }
    
    modalState.email = email;
    
    try {
        const response = await fetch('/api/v1/auth/magic-link/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show success
            const displayEmail = document.getElementById('displayEmail');
            if (displayEmail) {
                displayEmail.textContent = email;
            }
            showModalStep(4);
        } else {
            alert(data.message || 'Failed to send sign-in link. Please try again.');
        }
    } catch (error) {
        console.error('Error sending magic link:', error);
        // Show success anyway for demo
        const displayEmail = document.getElementById('displayEmail');
        if (displayEmail) {
            displayEmail.textContent = email;
        }
        showModalStep(4);
    }
}

// Signup form
async function submitSignup(e) {
    e.preventDefault();
    
    const email = document.getElementById('signupEmail').value.trim();
    const name = document.getElementById('signupName').value.trim();
    const company = document.getElementById('signupCompany').value.trim();
    
    if (!email || !isValidEmail(email)) {
        document.getElementById('signupEmail').focus();
        return;
    }
    
    if (!name) {
        document.getElementById('signupName').focus();
        return;
    }
    
    try {
        const response = await fetch('/api/v1/auth/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                email: email,
                name: name,
                company: company
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const displayEmail = document.getElementById('displayEmail');
            if (displayEmail) {
                displayEmail.textContent = email;
            }
            showModalStep(4);
        } else {
            alert(data.message || 'Signup failed. Please try again.');
        }
    } catch (error) {
        console.error('Error during signup:', error);
        // Show success anyway for demo
        const displayEmail = document.getElementById('displayEmail');
        if (displayEmail) {
            displayEmail.textContent = email;
        }
        showModalStep(4);
    }
}

// Email validation helper
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ============================================
// Pricing Toggle
// ============================================
function initPricingToggle() {
    const toggle = document.querySelector('.toggle-switch');
    if (toggle) {
        toggle.addEventListener('click', function() {
            this.classList.toggle('annual');
            updatePricing(this.classList.contains('annual'));
        });
    }
}

function updatePricing(isAnnual) {
    const prices = {
        individual: { monthly: 15, annual: 12 },
        business: { monthly: 60, annual: 48 },
        enterprise: { monthly: 200, annual: 160 }
    };
    
    // Update displayed prices (if dynamic pricing elements exist)
    document.querySelectorAll('[data-plan]').forEach(el => {
        const plan = el.dataset.plan;
        if (prices[plan]) {
            const price = isAnnual ? prices[plan].annual : prices[plan].monthly;
            el.textContent = `$${price}`;
        }
    });
    
    // Update toggle labels
    document.querySelectorAll('.pricing-toggle span').forEach((span, i) => {
        span.classList.toggle('active', (i === 0 && !isAnnual) || (i === 1 && isAnnual));
    });
}

// ============================================
// Smooth Scroll
// ============================================
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
                if (mobileMenu && mobileMenu.classList.contains('active')) {
                    mobileMenu.classList.remove('active');
                }
            }
        });
    });
}

// ============================================
// Header Shadow on Scroll
// ============================================
function initHeaderScroll() {
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            header.style.boxShadow = window.pageYOffset > 50 
                ? '0 1px 3px rgba(0,0,0,0.1)' 
                : 'none';
        });
    }
}

// ============================================
// Event Listeners
// ============================================
function initEventListeners() {
    // Escape key closes modal
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            const { overlay } = getModalElements();
            if (overlay && overlay.classList.contains('active')) {
                closeModal();
            }
        }
    });
    
    // Click outside mobile menu closes it
    document.addEventListener('click', e => {
        const mobileMenu = document.getElementById('mobileMenu');
        if (mobileMenu && mobileMenu.classList.contains('active')) {
            if (!mobileMenu.contains(e.target) && !e.target.closest('.mobile-menu-btn')) {
                mobileMenu.classList.remove('active');
            }
        }
    });
}

// ============================================
// Initialize on DOM Ready
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    startAutoSlide();
    initPricingToggle();
    initSmoothScroll();
    initHeaderScroll();
    initEventListeners();
});

// Export functions for global access (used by onclick handlers)
window.nextSlide = nextSlide;
window.prevSlide = prevSlide;
window.goToSlide = goToSlide;
window.toggleMobileMenu = toggleMobileMenu;
window.openModal = openModal;
window.closeModal = closeModal;
window.closeModalOnOverlay = closeModalOnOverlay;
window.goToStep0 = goToStep0;
window.goToSubdomainStep = goToSubdomainStep;
window.goToSharedStep = goToSharedStep;
window.goToSignupStep = goToSignupStep;
window.submitSubdomain = submitSubdomain;
window.submitSharedLogin = submitSharedLogin;
window.submitSignup = submitSignup;
