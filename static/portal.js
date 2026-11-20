'use strict';
const navToggle = document.querySelector('.nav-toggle');
const mainNav = document.querySelector('#main-nav');
const explorationMenu = mainNav?.querySelector('.nav-more');
function setNavigationOpen(open) {
  navToggle.setAttribute('aria-expanded', String(open));
  mainNav.classList.toggle('open', open);
  if (!open && explorationMenu) explorationMenu.open = false;
}
navToggle?.addEventListener('click', () => {
  setNavigationOpen(navToggle.getAttribute('aria-expanded') !== 'true');
});
mainNav?.addEventListener('click', event => {
  if (event.target.closest('a') && navToggle.getAttribute('aria-expanded') === 'true') {
    setNavigationOpen(false);
  }
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  if (explorationMenu?.open) {
    explorationMenu.open = false;
    explorationMenu.querySelector('summary').focus();
  } else if (navToggle?.getAttribute('aria-expanded') === 'true') {
    setNavigationOpen(false);
    navToggle.focus();
  }
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
