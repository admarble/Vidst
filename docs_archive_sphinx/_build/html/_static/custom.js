// Remove duplicate viewport meta tag
document.addEventListener('DOMContentLoaded', function () {
    const viewportMetas = document.querySelectorAll('meta[name="viewport"]');
    if (viewportMetas.length > 1) {
        viewportMetas[1].remove();
    }
});

// Remove inline styles
document.addEventListener('DOMContentLoaded', function () {
    const elements = document.querySelectorAll('[style]');
    elements.forEach(el => {
        if (el.style.background === '#2980B9') {
            el.classList.add('theme-color-bg');
            el.removeAttribute('style');
        }
    });
});

// Ensure proper ARIA attributes
document.addEventListener('DOMContentLoaded', function () {
    // Fix any remaining heading ARIA issues
    document.querySelectorAll('[role="heading"]').forEach(el => {
        if (!el.hasAttribute('aria-level')) {
            const tagName = el.tagName.toLowerCase();
            if (tagName.match(/^h[1-6]$/)) {
                el.removeAttribute('role'); // Remove redundant role for semantic headings
            } else {
                el.setAttribute('aria-level', '2'); // Default to level 2 for non-semantic headings
            }
        }
    });
});
