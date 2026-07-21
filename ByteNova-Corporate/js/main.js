/* ============================================
   ByteNova Technologies — Main JavaScript
   Premium Interactions | Animations | UX
   ============================================ */

(function() {
  'use strict';

  // ── DOM Ready ──
  document.addEventListener('DOMContentLoaded', function() {

    // ── Loading Screen ──
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
      window.addEventListener('load', function() {
        setTimeout(function() {
          loadingOverlay.classList.add('hidden');
          setTimeout(function() {
            loadingOverlay.style.display = 'none';
          }, 500);
        }, 400);
      });
      // Fallback: hide after 2s if load event already fired
      setTimeout(function() {
        if (!loadingOverlay.classList.contains('hidden')) {
          loadingOverlay.classList.add('hidden');
          setTimeout(function() {
            loadingOverlay.style.display = 'none';
          }, 500);
        }
      }, 2500);
    }

    // ── Scroll Progress Bar ──
    const progressBar = document.getElementById('scrollProgress');
    if (progressBar) {
      window.addEventListener('scroll', function() {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
        progressBar.style.width = progress + '%';
      });
    }

    // ── Sticky Navbar ──
    const navbar = document.getElementById('siteNavbar');
    if (navbar) {
      window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
          navbar.classList.add('scrolled');
        } else {
          navbar.classList.remove('scrolled');
        }
      });
    }

    // ── Mobile Menu Toggle ──
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (navToggle && navLinks) {
      navToggle.addEventListener('click', function() {
        navToggle.classList.toggle('active');
        navLinks.classList.toggle('open');
      });

      // Close menu on link click
      navLinks.querySelectorAll('a').forEach(function(link) {
        link.addEventListener('click', function() {
          navToggle.classList.remove('active');
          navLinks.classList.remove('open');
        });
      });

      // Close menu on outside click
      document.addEventListener('click', function(e) {
        if (!navbar.contains(e.target)) {
          navToggle.classList.remove('active');
          navLinks.classList.remove('open');
        }
      });
    }

    // ── Back to Top ──
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
      window.addEventListener('scroll', function() {
        if (window.scrollY > 400) {
          backToTop.classList.add('visible');
        } else {
          backToTop.classList.remove('visible');
        }
      });
      backToTop.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // ── Dark Mode Toggle ──
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
      // Check saved preference
      const savedTheme = localStorage.getItem('bn-theme');
      if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
      }

      themeToggle.addEventListener('click', function() {
        const current = document.documentElement.getAttribute('data-theme');
        if (current === 'dark') {
          document.documentElement.removeAttribute('data-theme');
          localStorage.setItem('bn-theme', 'light');
          themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
          document.documentElement.setAttribute('data-theme', 'dark');
          localStorage.setItem('bn-theme', 'dark');
          themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
      });
    }

    // ── Animated Counters ──
    function animateCounters() {
      const counters = document.querySelectorAll('.stat-number');
      if (!counters.length) return;

      const animate = function(element) {
        const target = parseInt(element.getAttribute('data-count'), 10) || 0;
        const duration = 1200;
        const startTime = performance.now();

        function update(now) {
          const elapsed = now - startTime;
          const progress = Math.min(elapsed / duration, 1);
          // Ease-out cubic
          const eased = 1 - Math.pow(1 - progress, 3);
          const current = Math.round(target * eased);
          element.textContent = current;
          if (progress < 1) {
            requestAnimationFrame(update);
          } else {
            element.textContent = target;
          }
        }
        requestAnimationFrame(update);
      };

      // Use intersection observer
      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
          entries.forEach(function(entry) {
            if (entry.isIntersecting) {
              const target = entry.target;
              animate(target);
              observer.unobserve(target);
            }
          });
        }, { threshold: 0.3 });

        counters.forEach(function(counter) {
          observer.observe(counter);
        });
      } else {
        // Fallback
        counters.forEach(animate);
      }
    }
    animateCounters();

    // ── Testimonials Carousel ──
    const testimonials = document.querySelectorAll('.testimonial-card');
    const prevBtn = document.getElementById('testPrev');
    const nextBtn = document.getElementById('testNext');
    const dots = document.querySelectorAll('.testimonial-dot');
    let currentTestimonial = 0;

    function showTestimonial(index) {
      testimonials.forEach(function(t, i) {
        t.classList.toggle('active', i === index);
      });
      dots.forEach(function(d, i) {
        d.classList.toggle('active', i === index);
      });
      currentTestimonial = index;
    }

    if (testimonials.length && prevBtn && nextBtn) {
      showTestimonial(0);

      prevBtn.addEventListener('click', function() {
        const idx = (currentTestimonial - 1 + testimonials.length) % testimonials.length;
        showTestimonial(idx);
      });
      nextBtn.addEventListener('click', function() {
        const idx = (currentTestimonial + 1) % testimonials.length;
        showTestimonial(idx);
      });

      dots.forEach(function(dot) {
        dot.addEventListener('click', function() {
          showTestimonial(parseInt(this.getAttribute('data-index'), 10));
        });
      });

      // Auto-rotate
      setInterval(function() {
        const idx = (currentTestimonial + 1) % testimonials.length;
        showTestimonial(idx);
      }, 5000);
    }

    // ── Portfolio Filters ──
    const filterBtns = document.querySelectorAll('.filter-btn');
    const filterItems = document.querySelectorAll('.filter-item');
    if (filterBtns.length && filterItems.length) {
      filterBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
          filterBtns.forEach(function(b) { b.classList.remove('active'); });
          this.classList.add('active');

          const filter = this.getAttribute('data-filter');
          filterItems.forEach(function(item) {
            if (filter === 'all' || item.getAttribute('data-category') === filter) {
              item.style.display = 'block';
              setTimeout(function() {
                item.style.opacity = '1';
                item.style.transform = 'scale(1)';
              }, 50);
            } else {
              item.style.opacity = '0';
              item.style.transform = 'scale(0.8)';
              setTimeout(function() {
                item.style.display = 'none';
              }, 300);
            }
          });
        });
      });
    }

    // ── FAQ Accordion ──
    const faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length) {
      faqItems.forEach(function(item) {
        const question = item.querySelector('.faq-question');
        if (question) {
          question.addEventListener('click', function() {
            const isOpen = item.classList.contains('open');
            // Close all
            faqItems.forEach(function(i) { i.classList.remove('open'); });
            // Toggle current
            if (!isOpen) {
              item.classList.add('open');
            }
          });
        }
      });
    }

    // ── Contact Form ──
    const contactForm = document.getElementById('contactForm');
    const contactStatus = document.getElementById('contactStatus');
    if (contactForm) {
      contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const name = document.getElementById('cf_name')?.value?.trim();
        const email = document.getElementById('cf_email')?.value?.trim();
        const phone = document.getElementById('cf_phone')?.value?.trim();
        const subject = document.getElementById('cf_subject')?.value?.trim();
        const message = document.getElementById('cf_message')?.value?.trim();

        if (!name || !email || !subject || !message) {
          if (contactStatus) {
            contactStatus.textContent = 'Please fill all required fields.';
            contactStatus.style.color = '#ef4444';
          }
          return;
        }

        // Email validation
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          if (contactStatus) {
            contactStatus.textContent = 'Please enter a valid email address.';
            contactStatus.style.color = '#ef4444';
          }
          return;
        }

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        }

        // Simulate sending (in production, POST to your server)
        setTimeout(function() {
          if (contactStatus) {
            contactStatus.textContent = 'Thank you! Your message has been received. We will get back to you within 1-2 business days.';
            contactStatus.style.color = '#10b981';
          }
          contactForm.reset();
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
          }
        }, 1200);
      });
    }

    // ── Newsletter ──
    const newsForm = document.getElementById('newsletterForm');
    const newsStatus = document.getElementById('newsStatus');
    if (newsForm) {
      newsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = this.querySelector('input')?.value?.trim();
        if (!email) {
          if (newsStatus) {
            newsStatus.textContent = 'Please enter your email.';
            newsStatus.style.color = '#ef4444';
          }
          return;
        }
        if (newsStatus) {
          newsStatus.textContent = 'Subscribing...';
          newsStatus.style.color = '#6b7280';
        }
        setTimeout(function() {
          if (newsStatus) {
            newsStatus.textContent = 'Subscribed successfully! Check your inbox for updates.';
            newsStatus.style.color = '#10b981';
          }
          newsForm.reset();
        }, 800);
      });
    }

    // ── Cookie Consent ──
    const cookieConsent = document.getElementById('cookieConsent');
    const cookieBtn = document.getElementById('cookieAccept');
    if (cookieConsent && cookieBtn) {
      if (!localStorage.getItem('bn-cookie')) {
        setTimeout(function() {
          cookieConsent.classList.add('show');
        }, 1500);
      }
      cookieBtn.addEventListener('click', function() {
        localStorage.setItem('bn-cookie', 'accepted');
        cookieConsent.classList.remove('show');
      });
    }

    // ── Smooth Scroll for Anchor Links ──
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
      anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });

    // ── Active Nav Link ──
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(function(link) {
      const href = link.getAttribute('href');
      if (href === currentPath || (currentPath === '' && href === 'index.html')) {
        link.classList.add('active');
      }
    });

    // ── Scroll Reveal Animations ──
    if ('IntersectionObserver' in window) {
      const revealElements = document.querySelectorAll('[data-aos]');
      const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('aos-animate');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

      revealElements.forEach(function(el) {
        observer.observe(el);
      });
    }

    // ── Particles Background (Hero) ──
    const heroParticles = document.getElementById('heroParticles');
    if (heroParticles) {
      for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.width = particle.style.height = (Math.random() * 4 + 2) + 'px';
        particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
        particle.style.animationDelay = (Math.random() * 10) + 's';
        heroParticles.appendChild(particle);
      }
    }

  }); // DOMContentLoaded end

})();
