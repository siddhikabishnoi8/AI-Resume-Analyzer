// Global Frontend Scripts for ResumeAI

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initMobileMenu();
    initFAQAccordions();
    initAuthForms();
});

// Toast System
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Choose icon based on toast type
    let icon = 'fa-circle-info';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-circle-exmark';
    if (type === 'warning') icon = 'fa-triangle-exclamation';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto dismiss after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s reverse forwards';
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }, 4000);
}

// Light / Dark Theme toggle sync
function initThemeToggle() {
    const themeBtn = document.getElementById('theme-toggle');
    if (!themeBtn) return;
    
    themeBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        showToast(`Switched to ${newTheme} mode!`, 'info');
    });
}

// Mobile Menu toggles
function initMobileMenu() {
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mobileNav = document.getElementById('mobile-nav');
    
    if (!menuBtn || !mobileNav) return;
    
    menuBtn.addEventListener('click', () => {
        const isVisible = mobileNav.style.display === 'flex';
        mobileNav.style.display = isVisible ? 'none' : 'flex';
        menuBtn.innerHTML = isVisible ? '<i class="fa-solid fa-bars"></i>' : '<i class="fa-solid fa-xmark"></i>';
    });
}

// Landing Page FAQ accordion panels
function initFAQAccordions() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(btn => {
        btn.addEventListener('click', () => {
            const item = btn.parentElement;
            
            // Toggle active class
            item.classList.toggle('active');
            
            // Close others if open
            document.querySelectorAll('.faq-item').forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
        });
    });
}

// Handle Form Submits for Authentication (Login / Register)
function initAuthForms() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    // Handle Login Submit
    if (loginForm) {
        // Toggle password visibility
        const toggleBtn = loginForm.querySelector('.pwd-toggle-btn');
        const pwdInput = loginForm.querySelector('#password');
        if (toggleBtn && pwdInput) {
            toggleBtn.addEventListener('click', () => {
                const isPwd = pwdInput.type === 'password';
                pwdInput.type = isPwd ? 'text' : 'password';
                toggleBtn.innerHTML = isPwd ? '<i class="fa-regular fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
            });
        }
        
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = loginForm.querySelector('#email').value;
            const password = loginForm.querySelector('#password').value;
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                const result = await response.get_json ? await response.get_json() : await response.json();
                
                if (result.success) {
                    showToast('Logged in successfully!', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showToast(result.message || 'Login failed', 'error');
                }
            } catch (err) {
                showToast('Server connection failed. Try again.', 'error');
                console.error(err);
            }
        });
    }
    
    // Handle Register Submit
    if (registerForm) {
        // Password togglers
        const togglers = registerForm.querySelectorAll('.pwd-toggle-btn');
        togglers.forEach((btn, idx) => {
            btn.addEventListener('click', () => {
                const input = btn.previousElementSibling;
                const isPwd = input.type === 'password';
                input.type = isPwd ? 'text' : 'password';
                btn.innerHTML = isPwd ? '<i class="fa-regular fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
            });
        });
        
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = registerForm.querySelector('#full_name').value;
            const email = registerForm.querySelector('#email').value;
            const password = registerForm.querySelector('#password').value;
            const confirm_password = registerForm.querySelector('#confirm_password').value;
            
            if (password !== confirm_password) {
                showToast('Passwords do not match.', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        full_name: name,
                        email,
                        password,
                        confirm_password
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast('Registration successful! Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showToast(result.message || 'Registration failed', 'error');
                }
            } catch (err) {
                showToast('Server connection failed. Try again.', 'error');
                console.error(err);
            }
        });
    }
}
