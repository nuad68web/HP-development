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

  document.querySelectorAll('a, button, .activities-content').forEach(el => {
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
// Hero Slick Slider
// ================================
$('.slider').slick({
  fade: true,
  autoplay: true,
  autoplaySpeed: 4000,
  speed: 1400,
  infinite: true,
  slidesToShow: 1,
  slidesToScroll: 1,
  arrows: false,
  dots: true,
  pauseOnFocus: false,
  pauseOnHover: false,
  draggable: true,
  swipe: true,
  cssEase: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
});


// ================================
// Scroll Reveal
// ================================
(function() {
  const targets = document.querySelectorAll(
    '.about-title, .about-text, .activities-title, .activities-text, .activities-box, .section__more, .join-title, .join-card, .sns__title, .sns__list'
  );

  targets.forEach(el => el.classList.add('reveal'));

  document.querySelectorAll('.activities-box .activities-content').forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = (0.1 * i) + 's';
  });

  document.querySelectorAll('.sns__item').forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = (0.1 * i) + 's';
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
})();


// ================================
// Activities Gallery Slider (Splide)
// ================================
document.addEventListener('DOMContentLoaded', function() {
  const activitiesSlider = document.querySelector('.activities-slider');

  if (activitiesSlider) {
    new Splide(activitiesSlider, {
      type: 'loop',
      drag: 'free',
      perPage: 4,
      gap: '20px',
      arrows: false,
      pagination: false,
      breakpoints: {
        769: { perPage: 2, gap: '15px' },
        426: { perPage: 1.5, gap: '10px' },
      },
      autoScroll: {
        speed: 1,
        pauseOnHover: true,
        pauseOnFocus: true,
      },
    }).mount(window.splide.Extensions);

    // Modal
    const modal    = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    let isClosing  = false;

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
      setTimeout(() => {
        modal.style.display = 'none';
        modal.classList.remove('is-closing');
        modalImg.src = '';
        isClosing = false;
      }, 320);
    }

    activitiesSlider.querySelectorAll('.splide__slide img').forEach(img => {
      img.addEventListener('click', () => openModal(img.src, img.alt));
    });

    modal.addEventListener('click', closeModal);
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && modal.style.display === 'block') closeModal();
    });
  }
});


// ================================
// Parallax on hero title
// ================================
$(window).on('scroll', function() {
  const scrollY = $(this).scrollTop();
  if (scrollY < window.innerHeight) {
    $('.hero_overlay').css('transform', 'translateY(' + (scrollY * 0.2) + 'px)');
  }
});


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
    $('html, body').animate({ scrollTop: 0 }, 500, 'swing');
  });
});


// ================================
// Magnetic CTA Button
// ================================
(function() {
  const btn = document.querySelector('.btn-cta');
  if (!btn) return;

  btn.addEventListener('mousemove', function(e) {
    const rect = btn.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px) translateY(-3px)`;
  });

  btn.addEventListener('mouseleave', function() {
    btn.style.transform = '';
  });
})();