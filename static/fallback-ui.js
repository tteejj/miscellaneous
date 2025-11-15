// Fallback UI for old browsers and limited devices
// Provides basic functionality when modern features aren't available

(function() {
    'use strict';

    // Wait for compat.js to load
    if (!window.BrowserCapabilities || !window.FeatureFlags) {
        console.error('compat.js must be loaded first!');
        return;
    }

    var cap = window.BrowserCapabilities;
    var flags = window.FeatureFlags;

    // ============================================================================
    // SSE FALLBACK - Polling for old browsers without EventSource
    // ============================================================================

    if (!flags.enableSSE) {
        console.log('SSE not available - using polling fallback');

        window.MessagePolling = {
            interval: null,
            lastMessageId: 0,
            pollFrequency: 5000, // 5 seconds

            start: function(channelId) {
                var self = this;
                this.channelId = channelId;

                // Poll immediately
                this.poll();

                // Then poll every 5 seconds
                this.interval = setInterval(function() {
                    self.poll();
                }, this.pollFrequency);
            },

            stop: function() {
                if (this.interval) {
                    clearInterval(this.interval);
                    this.interval = null;
                }
            },

            poll: function() {
                var self = this;
                var url = '/api/messages/' + this.channelId + '?after=' + this.lastMessageId;

                fetch(url)
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data.messages && data.messages.length > 0) {
                            data.messages.forEach(function(msg) {
                                if (typeof window.handleNewMessage === 'function') {
                                    window.handleNewMessage(msg);
                                }
                                self.lastMessageId = Math.max(self.lastMessageId, msg.id);
                            });
                        }
                    })
                    .catch(function(error) {
                        console.error('Polling error:', error);
                    });
            }
        };
    }

    // ============================================================================
    // IMAGE LAZY LOADING FALLBACK
    // ============================================================================

    if (!flags.enableImageLazyLoad || !cap.intersectionObserver) {
        console.log('IntersectionObserver not available - using scroll-based lazy loading');

        window.LazyLoadFallback = {
            images: [],

            init: function() {
                var self = this;
                this.loadVisibleImages();

                // Debounced scroll handler
                var scrollHandler = compatUtils.debounce(function() {
                    self.loadVisibleImages();
                }, 200);

                compatUtils.on(window, 'scroll', scrollHandler);
                compatUtils.on(window, 'resize', scrollHandler);
            },

            register: function(img) {
                this.images.push(img);
            },

            loadVisibleImages: function() {
                var windowHeight = window.innerHeight || document.documentElement.clientHeight;
                var scrollTop = window.pageYOffset || document.documentElement.scrollTop;

                this.images = this.images.filter(function(img) {
                    var rect = img.getBoundingClientRect();
                    var isVisible = rect.top < windowHeight + 200 && rect.bottom > -200;

                    if (isVisible && img.dataset.src) {
                        img.src = img.dataset.src;
                        delete img.dataset.src;
                        return false; // Remove from array
                    }

                    return true; // Keep in array
                });
            }
        };

        // Auto-init when DOM ready
        if (document.readyState === 'loading') {
            compatUtils.on(document, 'DOMContentLoaded', function() {
                window.LazyLoadFallback.init();
            });
        } else {
            window.LazyLoadFallback.init();
        }
    }

    // ============================================================================
    // SIMPLIFIED MESSAGE RENDERING FOR OLD BROWSERS
    // ============================================================================

    if (flags.useSimpleUI) {
        window.renderMessageSimple = function(msg) {
            // Simple HTML string generation (no templates)
            var html = '<div class="message" data-id="' + msg.id + '">';

            // Avatar
            if (msg.avatar_url) {
                html += '<img class="message-avatar" src="' + msg.avatar_url + '" alt="' + msg.username + '">';
            } else {
                var initials = msg.username.substring(0, 2).toUpperCase();
                html += '<div class="message-avatar" style="background-color:' + (msg.avatar_color || '#667eea') + '">' + initials + '</div>';
            }

            // Header
            html += '<div class="message-header">';
            html += '<strong>' + msg.username + '</strong> ';
            html += '<span class="timestamp">' + formatTimestamp(msg.timestamp) + '</span>';
            html += '</div>';

            // Content
            html += '<div class="message-content">';

            if (msg.message_type === 'text') {
                html += escapeHtml(msg.content);
            } else if (msg.message_type === 'image') {
                if (msg.image) {
                    html += '<a href="/uploads/' + msg.image.filename + '" target="_blank">';
                    html += '<img src="/uploads/thumbnails/' + msg.image.thumbnail_filename + '" alt="Image" style="max-width:100%;height:auto;">';
                    html += '</a>';
                }
            }

            html += '</div>';
            html += '</div>';

            return html;
        };

        // Simple timestamp formatting
        function formatTimestamp(timestamp) {
            var date = new Date(timestamp);
            var hours = date.getHours();
            var minutes = date.getMinutes();
            var ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12 || 12;
            minutes = minutes < 10 ? '0' + minutes : minutes;
            return hours + ':' + minutes + ' ' + ampm;
        }

        // HTML escape for security
        function escapeHtml(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    // ============================================================================
    // FORM SUBMISSION FALLBACK FOR VERY OLD BROWSERS
    // ============================================================================

    if (!cap.fetch && !cap.promise) {
        console.log('Using form submission fallback');

        window.sendMessageFallback = function(channelId, content) {
            // Create a hidden form
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = '/api/messages/' + channelId;
            form.style.display = 'none';

            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'message';
            input.value = content;

            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        };
    }

    // ============================================================================
    // TINY SCREEN OPTIMIZATIONS
    // ============================================================================

    if (cap.screenSize === 'tiny') {
        console.log('Tiny screen optimizations enabled');

        // Limit message history to save memory
        window.MAX_MESSAGES = 30;

        // Disable animations globally
        document.documentElement.style.cssText += ';animation:none!important;transition:none!important;';

        // Add helper to toggle sidebar on tiny screens
        window.toggleSidebar = function() {
            var sidebar = compatUtils.querySelector('.sidebar');
            if (sidebar) {
                if (sidebar.style.display === 'none') {
                    sidebar.style.display = 'block';
                    sidebar.style.position = 'fixed';
                    sidebar.style.top = '0';
                    sidebar.style.left = '0';
                    sidebar.style.bottom = '0';
                    sidebar.style.width = '80%';
                    sidebar.style.zIndex = '1000';
                    sidebar.style.backgroundColor = '#fff';
                } else {
                    sidebar.style.display = 'none';
                }
            }
        };

        // Auto-hide keyboard on message send (mobile)
        window.hideKeyboard = function() {
            if (document.activeElement) {
                document.activeElement.blur();
            }
        };
    }

    // ============================================================================
    // LOW MEMORY MODE
    // ============================================================================

    if (flags.lowMemoryMode) {
        console.log('Low memory mode enabled');

        // Aggressive message limit
        window.MAX_MESSAGES = 20;

        // Disable image auto-loading
        window.DISABLE_IMAGE_AUTOLOAD = true;

        // Add click handler to load images on demand
        window.loadImageOnDemand = function(img) {
            if (img.dataset.src) {
                img.src = img.dataset.src;
                delete img.dataset.src;
                img.style.opacity = '1';
            }
        };

        // Clear old messages periodically
        setInterval(function() {
            var messages = compatUtils.querySelectorAll('.message');
            if (messages.length > window.MAX_MESSAGES) {
                for (var i = 0; i < messages.length - window.MAX_MESSAGES; i++) {
                    messages[i].parentNode.removeChild(messages[i]);
                }
            }
        }, 30000); // Every 30 seconds
    }

    // ============================================================================
    // TOUCH DEVICE OPTIMIZATIONS
    // ============================================================================

    if (cap.touchSupport) {
        // Add tap-to-toggle for message actions
        compatUtils.on(document, 'touchstart', function(e) {
            var message = e.target.closest('.message');
            if (message) {
                var actions = message.querySelector('.message-actions');
                if (actions) {
                    if (actions.style.display === 'none' || !actions.style.display) {
                        actions.style.display = 'block';
                        actions.style.opacity = '1';
                    } else {
                        actions.style.display = 'none';
                    }
                }
            }
        });

        // Prevent double-tap zoom (accessibility concern, but can be annoying)
        var lastTouchEnd = 0;
        compatUtils.on(document, 'touchend', function(e) {
            var now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        });
    }

    // ============================================================================
    // EXPOSE FALLBACK API
    // ============================================================================

    window.FallbackUI = {
        cap: cap,
        flags: flags,
        initialized: true
    };

    console.log('Fallback UI initialized');

})();
