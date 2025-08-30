document.addEventListener('DOMContentLoaded', function() {
            // Intersection Observer for lazy loading
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.getAttribute('data-src');
                        const srcset = img.getAttribute('data-srcset');
                        
                        if (src) {
                            img.src = src;
                            img.removeAttribute('data-src');
                        }
                        
                        if (srcset) {
                            img.srcset = srcset;
                            img.removeAttribute('data-srcset');
                        }
                        
                        img.classList.remove('lazy-load');
                        img.classList.add('lazy-loaded');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '200px 0px'  // Load 200px before entering viewport
            });
            
            // Observe all lazy images
            document.querySelectorAll('img.lazy-load').forEach(img => {
                imageObserver.observe(img);
            });
            
            // Fallback for browsers without Intersection Observer
            if (!('IntersectionObserver' in window)) {
                document.querySelectorAll('img.lazy-load').forEach(img => {
                    const src = img.getAttribute('data-src');
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                    }
                });
            }
        });