// ============================================================
// JAZZMIN CUSTOM JAVASCRIPT - COMPLETE
// ============================================================

// ============================================================
// 0. NUCLEAR FIX: REMOVE ALL TEXT FROM LOGIN-LOGO
// ============================================================
(function() {
    function removeAllTextFromLoginLogo() {
        const loginLogo = document.querySelector('.login-logo');
        if (!loginLogo) return;
        
        // Get the image first
        const img = loginLogo.querySelector('img');
        
        // Clear everything
        loginLogo.innerHTML = '';
        
        // Add the image back
        if (img) {
            loginLogo.appendChild(img);
            img.style.display = 'block';
            img.style.margin = '0 auto';
            img.style.maxWidth = '80px';
            img.style.height = 'auto';
        }
    }
    
    // Run multiple times to catch dynamic content
    removeAllTextFromLoginLogo();
    document.addEventListener('DOMContentLoaded', removeAllTextFromLoginLogo);
    setTimeout(removeAllTextFromLoginLogo, 100);
    setTimeout(removeAllTextFromLoginLogo, 300);
    setTimeout(removeAllTextFromLoginLogo, 500);
    setTimeout(removeAllTextFromLoginLogo, 1000);
})();

// ============================================================
// 1. PREVENT SCROLLING & MOVEMENT ON LOGIN PAGE
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    const loginContainer = document.querySelector(".login-box");
    if (loginContainer) {
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
        document.body.style.transform = 'none';
        document.documentElement.style.transform = 'none';
        document.body.style.touchAction = 'none';
        document.documentElement.style.touchAction = 'none';
        
        const metaViewport = document.querySelector('meta[name="viewport"]');
        if (metaViewport) {
            metaViewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        }
    }
});

// ============================================================
// 2. AVATAR FROM DATA-AVATAR-URL
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    const userAvatar = document.querySelector(".user-avatar");
    if (userAvatar && userAvatar.dataset.avatarUrl) {
        userAvatar.src = userAvatar.dataset.avatarUrl;
    }
});

// ============================================================
// 3. INJECT FLOATING HOME BUTTON (Not on login page)
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    const loginContainer = document.querySelector(".login-box");
    if (!loginContainer) {
        const homeButton = document.createElement("a");
        homeButton.href = "/";
        homeButton.className = "floating-home-btn";
        homeButton.title = "Go to Home";
        homeButton.innerHTML = `<i class="fas fa-home"></i>`;
        document.body.appendChild(homeButton);
    }
});

// ============================================================
// 4. SCROLL-BASED HIDE/SHOW FOR FLOATING HOME BUTTON
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    let lastScrollTop = 0;
    const homeBtn = document.querySelector(".floating-home-btn");

    if (homeBtn) {
        window.addEventListener("scroll", function () {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            if (scrollTop > lastScrollTop) {
                homeBtn.classList.add("hide");
            } else {
                homeBtn.classList.remove("hide");
            }

            lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
        });
    }
});

// ============================================================
// 5. CONFIRM DIALOG FOR DELETE ACTIONS
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll('.deletelink, .btn-danger, [data-action="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// ============================================================
// 6. AUTO-FOCUS ON FIRST INPUT FIELD (Login Page)
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    const loginContainer = document.querySelector(".login-box");
    if (loginContainer) {
        const firstInput = document.querySelector('.login-box input:first-of-type');
        if (firstInput) {
            setTimeout(function() {
                firstInput.focus();
            }, 500);
        }
    }
});

// ============================================================
// 7. PREVENT SHAKING ON LOGIN PAGE (Additional Safety)
// ============================================================
(function() {
    const loginContainer = document.querySelector('.login-box');
    if (loginContainer) {
        document.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, { passive: false });
        
        document.addEventListener('wheel', function(e) {
            e.preventDefault();
        }, { passive: false });
    }
})();

// ============================================================
// END OF JAVASCRIPT FILE
// ============================================================