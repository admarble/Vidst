// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function () {
    // Remove duplicate viewport meta tags
    const viewportTags = document.querySelectorAll('meta[name="viewport"]');
    if (viewportTags.length > 1) {
        for (let i = 1; i < viewportTags.length; i++) {
            viewportTags[i].remove();
        }
    }

    // Fix heading hierarchy
    document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(function (heading) {
        const level = parseInt(heading.tagName[1]);
        heading.setAttribute('aria-level', level.toString());
    });

    // Fix caption headings
    document.querySelectorAll('.caption').forEach(function (caption) {
        caption.setAttribute('role', 'heading');
        caption.setAttribute('aria-level', '2');
    });

    // Remove inline styles
    document.querySelectorAll('[style]').forEach(function (element) {
        const style = element.getAttribute('style');
        if (style.includes('background: #2980B9')) {
            element.classList.add('theme-background');
        }
        if (style.includes('width: 100%')) {
            element.classList.add('full-width');
        }
        if (style.includes('display: none')) {
            element.classList.add('hidden');
        }
        element.removeAttribute('style');
    });

    // Fix table accessibility
    document.querySelectorAll('table').forEach(function (table) {
        if (!table.getAttribute('role')) {
            table.setAttribute('role', 'grid');
        }
        table.querySelectorAll('th').forEach(function (header) {
            if (!header.getAttribute('scope')) {
                header.setAttribute('scope', 'col');
            }
        });
    });

    // Add ARIA landmarks
    const nav = document.querySelector('.wy-nav-side');
    if (nav) {
        nav.setAttribute('role', 'navigation');
        nav.setAttribute('aria-label', 'Main navigation');
    }

    const search = document.querySelector('.wy-side-nav-search');
    if (search) {
        search.setAttribute('role', 'search');
    }

    const mainContent = document.querySelector('.wy-nav-content');
    if (mainContent) {
        mainContent.id = 'main-content';
        mainContent.setAttribute('role', 'main');
    }

    // Add skip to content link if missing
    if (!document.querySelector('.skip-to-content')) {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-to-content';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    // Add aria-expanded to expandable sections
    document.querySelectorAll('.wy-menu-vertical li.toctree-l1').forEach(function (section) {
        const link = section.querySelector('a');
        if (link && section.querySelector('ul')) {
            link.setAttribute('aria-expanded', section.classList.contains('current') ? 'true' : 'false');
            link.addEventListener('click', function () {
                const isExpanded = section.classList.contains('current');
                link.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
            });
        }
    });

    // Fix code block accessibility
    document.querySelectorAll('pre').forEach(function (block) {
        block.setAttribute('role', 'region');
        block.setAttribute('aria-label', 'Code example');
        if (!block.hasAttribute('tabindex')) {
            block.setAttribute('tabindex', '0');
        }
    });

    // Add labels to search inputs
    document.querySelectorAll('input[type="text"], input[type="search"]').forEach(function (input) {
        if (!input.getAttribute('aria-label')) {
            input.setAttribute('aria-label', 'Search documentation');
        }
    });

    // Add aria-hidden to decorative icons
    document.querySelectorAll('.fa').forEach(function (icon) {
        if (!icon.getAttribute('aria-hidden')) {
            icon.setAttribute('aria-hidden', 'true');
        }
    });
});
