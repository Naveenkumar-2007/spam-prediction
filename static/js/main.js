// ===================================
// SMS Spam Detector - Main JavaScript
// Handles form submission and UI updates
// ===================================

// DOM Elements
const spamForm = document.getElementById('spamForm');
const messageInput = document.getElementById('message');
const charCount = document.getElementById('charCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const loadingState = document.getElementById('loadingState');
const initialState = document.getElementById('initialState');
const resultDisplay = document.getElementById('resultDisplay');
const errorDisplay = document.getElementById('errorDisplay');
const exampleButtons = document.querySelectorAll('.example-btn');

// Initialize character counter
if (messageInput && charCount) {
    messageInput.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
}

// Clear button functionality
if (clearBtn) {
    clearBtn.addEventListener('click', function() {
        messageInput.value = '';
        charCount.textContent = '0';
        resetDisplay();
        messageInput.focus();
    });
}

// Example buttons functionality
exampleButtons.forEach(button => {
    button.addEventListener('click', function() {
        const exampleText = this.getAttribute('data-text');
        messageInput.value = exampleText;
        charCount.textContent = exampleText.length;
        messageInput.focus();
        // Scroll to textarea
        messageInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
});

// Form submission
if (spamForm) {
    spamForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        
        // Validation
        if (!message) {
            showError('Please enter a message to analyze');
            return;
        }
        
        if (message.length < 5) {
            showError('Message is too short. Please enter at least 5 characters.');
            return;
        }
        
        // Show loading state
        showLoading();
        
        try {
            // Send prediction request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            // If response is not OK, try to read JSON error message, otherwise show status
            if (!response.ok) {
                let serverMessage = '';
                try {
                    const errData = await response.json();
                    serverMessage = errData && errData.message ? ` - ${errData.message}` : '';
                } catch (jsonErr) {
                    // response wasn't JSON
                    serverMessage = '';
                }
                showError(`Server returned ${response.status}${serverMessage}`);
                return;
            }

            // Parse successful JSON
            let data;
            try {
                data = await response.json();
            } catch (parseErr) {
                console.error('Invalid JSON from server', parseErr);
                showError('Received invalid response from server.');
                return;
            }

            if (data.error) {
                showError(data.message || 'An error occurred during prediction');
            } else {
                showResult(data);
            }

        } catch (error) {
            console.error('Prediction error:', error);
            showError('Failed to connect to the server. Please check your network and try again.');
        }
    });
}

// Show loading state
function showLoading() {
    hideAllStates();
    if (loadingState) {
        loadingState.style.display = 'block';
    }
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Analyzing...</span>';
    }
}

// Show result
function showResult(data) {
    hideAllStates();
    
    if (!resultDisplay) return;
    
    resultDisplay.style.display = 'block';
    
    // Update result badge
    const resultBadge = document.getElementById('resultBadge');
    const resultText = document.getElementById('resultText');
    
    if (resultBadge && resultText) {
        resultBadge.className = 'result-badge ' + (data.is_spam ? 'spam' : 'legitimate');
        resultText.textContent = data.prediction;
        
        // Update icon
        const icon = resultBadge.querySelector('i');
        if (icon) {
            if (data.is_spam) {
                icon.className = 'fas fa-exclamation-triangle';
            } else {
                icon.className = 'fas fa-check-circle';
            }
        }
    }
    
    // Update confidence
    const confidenceValue = document.getElementById('confidenceValue');
    const progressFill = document.getElementById('progressFill');
    
    if (confidenceValue) {
        confidenceValue.textContent = data.confidence + '%';
    }
    
    if (progressFill) {
        // Animate progress bar
        setTimeout(() => {
            progressFill.style.width = data.confidence + '%';
            
            // Change color based on spam/legitimate
            if (data.is_spam) {
                progressFill.style.background = 'var(--gradient-danger)';
            } else {
                progressFill.style.background = 'var(--gradient-success)';
            }
        }, 100);
    }
    
    // Update classification text
    const classificationText = document.getElementById('classificationText');
    if (classificationText) {
        if (data.is_spam) {
            classificationText.innerHTML = '<span style="color: var(--danger-color);">⚠️ This message appears to be SPAM</span>';
        } else {
            classificationText.innerHTML = '<span style="color: var(--success-color);">✓ This message appears to be LEGITIMATE</span>';
        }
    }
    
    // Update accuracy text
    const accuracyText = document.getElementById('accuracyText');
    if (accuracyText) {
        let accuracyLevel = 'High';
        if (data.confidence < 60) {
            accuracyLevel = 'Low';
        } else if (data.confidence < 80) {
            accuracyLevel = 'Medium';
        }
        accuracyText.textContent = `${accuracyLevel} (${data.confidence}% confidence)`;
    }
    
    // Update analyzed message
    const analyzedMessage = document.getElementById('analyzedMessage');
    if (analyzedMessage) {
        analyzedMessage.textContent = data.message;
    }
    
    // Reset button
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i><span>Analyze Message</span>';
    }
    
    // Scroll to result
    resultDisplay.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Add animation
    resultDisplay.style.animation = 'fadeIn 0.5s ease-out';
}

// Show error
function showError(message) {
    hideAllStates();
    
    if (errorDisplay) {
        errorDisplay.style.display = 'block';
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.textContent = message;
        }
    }
    
    // Reset button
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i><span>Analyze Message</span>';
    }
    
    // Auto-hide error after 5 seconds
    setTimeout(() => {
        if (errorDisplay && errorDisplay.style.display === 'block') {
            resetDisplay();
        }
    }, 5000);
}

// Hide all states
function hideAllStates() {
    if (loadingState) loadingState.style.display = 'none';
    if (initialState) initialState.style.display = 'none';
    if (resultDisplay) resultDisplay.style.display = 'none';
    if (errorDisplay) errorDisplay.style.display = 'none';
}

// Reset display to initial state
function resetDisplay() {
    hideAllStates();
    if (initialState) {
        initialState.style.display = 'block';
    }
    
    // Reset progress bar
    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
        progressFill.style.width = '0%';
        progressFill.style.background = 'var(--gradient-primary)';
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (spamForm) {
            spamForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to clear
    if (e.key === 'Escape') {
        if (clearBtn) {
            clearBtn.click();
        }
    }
});

// Add tooltip for keyboard shortcuts
if (analyzeBtn) {
    analyzeBtn.title = 'Analyze (Ctrl+Enter)';
}

if (clearBtn) {
    clearBtn.title = 'Clear (Esc)';
}

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add active class to current nav item
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-menu a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
    }
});

// Console greeting
console.log('%c🚀 SMS Spam Detector', 'font-size: 20px; font-weight: bold; color: #6366f1;');
console.log('%c💡 Built with TensorFlow & Flask', 'font-size: 14px; color: #64748b;');
console.log('%c📊 GitHub: https://github.com/Naveenkumar-2007/spam-prediction', 'font-size: 12px; color: #10b981;');

// Performance monitoring
if (window.performance && window.performance.timing) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`⚡ Page loaded in ${pageLoadTime}ms`);
        }, 0);
    });
}

// Service Worker for PWA (optional future enhancement)
if ('serviceWorker' in navigator) {
    // Uncomment when you want to add PWA support
    // navigator.serviceWorker.register('/sw.js')
    //     .then(reg => console.log('Service Worker registered'))
    //     .catch(err => console.log('Service Worker registration failed'));
}
