'use strict';

if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const reveal = new IntersectionObserver((entries, observer) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-revealed');
        observer.unobserve(entry.target);
      }
    }
  }, {threshold: 0.15});

  document.querySelectorAll('.ks-landing [data-landing-reveal]').forEach(section => reveal.observe(section));
}
