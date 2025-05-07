/* ===================================================================
 * Main JS
 * ------------------------------------------------------------------- */

(function(html) {

    'use strict';
    
    /* Reusable Helper Functions
    * -------------------------------------------------- */
    function copyToClipboard(text, button) {
        // Try to use modern Clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text)
                .then(() => updateButtonState(button, true))
                .catch(err => {
                    console.error('Clipboard API failed:', err);
                    fallbackCopyToClipboard(text, button);
                });
        } else {
            // Fall back to deprecated execCommand method for older browsers
            fallbackCopyToClipboard(text, button);
        }
    }
    
    function fallbackCopyToClipboard(text, button) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        // Add to body temporarily
        document.body.appendChild(textarea);
        
        try {
            textarea.select();
            const success = document.execCommand('copy');
            if (success) {
                updateButtonState(button, true);
            } else {
                console.error('Copy command failed');
                updateButtonState(button, false);
            }
        } catch (err) {
            console.error('Fallback copy failed:', err);
            updateButtonState(button, false);
        } finally {
            document.body.removeChild(textarea);
        }
    }
    
    function updateButtonState(button, success) {
        if (success) {
            const icon = button.querySelector('i');
            button.classList.add('copied');
            
            if (icon) {
                icon.classList.remove('fa-copy');
                icon.classList.add('fa-check');
            }
            
            // Reset button state after 2 seconds
            setTimeout(() => {
                button.classList.remove('copied');
                if (icon) {
                    icon.classList.remove('fa-check');
                    icon.classList.add('fa-copy');
                }
            }, 2000);
        }
    }

    /* Preloader
    * -------------------------------------------------- */
    const preloader = document.querySelector("#preloader");
    if (preloader) {
        window.addEventListener('load', function() {
            document.querySelector('body').classList.remove('ss-preload');
            document.querySelector('body').classList.add('ss-loaded');
            preloader.style.display = 'none';
        });
    }
    
    // No need for a resize event handler as the CSS will handle everything

    // Only load content if the functions exist
    if (typeof loadAboutContent === 'function') {
        window.addEventListener('load', loadAboutContent);
    }
    if (typeof loadNewsContent === 'function') {
        window.addEventListener('load', loadNewsContent);
    }

    /* Load Featured Papers - Only on main page
    * -------------------------------------------------- */
    const loadFeaturedPapers = async () => {
        // Only load featured papers if we're on the main page
        if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
            try {
                const response = await fetch('/research/');
                if (!response.ok) {
                    throw new Error(`Failed to fetch research content: ${response.status} ${response.statusText}`);
                }
                
                const text = await response.text();
                
                // Create a temporary div to parse the HTML
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = text;
                
                // Find all paper sections
                const paperSections = tempDiv.querySelectorAll('h3');
                const featuredSections = Array.from(paperSections).filter(section => {
                    // Find the next tags element
                    let nextEl = section.nextElementSibling;
                    while (nextEl && !nextEl.matches('tags')) {
                        nextEl = nextEl.nextElementSibling;
                    }
                    return nextEl && nextEl.textContent.includes('Featured');
                });

                // Get the featured container
                const featuredContainer = document.querySelector('.featured-item__image');
                if (featuredContainer) {
                    // Clear existing content
                    featuredContainer.innerHTML = '';
                    
                    // Create a wrapper for featured papers
                    const wrapper = document.createElement('div');
                    wrapper.className = 'featured-papers';
                    
                    // Add each featured paper
                    featuredSections.forEach((section) => {
                        const paperDiv = document.createElement('div');
                        paperDiv.className = 'featured-paper';
                        paperDiv.style.cursor = 'pointer';
                        
                        // Get all content until the next h3 or end
                        let content = [section.cloneNode(true)];
                        let nextEl = section.nextElementSibling;
                        
                        while (nextEl && !nextEl.matches('h3')) {
                            // Skip the Highlights section and its list
                            if (nextEl.textContent.trim() === 'Highlights' || 
                                (nextEl.matches('ul') && nextEl.previousElementSibling && 
                                 nextEl.previousElementSibling.textContent.trim() === 'Highlights')) {
                                nextEl = nextEl.nextElementSibling;
                                continue;
                            }
                            
                            // Include everything else (tags, images, iframes)
                            const clone = nextEl.cloneNode(true);
                            
                            // If it's a tags element, make spans clickable
                            if (clone.matches('tags')) {
                                Array.from(clone.children).forEach(span => {
                                    span.style.cursor = 'pointer';
                                    span.addEventListener('click', (e) => {
                                        e.stopPropagation(); // Prevent container click
                                        window.location.href = `/research/?tag=${span.textContent.trim()}`;
                                    });
                                });
                            }
                            
                            content.push(clone);
                            nextEl = nextEl.nextElementSibling;
                        }
                        
                        // Get the paper title for creating the anchor
                        const title = content[0];
                        const originalTitle = title.textContent;
                        title.textContent = title.textContent.replace(/^\[\d+\]\s*/, '');
                        
                        content.forEach(el => paperDiv.appendChild(el));
                        
                        // Make the entire container clickable
                        paperDiv.addEventListener('click', (e) => {
                            // Don't navigate if clicking on a link, tag, or iframe
                            if (e.target.closest('a') || e.target.closest('tags') || e.target.closest('iframe')) {
                                return;
                            }
                            
                            // Extract paper number and navigate
                            const paperNumber = originalTitle.match(/^\[(\d+)\]/)?.[1];
                            if (paperNumber) {
                                // Navigate to research page with the paper ID
                                window.location.href = `/research/#${paperNumber}`;
                            } else {
                                window.location.href = '/research/';
                            }
                        });
                        
                        // Prevent iframe clicks from triggering container click
                        const iframes = paperDiv.querySelectorAll('iframe');
                        iframes.forEach(iframe => {
                            iframe.addEventListener('click', (e) => {
                                e.stopPropagation();
                            });
                        });
                        
                        // Prevent link clicks from triggering container click
                        const links = paperDiv.querySelectorAll('a');
                        links.forEach(link => {
                            link.addEventListener('click', (e) => {
                                e.stopPropagation();
                            });
                        });
                        
                        wrapper.appendChild(paperDiv);
                    });
                    
                    featuredContainer.appendChild(wrapper);
                }
            } catch (error) {
                console.error('Error loading featured papers:', error);
                // Add visible error message in the featured section
                const featuredContainer = document.querySelector('.featured-item__image');
                if (featuredContainer) {
                    featuredContainer.innerHTML = `
                        <div class="featured-error">
                            <p>Error loading featured papers. Make sure Jekyll is running:</p>
                            <code>bundle exec jekyll serve</code>
                            <p style="margin-top: 1rem; font-size: 1.4rem; color: #666;">Error: ${error.message}</p>
                        </div>
                    `;
                }
            }
        }
    };

    // Load featured papers when page loads
    window.addEventListener('load', loadFeaturedPapers);

    /* Mobile Menu
    * -------------------------------------------------- */
    const menuToggle = document.querySelector('.s-header__menu-toggle');
    const nav = document.querySelector('.s-header__nav');
    const closeBtn = document.querySelector('.s-header__nav-close-btn');
    const menuLinks = document.querySelectorAll('.s-header__nav-list a');
    
    // Debug elements
    console.log('Menu elements found:', { 
        menuToggle: menuToggle !== null, 
        nav: nav !== null, 
        closeBtn: closeBtn !== null,
        menuLinksCount: menuLinks ? menuLinks.length : 0
    });

    // Handle click outside
    document.addEventListener('click', function(e) {
        if (nav && nav.classList.contains('is-active')) {
            // Check if click is outside nav and not on menu toggle
            if ((!nav.contains(e.target) && menuToggle && !menuToggle.contains(e.target))) {
                console.log('Click outside detected');
                nav.classList.remove('is-active');
                // Reset the style
                nav.style.right = '-300px';
            }
        }
    });

    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent document click from immediately closing
            console.log('Menu toggle clicked');
            if (nav) {
                console.log('Adding is-active class to nav');
                nav.classList.add('is-active');
                
                // Make sure the style change is applied
                nav.style.right = '0';
            } else {
                console.error('Nav element not found when toggle clicked');
            }
        });
    } else {
        console.error('Menu toggle element not found');
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Close button clicked');
            if (nav) {
                console.log('Removing is-active class from nav');
                nav.classList.remove('is-active');
                // Reset the style
                nav.style.right = '-300px';
            } else {
                console.error('Nav element not found when close clicked');
            }
        });
    } else {
        console.error('Close button element not found');
    }

    if (menuLinks && menuLinks.length > 0) {
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                console.log('Menu link clicked');
                if (nav) {
                    console.log('Removing is-active class from nav');
                    nav.classList.remove('is-active');
                    // Reset the style
                    nav.style.right = '-300px';
                }
            });
        });
    }

    /* Smooth Scrolling
    * -------------------------------------------------- */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            
            // Skip navigation placeholders like #0
            if (href === '#0' || href === '#') {
                return;
            }
            
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    /* Back to Top
    * -------------------------------------------------- */
    const goTop = document.querySelector('.ss-go-top');

    if (goTop) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 800) {
                goTop.classList.add('link-is-visible');
            } else {
                goTop.classList.remove('link-is-visible');
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        const images = document.querySelectorAll('.member-image img[loading="lazy"]');
        
        images.forEach(img => {
            if (img.complete) {
                img.parentElement.classList.add('loaded');
            } else {
                img.addEventListener('load', function() {
                    img.parentElement.classList.add('loaded');
                });
            }
        });

        // Email copy functionality
        const copyButtons = document.querySelectorAll('.copy-btn');
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const textToCopy = this.getAttribute('data-clipboard-text');
                copyToClipboard(textToCopy, this);
            });
        });

        // Add accessible names to all copy buttons on document load
        copyButtons.forEach(button => {
            // Get the email text from data-text or data-clipboard-text attribute
            const emailText = button.getAttribute('data-text') || button.getAttribute('data-clipboard-text');
            // Add aria-label if it doesn't exist
            if (!button.hasAttribute('aria-label') && emailText) {
                button.setAttribute('aria-label', `Copy email address ${emailText}`);
            }
        });
    });

    /* Copy Email Functionality
    * -------------------------------------------------- */
    window.copyEmail = function(button) {
        const text = button.getAttribute('data-text') || button.getAttribute('data-clipboard-text');
        copyToClipboard(text, button);
    };

})(document.documentElement);