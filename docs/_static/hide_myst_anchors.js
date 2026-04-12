/* Hide MyST anchor syntax {#...} from heading text and navigation */
function removeMystAnchors() {
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, a, span, .toc .reference, .toctree .reference, .nav-link, .reference.internal').forEach(function(el) {
        if (el.innerHTML && /\{#[a-zA-Z0-9_-]+\}/.test(el.innerHTML)) {
            el.innerHTML = el.innerHTML.replace(/\s*\{#[a-zA-Z0-9_-]+\}/g, '');
        }
    });
}
document.addEventListener('DOMContentLoaded', removeMystAnchors);
// Also run after dynamic content loads (theme navigation)
if (typeof MutationObserver !== 'undefined') {
    var observer = new MutationObserver(function() { setTimeout(removeMystAnchors, 100); });
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(function() { observer.disconnect(); }, 5000);
}
