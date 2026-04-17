// ================================
// Mobile Nav: close on link tap + sub-menu toggle
// ================================
(function() {
  const toggle = document.getElementById('nav-toggle');
  if (!toggle) return;

  // Close menu when a regular nav link is tapped
  document.querySelectorAll('.site-nav .nav__link:not(.nav__link--parent)').forEach(function(link) {
    link.addEventListener('click', function() { toggle.checked = false; });
  });

  // Close menu when a sub-link is tapped
  document.querySelectorAll('.site-nav .nav__sub-link').forEach(function(link) {
    link.addEventListener('click', function() { toggle.checked = false; });
  });

  // Sub-menu accordion toggle (mobile)
  document.querySelectorAll('.nav__link--parent').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      var parent = btn.closest('.nav__item--has-sub');
      if (!parent) return;
      var isOpen = parent.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  });
})();

// ================================
// Custom Cursor
// ================================
(function() {
  if (window.matchMedia('(max-width: 768px)').matches) return;

  const dot = document.createElement('div');
  dot.className = 'cursor-dot';
  document.body.appendChild(dot);

  document.addEventListener('mousemove', e => {
    dot.style.left = e.clientX + 'px';
    dot.style.top  = e.clientY + 'px';
  });

  document.querySelectorAll('a, button, .activities-content, .gallery-item img').forEach(el => {
    el.addEventListener('mouseenter', () => dot.classList.add('is-hover'));
    el.addEventListener('mouseleave', () => dot.classList.remove('is-hover'));
  });
})();


// ================================
// Page Transition
// ================================
(function() {
  var overlay = document.getElementById('page-transition');
  if (!overlay) return;

  // --- Incoming: hide overlay after CSS reveal animation completes ---
  // Use timeout as most reliable method (animationend can be flaky)
  setTimeout(function() {
    overlay.style.display = 'none';
  }, 900);

  // --- Back/forward button (bfcache restore) ---
  window.addEventListener('pageshow', function(e) {
    if (e.persisted) {
      // Page restored from bfcache — overlay might still have outgoing styles
      // Force re-reveal: reset everything, replay animation, then hide
      overlay.className = '';                 // strip class
      overlay.removeAttribute('style');       // strip inline styles
      void overlay.offsetWidth;               // force reflow
      overlay.className = 'page-transition';  // re-add class → CSS animation restarts
      setTimeout(function() {
        overlay.style.display = 'none';
      }, 900);
    }
  });

  // --- Outgoing: click a link → overlay covers screen, then navigate ---
  document.querySelectorAll('a[href]').forEach(function(link) {
    var href = link.getAttribute('href');
    if (!href.startsWith('#') && !href.startsWith('http') && !href.startsWith('//')) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        var target = link.href;

        // Prepare overlay for outgoing animation
        overlay.className = '';                     // remove page-transition class
        overlay.removeAttribute('style');
        overlay.style.position = 'fixed';
        overlay.style.inset = '0';
        overlay.style.background = '#111';
        overlay.style.zIndex = '9000';
        overlay.style.display = 'block';
        overlay.style.transform = 'scaleY(0)';
        overlay.style.transformOrigin = 'bottom';
        overlay.style.pointerEvents = 'none';

        requestAnimationFrame(function() {
          overlay.style.transition = 'transform 0.6s cubic-bezier(0.77, 0, 0.18, 1)';
          overlay.style.transform = 'scaleY(1)';
          // Navigate after transition
          setTimeout(function() { window.location.href = target; }, 650);
        });
      });
    }
  });
})();


// ================================
// Smooth Scroll for Anchor Links
// ================================
(function() {
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#') return;
      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
})();


// ================================
// Unified Scroll Handler (single rAF)
// ================================
(function() {
  let ticking = false;

  window.addEventListener('scroll', function() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function() {
      const scrollY = window.pageYOffset || document.documentElement.scrollTop;

      // Header scroll state
      const header = document.querySelector('.site-header');
      if (header) {
        if (scrollY > 50) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      }

      // Page top button
      const pageTop = document.querySelector('.pagetop');
      if (pageTop) {
        if (scrollY > 200) {
          pageTop.classList.add('is-show');
        } else {
          pageTop.classList.remove('is-show');
        }
      }

      // Parallax on hero title (PC only)
      if (!window.matchMedia('(max-width: 768px)').matches) {
        const heroOverlay = document.querySelector('.hero_overlay');
        if (heroOverlay && scrollY < window.innerHeight) {
          heroOverlay.style.transform = 'translateY(' + (scrollY * 0.2) + 'px)';
        }
      }

      ticking = false;
    });
  }, { passive: true });

  // Page top click
  var pageTopBtn = document.querySelector('.pagetop');
  if (pageTopBtn) {
    pageTopBtn.addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();


// ================================
// Hero Fade Slider (Pure JS — no library)
// ================================
(function() {
  var slides = document.querySelectorAll('.slider .slider-item');
  var dotsContainer = document.querySelector('.slider-dots');
  if (!slides.length) return;

  var current = 0;
  var total = slides.length;
  var interval = 4000; // autoplay interval (ms)
  var timer = null;

  // Build dot buttons
  for (var i = 0; i < total; i++) {
    var li = document.createElement('li');
    var btn = document.createElement('button');
    btn.setAttribute('aria-label', 'スライド ' + (i + 1));
    if (i === 0) btn.classList.add('is-active');
    btn.dataset.index = i;
    btn.addEventListener('click', function() {
      goTo(parseInt(this.dataset.index, 10));
      resetTimer();
    });
    li.appendChild(btn);
    dotsContainer.appendChild(li);
  }

  var dots = dotsContainer.querySelectorAll('button');

  function goTo(index) {
    // Prepare and activate NEW slide FIRST (cross-fade: both visible briefly)
    slides[index].style.animation = 'none';
    void slides[index].offsetWidth;           // reflow to restart Ken Burns
    slides[index].style.animation = '';
    slides[index].classList.add('is-active');

    // THEN deactivate old slide — guarantees no gap where both are invisible
    slides[current].classList.remove('is-active');

    dots[current].classList.remove('is-active');
    dots[index].classList.add('is-active');

    current = index;
  }

  function next() {
    goTo((current + 1) % total);
  }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(next, interval);
  }

  // Start autoplay
  timer = setInterval(next, interval);
})();


// ================================
// Scroll Reveal
// ================================
(function() {
  // Elements already marked with .reveal in HTML stay as-is
  // Add reveal to remaining targets
  var targets = document.querySelectorAll(
    '.about-title, .about-text, .activities-title, .activities-text, .activities-box, .section__more, .join-title, .join-card, .sns__title, .sns__list'
  );
  targets.forEach(function(el) { el.classList.add('reveal'); });

  document.querySelectorAll('.activities-content').forEach(function(el, i) {
    el.style.transitionDelay = (0.15 * i) + 's';
  });

  document.querySelectorAll('.sns__item').forEach(function(el, i) {
    el.classList.add('reveal');
    el.style.transitionDelay = (0.12 * i) + 's';
  });

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(function(el) { observer.observe(el); });
})();


// ================================
// Gallery Marquee — rAF auto-scroll + Drag/Swipe with Inertia
// ================================
(function() {
  var marquee = document.querySelector('.gallery-marquee');
  var track   = document.querySelector('.gallery-track');
  if (!marquee || !track) return;

  // --- State ---
  var offset = 0;               // current translateX offset (always negative or zero)
  var halfWidth = 0;
  var autoSpeed = -1.2;         // px per frame at 60fps (negative = scroll left)
  var isAutoScrolling = false;
  var isDragging = false;
  var rafId = null;

  // Drag state
  var startX = 0;
  var startY = 0;
  var dragStartOffset = 0;
  var dragDistance = 0;
  var directionLocked = false;
  var isHorizontal = false;

  // Velocity
  var velocitySamples = [];
  var lastDragX = 0;
  var lastDragTime = 0;

  // --- Helpers ---
  function measureHalf() {
    halfWidth = track.scrollWidth / 2;
  }

  function normalize(val) {
    if (halfWidth === 0) return val;
    val = val % halfWidth;
    if (val > 0) val -= halfWidth;
    return val;
  }

  function applyTransform(x) {
    track.style.transform = 'translate3d(' + x + 'px, 0, 0)';
  }

  // --- Auto-scroll loop (rAF, no CSS animation) ---
  var prevTime = 0;

  function autoScrollLoop(timestamp) {
    if (!isAutoScrolling) return;

    if (prevTime === 0) prevTime = timestamp;
    var delta = timestamp - prevTime;
    prevTime = timestamp;

    // Normalize speed to ~60fps (16.67ms per frame)
    // autoSpeed is px per 16.67ms frame
    var move = autoSpeed * (delta / 16.67);
    offset = normalize(offset + move);
    applyTransform(offset);

    rafId = requestAnimationFrame(autoScrollLoop);
  }

  function startAutoScroll() {
    if (isAutoScrolling) return;
    isAutoScrolling = true;
    prevTime = 0;
    rafId = requestAnimationFrame(autoScrollLoop);
  }

  function stopAutoScroll() {
    isAutoScrolling = false;
    prevTime = 0;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
  }

  // --- Inertia coast (after drag release) ---
  function coast(velocity) {
    var friction = 0.95;
    var v = velocity;

    function step() {
      v *= friction;
      offset = normalize(offset + v);
      applyTransform(offset);

      if (Math.abs(v) > 0.3) {
        rafId = requestAnimationFrame(step);
      } else {
        rafId = null;
        startAutoScroll();
      }
    }
    rafId = requestAnimationFrame(step);
  }

  // --- Drag handlers ---
  function onStart(x, y) {
    stopAutoScroll();
    measureHalf();
    isDragging = true;
    directionLocked = false;
    isHorizontal = false;
    dragDistance = 0;
    dragStartOffset = offset;
    velocitySamples = [];
    startX = x;
    startY = y;
    lastDragX = x;
    lastDragTime = performance.now();
    marquee.classList.add('is-dragging');
  }

  function onMove(x, y, e) {
    if (!isDragging) return;

    // Direction lock
    if (!directionLocked) {
      var dx = Math.abs(x - startX);
      var dy = Math.abs(y - startY);
      if (dx + dy > 8) {
        directionLocked = true;
        isHorizontal = dx > dy;
        if (!isHorizontal) {
          isDragging = false;
          marquee.classList.remove('is-dragging');
          startAutoScroll();
          return;
        }
      } else {
        return;
      }
    }

    if (e && e.cancelable) e.preventDefault();

    var now = performance.now();
    var dt = now - lastDragTime;
    if (dt > 0) {
      velocitySamples.push((x - lastDragX) / dt);
      if (velocitySamples.length > 5) velocitySamples.shift();
    }
    lastDragX = x;
    lastDragTime = now;

    dragDistance = x - startX;
    offset = normalize(dragStartOffset + dragDistance);
    applyTransform(offset);
  }

  function onEnd() {
    if (!isDragging) return;
    isDragging = false;
    marquee.classList.remove('is-dragging');

    // Smoothed velocity → px/frame
    var v = 0;
    if (velocitySamples.length > 0) {
      var sum = 0;
      for (var i = 0; i < velocitySamples.length; i++) sum += velocitySamples[i];
      v = (sum / velocitySamples.length) * 16.67;
    }

    if (Math.abs(v) > 1.5) {
      coast(v);
    } else {
      startAutoScroll();
    }
  }

  // --- Mouse ---
  marquee.addEventListener('mousedown', function(e) {
    e.preventDefault();
    onStart(e.clientX, e.clientY);
  });
  window.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    onMove(e.clientX, e.clientY, e);
  });
  window.addEventListener('mouseup', onEnd);

  // --- Touch ---
  marquee.addEventListener('touchstart', function(e) {
    var t = e.touches[0];
    onStart(t.clientX, t.clientY);
  }, { passive: true });
  window.addEventListener('touchmove', function(e) {
    if (!isDragging) return;
    var t = e.touches[0];
    onMove(t.clientX, t.clientY, e);
  }, { passive: false });
  window.addEventListener('touchend', onEnd);
  window.addEventListener('touchcancel', onEnd);

  // --- Pause when not visible (saves battery) ---
  var visObserver = new IntersectionObserver(function(entries) {
    if (entries[0].isIntersecting) {
      if (!isDragging) startAutoScroll();
    } else {
      stopAutoScroll();
    }
  }, { threshold: 0 });
  visObserver.observe(marquee);

  // Expose for modal
  marquee._isDragClick = function() {
    return Math.abs(dragDistance) > 5;
  };

  // --- Init ---
  measureHalf();
  applyTransform(0);
  // Auto-scroll starts when IntersectionObserver fires
})();


// ================================
// Gallery Image Modal (no Splide)
// ================================
(function() {
  var modal    = document.getElementById('image-modal');
  var modalImg = document.getElementById('modal-image');
  if (!modal || !modalImg) return;
  var isClosing = false;

  function openModal(src, alt) {
    if (isClosing) return;
    modalImg.src = src;
    modalImg.alt = alt;
    modal.classList.remove('is-closing');
    modal.style.display = 'block';
  }

  function closeModal() {
    if (isClosing) return;
    isClosing = true;
    modal.classList.add('is-closing');
    setTimeout(function() {
      modal.style.display = 'none';
      modal.classList.remove('is-closing');
      modalImg.src = '';
      isClosing = false;
    }, 320);
  }

  var marqueeEl = document.querySelector('.gallery-marquee');
  document.querySelectorAll('.gallery-item img').forEach(function(img) {
    img.addEventListener('click', function() {
      // Don't open modal if user was dragging
      if (marqueeEl && marqueeEl._isDragClick && marqueeEl._isDragClick()) return;
      openModal(img.src, img.alt);
    });
  });

  modal.addEventListener('click', closeModal);
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.style.display === 'block') closeModal();
  });
})();


// ================================
// Magnetic CTA Button
// ================================
(function() {
  var btn = document.querySelector('.btn-cta');
  if (!btn) return;

  btn.addEventListener('mousemove', function(e) {
    var rect = btn.getBoundingClientRect();
    var x = e.clientX - rect.left - rect.width / 2;
    var y = e.clientY - rect.top - rect.height / 2;
    btn.style.transform = 'translate(' + (x * 0.15) + 'px, ' + (y * 0.15) + 'px) translateY(-3px)';
  });

  btn.addEventListener('mouseleave', function() {
    btn.style.transform = '';
  });
})();
