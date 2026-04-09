/* Hide MyST anchor syntax {#...} from heading text */
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, .toc .reference, .toctree .reference').forEach(function(el) {
        el.innerHTML = el.innerHTML.replace(/\s*\{#[a-zA-Z0-9_-]+\}/g, '');
    });
});
