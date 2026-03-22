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

  // Reveal the page: overlay scaleY(1) → scaleY(0) then hide
  function revealPage() {
    // Clear all inline styles so CSS class animation takes over
    overlay.removeAttribute('style');
    // Force-restart animation: remove class → reflow → add class
    overlay.classList.remove('page-transition');
    void overlay.offsetWidth;
    overlay.classList.add('page-transition');

    overlay.addEventListener('animationend', function handler() {
      overlay.style.display = 'none';
      overlay.removeEventListener('animationend', handler);
    });
  }

  // --- Initial page load ---
  revealPage();

  // --- Back/forward (bfcache) ---
  window.addEventListener('pageshow', function(e) {
    if (e.persisted) {
      revealPage();
    }
  });

  // --- Outgoing: click a link → overlay covers screen then navigate ---
  document.querySelectorAll('a[href]').forEach(function(link) {
    var href = link.getAttribute('href');
    if (!href.startsWith('#') && !href.startsWith('http') && !href.startsWith('//')) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        var target = link.href;

        // Reset overlay for outgoing transition
        overlay.removeAttribute('style');
        overlay.classList.remove('page-transition');
        overlay.style.display = 'block';
        overlay.style.transform = 'scaleY(0)';
        overlay.style.transformOrigin = 'bottom';

        requestAnimationFrame(function() {
          overlay.style.transition = 'transform 0.6s cubic-bezier(0.77, 0, 0.18, 1)';
          overlay.style.transform = 'scaleY(1)';

          // Navigate after overlay fully covers the screen
          overlay.addEventListener('transitionend', function handler() {
            overlay.removeEventListener('transitionend', handler);
            window.location.href = target;
          });

          // Fallback in case transitionend doesn't fire
          setTimeout(function() { window.location.href = target; }, 700);
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
// Gallery Marquee — Drag/Swipe with Inertia
// ================================
(function() {
  var marquee = document.querySelector('.gallery-marquee');
  var track   = document.querySelector('.gallery-track');
  if (!marquee || !track) return;

  var isDragging = false;
  var startX = 0;
  var startY = 0;
  var currentOffset = 0;
  var dragDistance = 0;
  var halfWidth = 0;
  var rafId = null;
  var pendingX = null;          // pending position for rAF batching
  var directionLocked = false;  // true once we know horiz vs vert
  var isHorizontal = false;     // locked to horizontal drag?

  // Velocity
  var velocitySamples = [];
  var lastX = 0;
  var lastTime = 0;

  function getHalfWidth() {
    halfWidth = track.scrollWidth / 2;
  }

  function getCurrentTranslateX() {
    var matrix = window.getComputedStyle(track).transform;
    if (!matrix || matrix === 'none') return 0;
    var m = matrix.match(/matrix.*\((.+)\)/);
    if (m) return parseFloat(m[1].split(', ')[4]) || 0;
    return 0;
  }

  function normalize(offset) {
    if (halfWidth === 0) return offset;
    offset = offset % halfWidth;
    if (offset > 0) offset -= halfWidth;
    return offset;
  }

  // Switch from CSS animation → manual JS control
  function enterManualMode() {
    currentOffset = getCurrentTranslateX();
    track.classList.remove('is-auto');
    track.style.animation = 'none';
    track.style.transform = 'translateX(' + currentOffset + 'px)';
  }

  // Switch from manual JS control → CSS animation
  function enterAutoMode(offset) {
    var progress = -offset / halfWidth;
    progress = ((progress % 1) + 1) % 1;
    var duration = 40; // must match CSS
    if (window.matchMedia('(max-width: 768px)').matches) duration = 30;

    // Clean up all inline styles, then re-add animation via class
    track.style.animation = '';
    track.style.transform = '';
    track.style.animationDelay = '-' + (progress * duration) + 's';

    // Force reflow so the browser picks up the new delay before adding class
    void track.offsetWidth;
    track.classList.add('is-auto');
  }

  // --- rAF-batched position update ---
  function scheduleUpdate() {
    if (rafId) return;
    rafId = requestAnimationFrame(function() {
      rafId = null;
      if (pendingX === null) return;
      var dx = pendingX - startX;
      dragDistance = dx;
      var pos = normalize(currentOffset + dx);
      track.style.transform = 'translateX(' + pos + 'px)';
    });
  }

  // --- Inertia ---
  function coast(velocity, offset) {
    var friction = 0.95;
    var v = velocity;
    var pos = offset;

    function step() {
      v *= friction;
      pos = normalize(pos + v);
      track.style.transform = 'translateX(' + pos + 'px)';

      if (Math.abs(v) > 0.3) {
        rafId = requestAnimationFrame(step);
      } else {
        rafId = null;
        enterAutoMode(pos);
      }
    }
    rafId = requestAnimationFrame(step);
  }

  // --- Drag ---
  function onStart(x, y) {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    getHalfWidth();
    enterManualMode();
    isDragging = true;
    directionLocked = false;
    isHorizontal = false;
    dragDistance = 0;
    pendingX = null;
    velocitySamples = [];
    startX = x;
    startY = y;
    lastX = x;
    lastTime = performance.now();
    marquee.classList.add('is-dragging');
  }

  function onMove(x, y, e) {
    if (!isDragging) return;

    // Direction lock: decide once whether this is a horizontal or vertical gesture
    if (!directionLocked) {
      var dx = Math.abs(x - startX);
      var dy = Math.abs(y - startY);
      if (dx + dy > 8) {
        directionLocked = true;
        isHorizontal = dx > dy;
        if (!isHorizontal) {
          // Vertical scroll → cancel gallery drag, let page scroll
          isDragging = false;
          marquee.classList.remove('is-dragging');
          enterAutoMode(currentOffset);
          return;
        }
      } else {
        return; // Not enough movement to decide yet
      }
    }

    // Horizontal drag — prevent page scroll
    if (e && e.cancelable) e.preventDefault();

    var now = performance.now();
    var dt = now - lastTime;
    if (dt > 0) {
      velocitySamples.push((x - lastX) / dt);
      if (velocitySamples.length > 5) velocitySamples.shift();
    }
    lastX = x;
    lastTime = now;

    pendingX = x;
    scheduleUpdate();
  }

  function onEnd() {
    if (!isDragging) return;
    isDragging = false;
    marquee.classList.remove('is-dragging');

    var finalOffset = normalize(currentOffset + dragDistance);

    // Smoothed velocity → px/frame
    var v = 0;
    if (velocitySamples.length > 0) {
      var sum = 0;
      for (var i = 0; i < velocitySamples.length; i++) sum += velocitySamples[i];
      v = (sum / velocitySamples.length) * 16.67;
    }

    if (Math.abs(v) > 1.5) {
      coast(v, finalOffset);
    } else {
      enterAutoMode(finalOffset);
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
  }, { passive: false }); // need non-passive to preventDefault on horizontal
  window.addEventListener('touchend', onEnd);
  window.addEventListener('touchcancel', onEnd);

  // Expose for modal
  marquee._isDragClick = function() {
    return Math.abs(dragDistance) > 5;
  };

  // Start in auto mode
  track.classList.add('is-auto');
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
