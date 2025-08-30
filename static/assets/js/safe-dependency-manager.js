/**
 * Safe Dependency Manager - manages script loading without infinite loops
 */
class SafeDependencyManager {
    constructor() {
        this.loadedScripts = new Set();
        this.loadingScripts = new Set();
        this.failedScripts = new Set();
        this.isInitialized = false;
        this.maxRetries = 2;
        this.retryCount = new Map();
        
        // Prevent multiple initializations
        if (window.SafeDependencyManager && window.SafeDependencyManager.isInitialized) {
            return window.SafeDependencyManager;
        }
        
        this.init();
        window.SafeDependencyManager = this;
    }

    init() {
        if (this.isInitialized) return;
        
        try {
            this.checkCriticalDependencies();
            this.isInitialized = true;
            console.log('SafeDependencyManager initialized');
        } catch (error) {
            console.error('Failed to initialize SafeDependencyManager:', error);
        }
    }

    checkCriticalDependencies() {
        const criticalDeps = [
            { name: 'jQuery', check: () => typeof window.$ !== 'undefined' },
            { name: 'Bootstrap', check: () => typeof window.bootstrap !== 'undefined' },
            { name: 'React', check: () => typeof window.React !== 'undefined' }
        ];

        criticalDeps.forEach(dep => {
            if (dep.check()) {
                console.log(`✓ ${dep.name} loaded successfully`);
                this.loadedScripts.add(dep.name.toLowerCase());
            } else {
                console.warn(`⚠ ${dep.name} not found`);
            }
        });
    }

    loadScript(src, options = {}) {
        return new Promise((resolve, reject) => {
            // Check if already loaded or loading
            if (this.loadedScripts.has(src)) {
                resolve();
                return;
            }
            
            if (this.loadingScripts.has(src)) {
                // Wait for existing load
                const checkLoaded = () => {
                    if (this.loadedScripts.has(src)) {
                        resolve();
                    } else if (this.failedScripts.has(src)) {
                        reject(new Error(`Script failed to load: ${src}`));
                    } else {
                        setTimeout(checkLoaded, 100);
                    }
                };
                checkLoaded();
                return;
            }

            // Check retry limit
            const retries = this.retryCount.get(src) || 0;
            if (retries >= this.maxRetries) {
                reject(new Error(`Max retries exceeded for: ${src}`));
                return;
            }

            this.loadingScripts.add(src);
            
            const script = document.createElement('script');
            script.src = src;
            script.async = options.async !== false;
            
            const cleanup = () => {
                this.loadingScripts.delete(src);
                document.head.removeChild(script);
            };

            script.onload = () => {
                this.loadedScripts.add(src);
                this.loadingScripts.delete(src);
                console.log(`✓ Script loaded: ${src}`);
                resolve();
            };

            script.onerror = () => {
                this.failedScripts.add(src);
                this.loadingScripts.delete(src);
                this.retryCount.set(src, retries + 1);
                
                console.error(`✗ Script failed to load: ${src}`);
                
                // Retry with delay
                if (retries < this.maxRetries) {
                    setTimeout(() => {
                        this.loadScript(src, options).then(resolve).catch(reject);
                    }, 1000 * (retries + 1));
                } else {
                    reject(new Error(`Failed to load script: ${src}`));
                }
            };

            // Timeout handling
            const timeout = options.timeout || 10000;
            const timeoutId = setTimeout(() => {
                if (this.loadingScripts.has(src)) {
                    cleanup();
                    this.failedScripts.add(src);
                    reject(new Error(`Script load timeout: ${src}`));
                }
            }, timeout);

            script.onload = () => {
                clearTimeout(timeoutId);
                this.loadedScripts.add(src);
                this.loadingScripts.delete(src);
                console.log(`✓ Script loaded: ${src}`);
                resolve();
            };

            try {
                document.head.appendChild(script);
            } catch (error) {
                cleanup();
                reject(error);
            }
        });
    }

    loadScripts(scripts, options = {}) {
        if (options.sequential) {
            return scripts.reduce((promise, script) => {
                return promise.then(() => this.loadScript(script, options));
            }, Promise.resolve());
        } else {
            return Promise.all(scripts.map(script => this.loadScript(script, options)));
        }
    }

    isLoaded(scriptName) {
        return this.loadedScripts.has(scriptName.toLowerCase());
    }

    getStatus() {
        return {
            loaded: Array.from(this.loadedScripts),
            loading: Array.from(this.loadingScripts),
            failed: Array.from(this.failedScripts)
        };
    }

    // Safe fallback loading
    loadWithFallback(primary, fallback, options = {}) {
        return this.loadScript(primary, options).catch(() => {
            console.warn(`Primary script failed, trying fallback: ${fallback}`);
            return this.loadScript(fallback, options);
        });
    }
}

// Initialize safely
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new SafeDependencyManager();
        });
    } else {
        new SafeDependencyManager();
    }
} catch (error) {
    console.error('Failed to initialize SafeDependencyManager:', error);
}