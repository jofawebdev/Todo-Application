/**
 * Todo App - Enhanced JavaScript with Bootstrap 5 Integration
 * ------------------------------------------------------------
 * Best practices:
 * 1. Bootstrap's native JS components replace custom mobile toggle & tooltips.
 * 2. Custom todo interactions, form enhancements, and animations are preserved.
 * 3. All Bootstrap components are initialized after the DOM is ready.
 * 4. Defensive checks ensure Bootstrap is loaded before using its APIs.
 * 
 * FIX: Delete confirmation button now properly submits the form.
 *      Added e.preventDefault() + this.form.submit() to prevent disabled button from blocking submission.
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initBootstrapComponents();
    initTodoInteractions();
    initFormEnhancements();
    initPriorityFilter();
    initSmoothAnimations();
    autoHideMessages();
    initConfirmationDialogs();   // <-- FIX applied here
    setupVisualFeedback();
    initRippleEffects();
});

// ----------------------------------------------------------------------
// BOOTSTRAP 5 INTEGRATION
// ----------------------------------------------------------------------
function initBootstrapComponents() {
    // ----- Tooltips -----
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } else {
        console.warn('Bootstrap JS not loaded – tooltips are disabled.');
    }

    // ----- Popovers (optional) -----
    // (commented – enable if needed)
}

// ----------------------------------------------------------------------
// CUSTOM TODO INTERACTIONS
// ----------------------------------------------------------------------
function initTodoInteractions() {
    // Add hover/click feedback and keyboard accessibility to todo cards
    const todoCards = document.querySelectorAll('.todo-card');
    
    todoCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.action-btn') && !e.target.closest('a')) {
                this.style.transform = 'scale(0.99)';
                setTimeout(() => { this.style.transform = ''; }, 150);
            }
        });
        
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', 'Todo item. Press Enter to toggle completion.');
        
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const toggleBtn = this.querySelector('.toggle-btn');
                if (toggleBtn) toggleBtn.click();
            }
        });
    });
    
    // Toggle button animation (visual feedback)
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const card = this.closest('.todo-card');
            if (card) {
                card.classList.add('processing');
                const icon = this.querySelector('i');
                const willComplete = icon && icon.classList.contains('fa-circle');
                if (willComplete) {
                    card.classList.add('celebrating');
                    icon.classList.remove('fa-circle');
                    icon.classList.add('fa-check');
                    setTimeout(() => {
                        icon.classList.remove('fa-check');
                        icon.classList.add('fa-circle');
                        card.classList.remove('celebrating');
                    }, 1000);
                }
                setTimeout(() => { card.classList.remove('processing'); }, 500);
            }
        });
    });
}

// ----------------------------------------------------------------------
// FORM ENHANCEMENTS
// ----------------------------------------------------------------------
function initFormEnhancements() {
    const forms = document.querySelectorAll('.todo-form');
    
    forms.forEach(form => {
        const titleInput = form.querySelector('[name="title"]');
        const dueDateInput = form.querySelector('[name="due_date"]');
        const prioritySelect = form.querySelector('[name="priority"]');
        const descriptionTextarea = form.querySelector('[name="description"]');
        
        // Auto-focus title field
        if (titleInput) {
            setTimeout(() => {
                titleInput.focus();
                titleInput.style.animation = 'pulse 2s';
                setTimeout(() => { titleInput.style.animation = ''; }, 2000);
            }, 300);
        }
        
        // Set min date to today for due_date
        if (dueDateInput && !dueDateInput.value) {
            const today = new Date().toISOString().split('T')[0];
            dueDateInput.min = today;
        }
        
        // Character counter for description
        if (descriptionTextarea) {
            const charCounter = document.createElement('div');
            charCounter.className = 'char-counter';
            descriptionTextarea.parentNode.appendChild(charCounter);
            
            const updateCounter = () => {
                const length = descriptionTextarea.value.length;
                charCounter.textContent = `${length}/1000 characters`;
                charCounter.style.color = length > 800 ? 'var(--warning-color)' : 'var(--text-muted)';
            };
            descriptionTextarea.addEventListener('input', updateCounter);
            updateCounter();
        }
        
        // Visual priority indicator
        if (prioritySelect) {
            prioritySelect.addEventListener('change', function() {
                updatePriorityIndicator(this);
            });
            updatePriorityIndicator(prioritySelect);
        }
        
        // Form submit spinner
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.8';
                
                // Fallback: re-enable after 5 seconds if something goes wrong
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                        submitBtn.style.opacity = '1';
                    }
                }, 5000);
            }
        });
    });
}

// ----------------------------------------------------------------------
// PRIORITY INDICATOR (stars)
// ----------------------------------------------------------------------
function updatePriorityIndicator(selectElement) {
    const container = selectElement.closest('.form-group');
    if (!container) return;
    
    const existingIndicator = container.querySelector('.priority-visual');
    if (existingIndicator) existingIndicator.remove();
    
    const priority = parseInt(selectElement.value) || 3;
    const indicator = document.createElement('div');
    indicator.className = 'priority-visual';
    indicator.style.marginTop = '0.5rem';
    indicator.style.display = 'flex';
    indicator.style.gap = '0.25rem';
    indicator.style.justifyContent = 'center';
    
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('span');
        star.textContent = i <= priority ? '⭐' : '☆';
        star.style.fontSize = '1.25rem';
        star.style.opacity = i <= priority ? '1' : '0.3';
        indicator.appendChild(star);
    }
    container.appendChild(indicator);
}

// ----------------------------------------------------------------------
// PRIORITY FILTER BUTTONS
// ----------------------------------------------------------------------
function initPriorityFilter() {
    const priorityButtons = document.querySelectorAll('.priority-btn:not(.clear-filter)');
    priorityButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!this.classList.contains('active')) {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => { this.style.transform = ''; }, 200);
            }
        });
    });
    
    const clearFilterBtn = document.querySelector('.clear-filter');
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function() {
            this.style.animation = 'shake 0.5s';
            setTimeout(() => { this.style.animation = ''; }, 500);
        });
    }
}

// ----------------------------------------------------------------------
// SMOOTH ANIMATIONS
// ----------------------------------------------------------------------
function initSmoothAnimations() {
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.style.opacity = '0';
        mainContent.style.animation = 'fadeIn 0.5s ease 0.3s forwards';
    }
    
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.animation = `slideUp 0.5s ease ${index * 0.1}s forwards`;
    });
}

// ----------------------------------------------------------------------
// CONFIRMATION DIALOGS (FIXED for delete confirmation)
// ----------------------------------------------------------------------
function initConfirmationDialogs() {
    const deleteButtons = document.querySelectorAll('.delete-btn, .btn-danger');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // --- CASE 1: Delete confirmation page (btn-danger inside .delete-actions) ---
            if (this.classList.contains('btn-danger') && this.closest('.delete-actions')) {
                // 🛑 PREVENT DEFAULT – we will manually submit the form
                e.preventDefault();

                const card = this.closest('.delete-card');
                if (card) {
                    card.style.animation = 'shake 0.5s';
                    setTimeout(() => { card.style.animation = ''; }, 500);
                }

                // Disable button and show spinner
                this.disabled = true;
                this.innerHTML = '<span class="spinner"></span> Deleting...';

                // ✅ MANUALLY SUBMIT THE FORM – this is the FIX
                // The form is submitted even though the button is disabled.
                if (this.form) {
                    this.form.submit();
                }

                // Fallback: re-enable after 2 seconds if the submission failed (e.g., network error)
                setTimeout(() => {
                    if (this.disabled) {
                        this.disabled = false;
                        this.innerHTML = '<span class="btn-icon">🗑️</span> Yes, Delete Permanently';
                    }
                }, 2000);
            }
            // --- CASE 2: Delete button on todo cards (original confirmation dialog) ---
            else if (this.classList.contains('delete-btn')) {
                e.preventDefault();   // Stop immediate navigation
                const todoCard = this.closest('.todo-card');
                const todoTitle = todoCard?.querySelector('.todo-title')?.textContent || 'this task';
                if (confirm(`Are you sure you want to delete "${todoTitle}"?`)) {
                    if (todoCard) {
                        todoCard.style.animation = 'fadeOut 0.5s ease forwards';
                    }
                    // Navigate to the delete URL after animation
                    setTimeout(() => { window.location.href = this.href; }, 500);
                }
            }
        });
    });
}

// ----------------------------------------------------------------------
// AUTO-HIDE MESSAGES
// ----------------------------------------------------------------------
function autoHideMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        if (message.classList.contains('message-success') || message.classList.contains('message-info')) {
            setTimeout(() => {
                if (message.parentNode) {
                    message.style.animation = 'fadeOut 0.5s ease forwards';
                    setTimeout(() => {
                        if (message.parentNode) message.remove();
                    }, 500);
                }
            }, 5000);
        }
    });
}

// ----------------------------------------------------------------------
// VISUAL FEEDBACK & RIPPLE EFFECTS
// ----------------------------------------------------------------------
function setupVisualFeedback() {
    const style = document.createElement('style');
    style.textContent = `
        .spinner {
            display: inline-block;
            width: 1em;
            height: 1em;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
            margin-right: 0.5em;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.7; } }
        .processing {
            position: relative;
            pointer-events: none;
        }
        .processing::after {
            content: '';
            position: absolute;
            top:0; left:0; right:0; bottom:0;
            background: rgba(255,255,255,0.7);
            border-radius: inherit;
            animation: pulse 1.5s ease infinite;
        }
        .celebrating {
            animation: celebrate 1s ease;
        }
        @keyframes celebrate {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); box-shadow: 0 0 20px rgba(16,185,129,0.5); }
            100% { transform: scale(1); }
        }
        .char-counter {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
            text-align: right;
            transition: color 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

function initRippleEffects() {
    const rippleStyle = document.createElement('style');
    rippleStyle.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(99,102,241,0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        @keyframes ripple-animation {
            to { transform: scale(4); opacity: 0; }
        }
        @keyframes fadeOut {
            to { opacity: 0; transform: translateY(-20px); }
        }
        @keyframes shake {
            0%,100% { transform: translateX(0); }
            10%,30%,50%,70%,90% { transform: translateX(-5px); }
            20%,40%,60%,80% { transform: translateX(5px); }
        }
    `;
    document.head.appendChild(rippleStyle);
}

// ----------------------------------------------------------------------
// UTILITY FUNCTIONS
// ----------------------------------------------------------------------
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export for module usage (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initTodoInteractions,
        initFormEnhancements,
        debounce,
        throttle
    };
}