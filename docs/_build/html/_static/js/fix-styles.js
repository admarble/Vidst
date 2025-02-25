document.addEventListener('DOMContentLoaded', function () {
    // Remove any remaining inline styles
    const elementsWithStyle = document.querySelectorAll('[style]');
    elementsWithStyle.forEach(el => {
        el.removeAttribute('style');
        if (el.matches('.wy-nav-side, .wy-side-nav-search, .wy-nav-top')) {
            el.classList.add('theme-background');
        }
    });

    // Fix heading ARIA attributes and structure
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, .caption');
    let currentLevel = 1;
    let lastHeading = null;

    headings.forEach(heading => {
        // Set role="heading" if not present
        if (!heading.hasAttribute('role')) {
            heading.setAttribute('role', 'heading');
        }

        // Determine appropriate heading level
        let level;
        if (heading.matches('h1, h2, h3, h4, h5, h6')) {
            level = parseInt(heading.tagName[1]);
        } else if (heading.matches('.caption')) {
            // For caption elements, determine level based on context
            if (heading.closest('.toctree-l1')) {
                level = 2;
            } else if (heading.closest('.toctree-l2')) {
                level = 3;
            } else {
                level = Math.min(currentLevel + 1, 6);
            }
        }

        // Ensure heading levels don't skip (e.g., h1 to h3)
        if (lastHeading) {
            const lastLevel = parseInt(lastHeading.getAttribute('aria-level'));
            if (level > lastLevel + 1) {
                level = lastLevel + 1;
            }
        }

        heading.setAttribute('aria-level', level.toString());
        currentLevel = level;
        lastHeading = heading;
    });

    // Add labels to form elements
    const unlabeledInputs = document.querySelectorAll('input:not([aria-label]):not([type="hidden"])');
    unlabeledInputs.forEach(input => {
        const inputId = input.id || `input-${Math.random().toString(36).substr(2, 9)}`;
        input.id = inputId;

        if (!input.hasAttribute('aria-label')) {
            const placeholder = input.getAttribute('placeholder');
            if (placeholder) {
                input.setAttribute('aria-label', placeholder);
            } else {
                input.setAttribute('aria-label', `${input.type} input`);
            }
        }
    });

    // Add skip to content link if not present
    if (!document.querySelector('.skip-to-content')) {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-to-content';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    // Fix navigation ARIA roles
    const nav = document.querySelector('.wy-nav-side');
    if (nav && !nav.hasAttribute('role')) {
        nav.setAttribute('role', 'navigation');
        nav.setAttribute('aria-label', 'main navigation');
    }

    // Fix search form accessibility
    const searchForm = document.querySelector('.wy-side-nav-search form');
    if (searchForm) {
        searchForm.setAttribute('role', 'search');
        const searchInput = searchForm.querySelector('input[type="text"]');
        if (searchInput && !searchInput.hasAttribute('aria-label')) {
            searchInput.setAttribute('aria-label', 'Search documentation');
        }
    }

    // Fix table of contents accessibility
    const toc = document.querySelector('.wy-menu-vertical');
    if (toc) {
        toc.setAttribute('role', 'navigation');
        toc.setAttribute('aria-label', 'Table of Contents');
    }
});
