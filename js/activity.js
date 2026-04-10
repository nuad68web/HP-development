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

  document.querySelectorAll('a, button').forEach(el => {
    el.addEventListener('mouseenter', () => dot.classList.add('is-hover'));
    el.addEventListener('mouseleave', () => dot.classList.remove('is-hover'));
  });
})();


// ================================
// Page Transition
// ================================
(function() {
  const overlay = document.createElement('div');
  overlay.className = 'page-transition';
  document.body.prepend(overlay);

  setTimeout(() => { overlay.style.display = 'none'; }, 1100);

  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href.startsWith('#') && !href.startsWith('http') && !href.startsWith('//')) {
      link.addEventListener('click', e => {
        e.preventDefault();
        const target = link.href;
        overlay.style.display = 'block';
        overlay.style.animation = 'none';
        overlay.style.transform = 'scaleY(0)';
        overlay.style.transformOrigin = 'bottom';
        requestAnimationFrame(() => {
          overlay.style.transition = 'transform 0.6s cubic-bezier(0.77, 0, 0.18, 1)';
          overlay.style.transform = 'scaleY(1)';
          setTimeout(() => { window.location.href = target; }, 650);
        });
      });
    }
  });
})();


// ================================
// Header scroll state
// ================================
$(window).on('scroll', function() {
  $(this).scrollTop() > 50
    ? $('.site-header').addClass('scrolled')
    : $('.site-header').removeClass('scrolled');
});


// ================================
// Timeline scroll animation
// ================================
function ScrollTimelineAnime() {
  $('.timeline li').each(function() {
    var elemPos    = $(this).offset().top;
    var scroll     = $(window).scrollTop();
    var winH       = $(window).height();
    var startPoint = 200;

    if (scroll >= elemPos - winH - startPoint) {
      var H = $(this).outerHeight(true);
      var percent = (scroll + startPoint - elemPos) / (H / 2) * 100;
      if (percent > 100) percent = 100;
      $(this).children('.border-line').css({ height: percent + '%' });
    }
  });
}

$(window).on('scroll', ScrollTimelineAnime);
$(window).on('load', ScrollTimelineAnime);


// ================================
// Scroll Reveal
// ================================
(function() {
  const targets = document.querySelectorAll(
    '.creation-title, .creation-text, .row, .two-competition, .event-title, .timeline li, .competition'
  );

  targets.forEach(el => {
    el.classList.add('reveal');
    if (el.closest('.timeline')) {
      el.style.transitionDelay = '0s';
    }
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
})();


// ================================
// Page Top Button
// ================================
$(function() {
  const $pageTop = $('.pagetop');

  $(window).on('scroll', function() {
    $(this).scrollTop() > 200
      ? $pageTop.addClass('is-show')
      : $pageTop.removeClass('is-show');
  });

  $pageTop.on('click', function(e) {
    e.preventDefault();
    $('html, body').animate({ scrollTop: 0 }, 500);
  });
});