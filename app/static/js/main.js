/**
 * Patient Tracker - Modern Frontend Enhancements
 * Enhances UI with animations, live previews, password toggles, and toast alerts
 * without interfering with existing backend forms or inline scripts.
 */

document.addEventListener('DOMContentLoaded', () => {
    initFlashAutoDismiss();
    initAnimatedCounters();
    initPasswordVisibilityToggles();
    initPaymentCardMirror();
    initSymptomChipsHelper();
    initDropzoneDragEffects();
});

/**
 * 1. Auto-dismiss flash alerts smoothly after 6 seconds
 */
function initFlashAutoDismiss() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach((alertEl) => {
        setTimeout(() => {
            if (alertEl && typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                if (bsAlert) bsAlert.close();
            } else if (alertEl) {
                alertEl.style.transition = 'opacity 0.5s ease';
                alertEl.style.opacity = '0';
                setTimeout(() => alertEl.remove(), 500);
            }
        }, 6000);
    });
}

/**
 * 2. Animated Counter Numbers (for landing page statistics)
 */
function initAnimatedCounters() {
    const counterElements = document.querySelectorAll('[data-counter-target]');
    if (!counterElements.length) return;

    const animateCounter = (el) => {
        const target = parseInt(el.getAttribute('data-counter-target'), 10) || 0;
        const prefix = el.getAttribute('data-counter-prefix') || '';
        const suffix = el.getAttribute('data-counter-suffix') || '';
        const duration = 1600;
        const frameRate = 30;
        const totalFrames = Math.round((duration / 1000) * frameRate);
        let frame = 0;

        const timer = setInterval(() => {
            frame++;
            const progress = frame / totalFrames;
            // Ease-out cubic
            const currentVal = Math.round(target * (1 - Math.pow(1 - progress, 3)));
            el.textContent = `${prefix}${currentVal.toLocaleString()}${suffix}`;

            if (frame >= totalFrames) {
                clearInterval(timer);
                el.textContent = `${prefix}${target.toLocaleString()}${suffix}`;
            }
        }, 1000 / frameRate);
    };

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        counterElements.forEach((el) => observer.observe(el));
    } else {
        counterElements.forEach((el) => animateCounter(el));
    }
}

/**
 * 3. Password Show/Hide Toggle Button
 */
function initPasswordVisibilityToggles() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach((input) => {
        // If already wrapped or parent has a toggle, skip
        if (input.dataset.toggleInitialized) return;
        input.dataset.toggleInitialized = 'true';

        // Check if there is already a toggle button in the DOM
        let toggleBtn = input.parentElement.querySelector('.password-toggle-btn');
        if (!toggleBtn) {
            // Ensure parent has position relative
            input.parentElement.style.position = 'relative';
            toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'password-toggle-btn';
            toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
            toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
            input.parentElement.appendChild(toggleBtn);
        }

        toggleBtn.addEventListener('click', () => {
            const isPassword = input.getAttribute('type') === 'password';
            input.setAttribute('type', isPassword ? 'text' : 'password');
            toggleBtn.innerHTML = isPassword ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
        });
    });
}

/**
 * 4. Payment Page - Interactive Card Mirror
 */
function initPaymentCardMirror() {
    const cardInput = document.querySelector('input[name="card_number"]');
    const expiryInput = document.querySelector('input[name="expiry"]');
    const nameInput = document.querySelector('input[name="cardholder_name"]');

    const cardDisplay = document.getElementById('cardDisplayNumber');
    const expiryDisplay = document.getElementById('cardDisplayExpiry');
    const nameDisplay = document.getElementById('cardDisplayHolder');

    if (cardInput && cardDisplay) {
        cardInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 16);
            let formatted = val.replace(/(.{4})/g, '$1 ').trim();
            e.target.value = formatted;
            cardDisplay.textContent = formatted || '•••• •••• •••• ••••';
        });
    }

    if (expiryInput && expiryDisplay) {
        expiryInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 4);
            if (val.length >= 3) {
                val = val.substring(0, 2) + '/' + val.substring(2, 4);
            }
            e.target.value = val;
            expiryDisplay.textContent = val || 'MM/YY';
        });
    }

    if (nameInput && nameDisplay) {
        nameInput.addEventListener('input', (e) => {
            nameDisplay.textContent = (e.target.value || 'PATIENT NAME').toUpperCase();
        });
    }
}

/**
 * 5. Symptom Checker - Click chip to insert into textarea
 */
function initSymptomChipsHelper() {
    const textarea = document.querySelector('textarea[name="symptoms_text"]');
    const chips = document.querySelectorAll('.symptom-tag-pill[data-symptom]');

    if (!textarea || !chips.length) return;

    chips.forEach((chip) => {
        chip.addEventListener('click', () => {
            const symptom = chip.getAttribute('data-symptom');
            const current = textarea.value.trim();
            if (current.toLowerCase().includes(symptom.toLowerCase())) return;

            if (current.length === 0) {
                textarea.value = `I am experiencing ${symptom}`;
            } else {
                textarea.value = `${current}, ${symptom}`;
            }
            textarea.focus();
            chip.classList.add('badge-primary-soft');
        });
    });
}

/**
 * 6. File Upload Dropzone dragover effects
 */
function initDropzoneDragEffects() {
    const dropzone = document.querySelector('.upload-dropzone');
    const fileInput = document.getElementById('fileInput');

    if (!dropzone || !fileInput) return;

    ['dragenter', 'dragover'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt && dt.files && dt.files.length) {
            fileInput.files = dt.files;
            // Dispatch change event so existing listener picks it up
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
}
