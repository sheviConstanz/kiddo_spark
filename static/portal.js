'use strict';
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
