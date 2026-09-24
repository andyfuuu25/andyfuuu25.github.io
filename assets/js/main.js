/* Theme toggle, scroll-spy nav, and reveal-on-scroll. */
(function () {
  'use strict';

  var root = document.documentElement;

  /* ------------------------------------------------------------- theme -- */
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var current = root.getAttribute('data-theme');
      if (!current) {
        // No explicit choice yet, so flip away from whatever the OS is giving us.
        var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        current = prefersDark ? 'dark' : 'light';
      }
      var next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  /* -------------------------------------------------- nav border on scroll */
  var nav = document.getElementById('nav');
  if (nav) {
    var setScrolled = function () {
      nav.setAttribute('data-scrolled', window.scrollY > 8 ? 'true' : 'false');
    };
    setScrolled();
    window.addEventListener('scroll', setScrolled, { passive: true });
  }

  /* ------------------------------------------------------------- year --- */
  var year = document.getElementById('year');
  if (year) { year.textContent = String(new Date().getFullYear()); }

  /* ----------------------------------------------------------- reveal --- */
  var revealables = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(revealables, function (el) { el.classList.add('is-visible'); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

    Array.prototype.forEach.call(revealables, function (el, i) {
      el.style.transitionDelay = Math.min(i % 4, 3) * 60 + 'ms';
      revealObserver.observe(el);
    });
  }

  /* --------------------------------------------------------- scroll spy -- */
  var navLinks = Array.prototype.slice.call(
    document.querySelectorAll('.nav__links a[href^="#"]')
  );
  var sections = navLinks
    .map(function (link) { return document.querySelector(link.getAttribute('href')); })
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    var visible = new Set();

    var spyObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { visible.add(entry.target.id); }
        else { visible.delete(entry.target.id); }
      });

      // Highlight the topmost section currently on screen.
      var activeId = null;
      for (var i = 0; i < sections.length; i++) {
        if (visible.has(sections[i].id)) { activeId = sections[i].id; break; }
      }

      navLinks.forEach(function (link) {
        var isActive = activeId !== null && link.getAttribute('href') === '#' + activeId;
        if (isActive) { link.setAttribute('aria-current', 'true'); }
        else { link.removeAttribute('aria-current'); }
      });
    }, { rootMargin: '-25% 0px -55% 0px', threshold: 0 });

    sections.forEach(function (section) { spyObserver.observe(section); });
  }
})();
