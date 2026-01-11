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
// MODAL - SIGN IN FLOW
// =============================================================================

const SignInModal = {
    overlay: null,
    steps: {},
    inputs: {},
    currentDomain: '',
    selectedSignInType: 'subdomain', // 'subdomain' or 'shared'
    
    init() {
        this.overlay = document.getElementById('modalOverlay');
        this.steps = {
            select: document.getElementById('modalStepSelect'),
            domain: document.getElementById('modalStep1'),
            email: document.getElementById('modalStep2'),
            success: document.getElementById('modalStep3'),
        };
        this.inputs = {
            domain: document.getElementById('domain'),
            email: document.getElementById('email'),
        };
        
        // Set up event listeners
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.overlay?.classList.contains('active')) {
                this.close();
            }
        });
        
        // Close on overlay click
        this.overlay?.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });
    },
    
    open() {
        if (!this.overlay) return;
        
        // Check cache for returning users
        const cached = this.loadSubdomainFromCache();
        if (cached && cached.subdomain) {
            // Auto-redirect to their subdomain
            window.location.href = `https://${cached.subdomain}.hubsign.io`;
            return;
        }
        
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        this.reset();
        
        // Focus first interactive element after animation
        setTimeout(() => {
            const firstOption = document.querySelector('.signin-option');
            if (firstOption) firstOption.focus();
        }, 200);
    },
    
    close() {
        if (!this.overlay) return;
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(() => this.reset(), 200);
    },
    
    reset() {
        // Hide all steps
        Object.values(this.steps).forEach(step => {
            if (step) step.classList.add('hidden');
        });
        
        // Show selection step
        if (this.steps.select) {
            this.steps.select.classList.remove('hidden');
        }
        
        // Clear inputs
        if (this.inputs.domain) this.inputs.domain.value = '';
        if (this.inputs.email) this.inputs.email.value = '';
        
        this.currentDomain = '';
        this.selectedSignInType = 'subdomain';
        
        // Reset option selection UI
        document.querySelectorAll('.signin-option').forEach(opt => {
            opt.classList.remove('selected');
        });
    },
    
    selectSignInType(type) {
        this.selectedSignInType = type;
        
        // Update UI
        document.querySelectorAll('.signin-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        const selectedOption = document.querySelector(`[data-signin-type="${type}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
        
        // Proceed based on type
        if (type === 'subdomain') {
            this.showStep('domain');
            setTimeout(() => this.inputs.domain?.focus(), 100);
        } else {
            // Shared instance - go directly to email
            this.currentDomain = 'app.hubsign.io';
            this.showStep('email');
            setTimeout(() => this.inputs.email?.focus(), 100);
        }
    },
    
    showStep(stepName) {
        Object.entries(this.steps).forEach(([name, step]) => {
            if (step) {
                step.classList.toggle('hidden', name !== stepName);
            }
        });
    },
    
    goToSelect() {
        this.showStep('select');
    },
    
    goToDomain() {
        this.showStep('domain');
        if (this.inputs.domain) {
            this.inputs.domain.value = this.currentDomain;
            setTimeout(() => this.inputs.domain.focus(), 100);
        }
    },
    
    async submitDomain(event) {
        event.preventDefault();
        
        const input = this.inputs.domain?.value.trim().toLowerCase();
        if (!input) {
            this.inputs.domain?.focus();
            return;
        }
        
        // Extract subdomain from input
        let subdomain = input;
        
        // Handle different input formats:
        // 1. "example.hubsign.io" -> extract "example"
        // 2. "example" -> use as-is
        if (input.includes('.')) {
            // Has dots - extract the first part
            subdomain = input.split('.')[0];
        }
        
        // Validate subdomain format (alphanumeric and hyphens only)
        const subdomainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?$/;
        if (!subdomainRegex.test(subdomain)) {
            this.showError('domain', 'Please enter a valid subdomain (e.g., example.hubsign.io)');
            return;
        }
        
        // Show loading state
        const continueBtn = event.target.querySelector('button[type="submit"]');
        const originalText = continueBtn?.innerHTML;
        if (continueBtn) {
            continueBtn.disabled = true;
            continueBtn.innerHTML = '<span>Validating...</span>';
        }
        
        // Validate subdomain via API
        try {
            const response = await this.validateSubdomain(subdomain);
            
            if (response.exists && response.subdomain) {
                // Valid subdomain - save to cache and redirect
                this.saveSubdomainToCache(response.subdomain, `${subdomain}.hubsign.io`);
                this.currentDomain = `${subdomain}.hubsign.io`;
                
                // Show success message briefly then redirect
                this.showSuccessMessage(`Redirecting to ${response.subdomain}.hubsign.io...`);
                
                setTimeout(() => {
                    window.location.href = `https://${response.subdomain}.hubsign.io`;
                }, 1500);
                
            } else if (response.exists === false) {
                // Subdomain doesn't exist - show error
                if (continueBtn) {
                    continueBtn.disabled = false;
                    continueBtn.innerHTML = originalText;
                }
                this.showError('domain', `Subdomain "${subdomain}" is not registered. Please check your company subdomain or contact support.`);
                
            } else {
                // Unknown response - continue to email step
                this.currentDomain = `${subdomain}.hubsign.io`;
                const displayDomain = document.getElementById('displayDomain');
                if (displayDomain) {
                    displayDomain.textContent = this.currentDomain;
                }
                
                if (continueBtn) {
                    continueBtn.disabled = false;
                    continueBtn.innerHTML = originalText;
                }
                
                this.showStep('email');
                setTimeout(() => this.inputs.email?.focus(), 100);
            }
            
        } catch (error) {
            console.error('Subdomain validation failed:', error);
            
            // Reset button state
            if (continueBtn) {
                continueBtn.disabled = false;
                continueBtn.innerHTML = originalText;
            }
            
            // Show error or continue based on error type
            this.showError('domain', 'Unable to validate domain. Please try again or use "Sign in to shared instance".');
        }
    },
    
    async validateSubdomain(domain) {
        const response = await fetch('/api/v1/tenant/validate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({ domain }),
        });
        
        if (!response.ok) {
            throw new Error(`Validation failed: ${response.status}`);
        }
        
        return response.json();
    },
    
    saveSubdomainToCache(subdomain, domain) {
        try {
            const cacheData = {
                subdomain: subdomain,
                domain: domain,
                timestamp: Date.now(),
            };
            localStorage.setItem('hubsign_subdomain', JSON.stringify(cacheData));
        } catch (error) {
            console.error('Failed to save subdomain to cache:', error);
        }
    },
    
    loadSubdomainFromCache() {
        try {
            const cached = localStorage.getItem('hubsign_subdomain');
            if (cached) {
                const data = JSON.parse(cached);
                // Cache valid for 30 days
                const cacheAge = Date.now() - data.timestamp;
                const thirtyDays = 30 * 24 * 60 * 60 * 1000;
                
                if (cacheAge < thirtyDays) {
                    return data;
                } else {
                    // Clear old cache
                    localStorage.removeItem('hubsign_subdomain');
                }
            }
        } catch (error) {
            console.error('Failed to load subdomain from cache:', error);
        }
        return null;
    },
    
    showSuccessMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'success-message';
        messageEl.textContent = message;
        messageEl.style.cssText = 'padding: 12px; background: #d1fae5; color: #065f46; border-radius: 8px; margin: 16px 0; text-align: center; font-size: 0.875rem;';
        
        const form = this.steps.domain?.querySelector('.modal-form');
        if (form) {
            form.insertBefore(messageEl, form.firstChild);
        }
    },
    
    showError(inputName, message) {
        const input = this.inputs[inputName];
        if (!input) return;
        
        // Remove existing error
        const existingError = input.parentElement?.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Add error message
        const errorEl = document.createElement('div');
        errorEl.className = 'error-message';
        errorEl.textContent = message;
        errorEl.style.cssText = 'color: #dc2626; font-size: 0.75rem; margin-top: 4px;';
        
        input.parentElement?.appendChild(errorEl);
        input.focus();
        
        // Add error styling to input
        input.style.borderColor = '#dc2626';
        
        // Remove error on input
        input.addEventListener('input', function removeError() {
            errorEl.remove();
            input.style.borderColor = '';
            input.removeEventListener('input', removeError);
        }, { once: true });
    },

    
    async submitEmail(event) {
        event.preventDefault();
        
        const email = this.inputs.email?.value.trim();
        if (!email) {
            this.inputs.email?.focus();
            return;
        }
        
        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.showError('email', 'Please enter a valid email address');
            return;
        }
        
        // Submit sign-in request
        try {
            const response = await fetch('/api/v1/auth/magic-link/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    email,
                    domain: this.currentDomain,
                    use_shared_instance: this.selectedSignInType === 'shared',
                }),
            });
            
            const result = await response.json();
            
            if (result.success || response.ok) {
                // Show success
                const displayEmail = document.getElementById('displayEmail');
                if (displayEmail) {
                    displayEmail.textContent = email;
                }
                this.showStep('success');
            } else {
                this.showError('email', result.message || 'Unable to send sign-in link');
            }
        } catch (error) {
            console.error('Sign-in request failed:', error);
            // Show success anyway for demo purposes
            const displayEmail = document.getElementById('displayEmail');
            if (displayEmail) {
                displayEmail.textContent = email;
            }
            this.showStep('success');
        }
    },
    
    getCSRFToken() {
        // Get CSRF token from cookie
        const name = 'csrftoken';
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
};

// Global functions for onclick handlers
function openModal() {
    SignInModal.open();
}

function closeModal() {
    SignInModal.close();
}

function selectSignInType(type) {
    SignInModal.selectSignInType(type);
}

function goToSelect() {
    SignInModal.goToSelect();
}

function goToStep1() {
    SignInModal.goToDomain();
}

function goToStep2(event) {
    SignInModal.submitDomain(event);
}

function submitLogin(event) {
    SignInModal.submitEmail(event);
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

function initPricingToggle() {
    const toggle = document.querySelector('.toggle-switch');
    if (!toggle) return;
    
    toggle.addEventListener('click', function() {
        this.classList.toggle('annual');
        
        // Update pricing display
        const isAnnual = this.classList.contains('annual');
        
        // Update toggle labels
        const labels = document.querySelectorAll('.pricing-toggle span');
        labels.forEach((label, index) => {
            label.classList.toggle('active', (index === 0 && !isAnnual) || (index === 1 && isAnnual));
        });
        
        // TODO: Update pricing amounts based on annual/monthly
    });
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initSlider();
    SignInModal.init();
    initSmoothScroll();
    initHeaderScroll();
    initPricingToggle();
});
