'use strict';
const navToggle = document.querySelector('.nav-toggle');
navToggle?.addEventListener('click', () => {
  const open = navToggle.getAttribute('aria-expanded') !== 'true';
  navToggle.setAttribute('aria-expanded', String(open));
  document.querySelector('#main-nav').classList.toggle('open', open);
});
document.querySelectorAll('form[data-confirm]').forEach(form => {
  form.addEventListener('submit', event => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});
document.querySelectorAll('input[data-sparks]').forEach(input => {
  input.addEventListener('change', () => {
    const sum = [...document.querySelectorAll('input[data-sparks]:checked')].reduce((n, item) => n + Number(item.dataset.sparks), 0);
    document.querySelector('#calc-total').textContent = String(sum);
  });
});
