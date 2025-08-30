/**
 * CSS 404 Fix - Removes problematic CSS links that cause 404 errors
 */

document.addEventListener('DOMContentLoaded', function() {
    // Remove problematic CSS links that return 404
    const problematicPaths = [
        'frontend/src/design-system/styles/tokens.css',
        'frontend/src/design-system/styles/base.css', 
        'frontend/src/design-system/styles/utilities.css'
    ];
    
    const links = document.querySelectorAll('link[rel="stylesheet"]');
    let removedCount = 0;
    
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && problematicPaths.some(path => href.includes(path))) {
            link.remove();
            removedCount++;
            console.log('Removed problematic CSS link:', href);
        }
    });
    
    if (removedCount > 0) {
        console.log(`✅ Removed ${removedCount} problematic CSS links`);
    }
});