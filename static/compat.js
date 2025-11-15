// Browser Compatibility & Feature Detection Layer
// Handles old browsers, tiny screens, and graceful degradation

(function() {
    'use strict';

    // ============================================================================
    // FEATURE DETECTION
    // ============================================================================

    window.BrowserCapabilities = {
        // Modern features
        fetch: typeof fetch !== 'undefined',
        promise: typeof Promise !== 'undefined',
        localStorage: (function() {
            try {
                localStorage.setItem('test', 'test');
                localStorage.removeItem('test');
                return true;
            } catch(e) {
                return false;
            }
        })(),
        eventSource: typeof EventSource !== 'undefined',
        flexbox: (function() {
            var div = document.createElement('div');
            return 'flex' in div.style;
        })(),

        // ES6 features
        arrow: (function() {
            try {
                eval('()=>{}');
                return true;
            } catch(e) {
                return false;
            }
        })(),
        const: (function() {
            try {
                eval('const x = 1');
                return true;
            } catch(e) {
                return false;
            }
        })(),

        // APIs
        formData: typeof FormData !== 'undefined',
        intersectionObserver: typeof IntersectionObserver !== 'undefined',
        serviceWorker: 'serviceWorker' in navigator,

        // Screen capabilities
        touchSupport: 'ontouchstart' in window || navigator.maxTouchPoints > 0,

        // Get screen size category
        screenSize: (function() {
            var w = window.innerWidth || document.documentElement.clientWidth;
            if (w < 320) return 'tiny';      // < 320px (old feature phones)
            if (w < 480) return 'small';     // < 480px (old smartphones)
            if (w < 768) return 'mobile';    // < 768px (modern smartphones)
            if (w < 1024) return 'tablet';   // < 1024px (tablets)
            return 'desktop';
        })(),

        // Browser detection
        browser: (function() {
            var ua = navigator.userAgent;
            if (/MSIE|Trident/.test(ua)) return 'ie';
            if (/Edge/.test(ua)) return 'edge';
            if (/Firefox/.test(ua)) return 'firefox';
            if (/Chrome/.test(ua)) return 'chrome';
            if (/Safari/.test(ua)) return 'safari';
            return 'unknown';
        })(),

        // Get browser version
        browserVersion: (function() {
            var ua = navigator.userAgent;
            var match = ua.match(/(?:MSIE |Trident.*rv:|Edge\/|Firefox\/|Chrome\/|Safari\/)(\d+)/);
            return match ? parseInt(match[1]) : 0;
        })()
    };

    // ============================================================================
    // POLYFILLS FOR OLD BROWSERS
    // ============================================================================

    // Array.forEach polyfill (IE8)
    if (!Array.prototype.forEach) {
        Array.prototype.forEach = function(callback, thisArg) {
            for (var i = 0; i < this.length; i++) {
                callback.call(thisArg, this[i], i, this);
            }
        };
    }

    // Array.indexOf polyfill (IE8)
    if (!Array.prototype.indexOf) {
        Array.prototype.indexOf = function(searchElement) {
            for (var i = 0; i < this.length; i++) {
                if (this[i] === searchElement) return i;
            }
            return -1;
        };
    }

    // Array.map polyfill
    if (!Array.prototype.map) {
        Array.prototype.map = function(callback, thisArg) {
            var result = [];
            for (var i = 0; i < this.length; i++) {
                result.push(callback.call(thisArg, this[i], i, this));
            }
            return result;
        };
    }

    // Array.filter polyfill
    if (!Array.prototype.filter) {
        Array.prototype.filter = function(callback, thisArg) {
            var result = [];
            for (var i = 0; i < this.length; i++) {
                if (callback.call(thisArg, this[i], i, this)) {
                    result.push(this[i]);
                }
            }
            return result;
        };
    }

    // Object.keys polyfill (IE8)
    if (!Object.keys) {
        Object.keys = function(obj) {
            var keys = [];
            for (var key in obj) {
                if (obj.hasOwnProperty(key)) {
                    keys.push(key);
                }
            }
            return keys;
        };
    }

    // String.trim polyfill (IE8)
    if (!String.prototype.trim) {
        String.prototype.trim = function() {
            return this.replace(/^\s+|\s+$/g, '');
        };
    }

    // addEventListener polyfill (IE8)
    if (!window.addEventListener) {
        window.addEventListener = function(event, handler) {
            window.attachEvent('on' + event, handler);
        };
        Element.prototype.addEventListener = function(event, handler) {
            this.attachEvent('on' + event, handler);
        };
    }

    // ============================================================================
    // FETCH POLYFILL (using XMLHttpRequest)
    // ============================================================================

    if (!window.BrowserCapabilities.fetch) {
        window.fetch = function(url, options) {
            options = options || {};

            return new Promise(function(resolve, reject) {
                var xhr = new XMLHttpRequest();
                xhr.open(options.method || 'GET', url, true);

                // Set headers
                if (options.headers) {
                    for (var key in options.headers) {
                        xhr.setRequestHeader(key, options.headers[key]);
                    }
                }

                xhr.onload = function() {
                    var response = {
                        ok: xhr.status >= 200 && xhr.status < 300,
                        status: xhr.status,
                        statusText: xhr.statusText,
                        headers: {
                            get: function(name) {
                                return xhr.getResponseHeader(name);
                            }
                        },
                        text: function() {
                            return Promise.resolve(xhr.responseText);
                        },
                        json: function() {
                            return Promise.resolve(JSON.parse(xhr.responseText));
                        }
                    };
                    resolve(response);
                };

                xhr.onerror = function() {
                    reject(new Error('Network error'));
                };

                xhr.send(options.body || null);
            });
        };
    }

    // ============================================================================
    // PROMISE POLYFILL (simplified)
    // ============================================================================

    if (!window.BrowserCapabilities.promise) {
        window.Promise = function(executor) {
            var self = this;
            self.state = 'pending';
            self.value = undefined;
            self.callbacks = [];

            function resolve(value) {
                if (self.state !== 'pending') return;
                self.state = 'fulfilled';
                self.value = value;
                self.callbacks.forEach(function(cb) {
                    if (cb.onFulfilled) cb.onFulfilled(value);
                });
            }

            function reject(reason) {
                if (self.state !== 'pending') return;
                self.state = 'rejected';
                self.value = reason;
                self.callbacks.forEach(function(cb) {
                    if (cb.onRejected) cb.onRejected(reason);
                });
            }

            try {
                executor(resolve, reject);
            } catch (e) {
                reject(e);
            }
        };

        Promise.prototype.then = function(onFulfilled, onRejected) {
            var self = this;
            return new Promise(function(resolve, reject) {
                function handle() {
                    var cb = self.state === 'fulfilled' ? onFulfilled : onRejected;
                    if (!cb) {
                        (self.state === 'fulfilled' ? resolve : reject)(self.value);
                        return;
                    }
                    try {
                        resolve(cb(self.value));
                    } catch (e) {
                        reject(e);
                    }
                }

                if (self.state !== 'pending') {
                    setTimeout(handle, 0);
                } else {
                    self.callbacks.push({
                        onFulfilled: onFulfilled,
                        onRejected: onRejected
                    });
                }
            });
        };

        Promise.prototype.catch = function(onRejected) {
            return this.then(null, onRejected);
        };

        Promise.resolve = function(value) {
            return new Promise(function(resolve) {
                resolve(value);
            });
        };

        Promise.reject = function(reason) {
            return new Promise(function(resolve, reject) {
                reject(reason);
            });
        };
    }

    // ============================================================================
    // LOCALSTORAGE FALLBACK (in-memory)
    // ============================================================================

    if (!window.BrowserCapabilities.localStorage) {
        window.localStorage = (function() {
            var data = {};
            return {
                getItem: function(key) {
                    return data[key] || null;
                },
                setItem: function(key, value) {
                    data[key] = String(value);
                },
                removeItem: function(key) {
                    delete data[key];
                },
                clear: function() {
                    data = {};
                }
            };
        })();
    }

    // ============================================================================
    // FEATURE FLAGS BASED ON CAPABILITIES
    // ============================================================================

    window.FeatureFlags = {
        // Enable/disable features based on browser capabilities
        enableSSE: BrowserCapabilities.eventSource,
        enableServiceWorker: BrowserCapabilities.serviceWorker && BrowserCapabilities.screenSize !== 'tiny',
        enableInfiniteScroll: BrowserCapabilities.intersectionObserver || BrowserCapabilities.screenSize !== 'tiny',
        enableDragDrop: BrowserCapabilities.formData && BrowserCapabilities.screenSize !== 'tiny',
        enableImageLazyLoad: BrowserCapabilities.intersectionObserver || BrowserCapabilities.screenSize !== 'tiny',
        enableAnimations: BrowserCapabilities.screenSize !== 'tiny',
        enableEmojiPicker: BrowserCapabilities.screenSize !== 'tiny',
        enableMarkdown: true, // Always enabled, server-side rendering fallback
        enablePolls: true, // Always enabled
        enableThreading: BrowserCapabilities.screenSize !== 'tiny',

        // UI simplifications for old browsers
        useSimpleUI: BrowserCapabilities.browser === 'ie' || BrowserCapabilities.screenSize === 'tiny',
        useCompactLayout: BrowserCapabilities.screenSize === 'tiny' || BrowserCapabilities.screenSize === 'small',

        // Performance optimizations
        reducedMotion: BrowserCapabilities.screenSize === 'tiny' ||
                       (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches),
        lowMemoryMode: BrowserCapabilities.screenSize === 'tiny'
    };

    // ============================================================================
    // BROWSER WARNING/INFO
    // ============================================================================

    window.showBrowserInfo = function() {
        var cap = BrowserCapabilities;
        var flags = FeatureFlags;

        // Only show warning for very old browsers
        if (cap.browser === 'ie' && cap.browserVersion < 11) {
            var message = 'You are using an outdated browser. Some features may not work correctly. ' +
                         'For the best experience, please upgrade to a modern browser.';

            var banner = document.createElement('div');
            banner.style.cssText = 'background:#ff9800;color:#fff;padding:10px;text-align:center;position:fixed;top:0;left:0;right:0;z-index:10000;font-size:12px;';
            banner.innerHTML = message + ' <a href="#" style="color:#fff;text-decoration:underline;" onclick="this.parentNode.remove();return false;">Dismiss</a>';
            document.body.insertBefore(banner, document.body.firstChild);
        }

        // Info for tiny screens
        if (cap.screenSize === 'tiny') {
            console.log('Tiny screen mode enabled - some features disabled for better performance');
        }
    };

    // ============================================================================
    // UTILITY FUNCTIONS FOR COMPATIBILITY
    // ============================================================================

    window.compatUtils = {
        // Safe JSON parse
        parseJSON: function(str) {
            try {
                return JSON.parse(str);
            } catch (e) {
                return null;
            }
        },

        // Safe querySelector (fallback to getElementById)
        querySelector: function(selector) {
            if (document.querySelector) {
                return document.querySelector(selector);
            }
            // Fallback for old browsers - only works with ID selectors
            if (selector.charAt(0) === '#') {
                return document.getElementById(selector.slice(1));
            }
            return null;
        },

        // Safe querySelectorAll (fallback to getElementsByTagName/ClassName)
        querySelectorAll: function(selector) {
            if (document.querySelectorAll) {
                return document.querySelectorAll(selector);
            }
            // Very basic fallback
            if (selector.charAt(0) === '.') {
                return document.getElementsByClassName(selector.slice(1));
            }
            return document.getElementsByTagName(selector);
        },

        // Safe classList (fallback to className manipulation)
        addClass: function(element, className) {
            if (element.classList) {
                element.classList.add(className);
            } else {
                var classes = element.className.split(' ');
                if (classes.indexOf(className) === -1) {
                    element.className += ' ' + className;
                }
            }
        },

        removeClass: function(element, className) {
            if (element.classList) {
                element.classList.remove(className);
            } else {
                element.className = element.className.replace(new RegExp('\\b' + className + '\\b', 'g'), '').trim();
            }
        },

        // Debounce function for old browsers
        debounce: function(func, wait) {
            var timeout;
            return function() {
                var context = this;
                var args = arguments;
                clearTimeout(timeout);
                timeout = setTimeout(function() {
                    func.apply(context, args);
                }, wait);
            };
        },

        // Safe addEventListener
        on: function(element, event, handler) {
            if (element.addEventListener) {
                element.addEventListener(event, handler);
            } else if (element.attachEvent) {
                element.attachEvent('on' + event, handler);
            }
        }
    };

    // ============================================================================
    // INITIALIZE ON DOM READY
    // ============================================================================

    function init() {
        // Add capability classes to body for CSS targeting
        var body = document.body;
        var cap = BrowserCapabilities;

        // Screen size classes
        compatUtils.addClass(body, 'screen-' + cap.screenSize);

        // Browser classes
        compatUtils.addClass(body, 'browser-' + cap.browser);

        // Feature classes
        if (!cap.flexbox) compatUtils.addClass(body, 'no-flexbox');
        if (!cap.fetch) compatUtils.addClass(body, 'no-fetch');
        if (!cap.eventSource) compatUtils.addClass(body, 'no-sse');
        if (cap.touchSupport) compatUtils.addClass(body, 'touch');
        if (FeatureFlags.useSimpleUI) compatUtils.addClass(body, 'simple-ui');
        if (FeatureFlags.useCompactLayout) compatUtils.addClass(body, 'compact-layout');

        // Show browser info/warnings
        showBrowserInfo();

        // Log capabilities for debugging
        console.log('Browser Capabilities:', cap);
        console.log('Feature Flags:', FeatureFlags);
    }

    // DOM ready handler for old browsers
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(init, 1);
    } else if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', init);
    } else if (document.attachEvent) {
        document.attachEvent('onreadystatechange', function() {
            if (document.readyState === 'complete') init();
        });
    }

})();
