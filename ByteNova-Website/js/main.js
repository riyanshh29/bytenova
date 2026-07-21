// ByteNova Company Website (standalone)

(function () {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  // Loading overlay
  window.addEventListener('load', () => {
    const overlay = $('#loadingOverlay');
    if (!overlay) return;
    setTimeout(() => {
      overlay.style.opacity = '0';
      overlay.style.transition = 'opacity .35s ease';
      setTimeout(() => {
        overlay.remove();
      }, 350);
    }, 250);
  });

  // Scroll progress
  const progress = $('#scrollProgress');
  const onScroll = () => {
    if (!progress) return;
    const doc = document.documentElement;
    const scrollTop = doc.scrollTop || document.body.scrollTop;
    const max = doc.scrollHeight - doc.clientHeight;
    const pct = max > 0 ? Math.min(100, Math.max(0, (scrollTop / max) * 100)) : 0;
    progress.style.width = pct + '%';
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Back to top
  const backBtn = $('#backToTop');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Floating contact
  const floating = $('#floatingContact');
  if (floating) {
    floating.addEventListener('click', () => {
      const contact = document.querySelector('#contact, #faq');
      if (contact) contact.scrollIntoView({ behavior: 'smooth', block: 'start' });
      else window.location.href = 'contact.html';
    });
  }

  // Stats counter
  const startCounter = () => {
    const counters = $$('.stat-number[data-count]');
    if (!counters.length) return;

    const animate = (el) => {
      const target = Number(el.getAttribute('data-count') || '0');
      const duration = 900;
      const start = performance.now();

      const step = (now) => {
        const t = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        const val = Math.round(target * eased);
        el.textContent = val;
        if (t < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    // only run once per page load
    let ran = false;
    const runOnce = () => {
      if (ran) return;
      ran = true;
      counters.forEach(animate);
    };

    // Use intersection observer if available
    if ('IntersectionObserver' in window) {
      const el = $('#stats') || counters[0];
      if (el) {
        const obs = new IntersectionObserver((entries) => {
          for (const e of entries) {
            if (e.isIntersecting) {
              runOnce();
              obs.disconnect();
              break;
            }
          }
        }, { threshold: 0.2 });
        obs.observe(el);
        return;
      }
    }

    runOnce();
  };

  startCounter();

  // Typing effect (hero)
  const typingRoot = document.querySelector('.typing');
  if (typingRoot) {
    const phrases = [
      'Python Development',
      'AI Automation',
      'Web Applications',
      'REST APIs & Dashboards'
    ];
    const el = typingRoot;
    let idx = 0;
    let char = 0;
    let deleting = false;

    const type = () => {
      const current = phrases[idx % phrases.length];
      if (!deleting) {
        char++;
        el.textContent = current.slice(0, char);
        if (char >= current.length) {
          deleting = true;
          setTimeout(type, 900);
          return;
        }
      } else {
        char--;
        el.textContent = current.slice(0, char);
        if (char <= 0) {
          deleting = false;
          idx++;
          setTimeout(type, 250);
          return;
        }
      }
      setTimeout(type, deleting ? 35 : 55);
    };
    type();
  }

  // AOS init (safe if library missing)
  if (window.AOS && typeof window.AOS.init === 'function') {
    try { window.AOS.init({ duration: 800, once: true, offset: 60 }); } catch (e) {}
  }

  // Contact form (client-side validation + fake submit)
  const form = $('#contactForm');
  const status = $('#contactStatus');
  const sendBtn = $('#sendMessageBtn');

  const setStatus = (msg, kind) => {
    if (!status) return;
    status.textContent = msg;
    status.className = 'small';
    status.style.color = kind === 'ok' ? '#16a34a' : kind === 'err' ? '#dc2626' : '#64748b';
  };

  if (form && sendBtn) {
    sendBtn.addEventListener('click', () => {
      const fd = new FormData(form);
      const name = (fd.get('name') || '').toString().trim();
      const email = (fd.get('email') || '').toString().trim();
      const phone = (fd.get('phone') || '').toString().trim();
      const msg = (fd.get('message') || '').toString().trim();
      const title = (fd.get('messageTitle') || '').toString().trim();

      if (!name || !email || !phone || !title || !msg) {
        setStatus('Please fill all fields.', 'err');
        return;
      }

      // basic email
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setStatus('Please enter a valid email address.', 'err');
        return;
      }

      setStatus('Sending message…', 'info');
      sendBtn.disabled = true;
      sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Sending…';

      // simulate request
      setTimeout(() => {
        setStatus('Message received. We will reach out shortly.', 'ok');
        form.reset();
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="bi bi-send-fill me-2"></i> Send Message';
      }, 900);
    });
  }

  // Newsletter subscription (client-side)
  const newsBtn = $('#newsBtn');
  const newsEmail = $('#newsEmail');
  const newsStatus = $('#newsStatus');

  if (newsBtn && newsEmail && newsStatus) {
    newsBtn.addEventListener('click', () => {
      const email = (newsEmail.value || '').trim();
      if (!email) {
        newsStatus.textContent = 'Please enter an email.';
        newsStatus.style.color = '#dc2626';
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        newsStatus.textContent = 'Enter a valid email address.';
        newsStatus.style.color = '#dc2626';
        return;
      }
      newsStatus.textContent = 'Subscribing…';
      newsStatus.style.color = '#64748b';
      newsBtn.disabled = true;
      setTimeout(() => {
        newsStatus.textContent = 'Subscribed successfully!';
        newsStatus.style.color = '#16a34a';
        newsBtn.disabled = false;
      }, 750);
    });
  }
})();

