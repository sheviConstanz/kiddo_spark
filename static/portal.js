'use strict';
const workspace = document.querySelector('[data-workspace-layout]');
if (workspace) {
  const toggle = workspace.querySelector('[data-workspace-toggle]');
  const links = document.getElementById(toggle.getAttribute('aria-controls'));
  const storageKey = 'kiddo-sidebar-' + workspace.dataset.workspaceLayout;

  function setSidebarCollapsed(collapsed) {
    workspace.classList.toggle('is-sidebar-collapsed', collapsed);
    links.hidden = collapsed;
    toggle.setAttribute('aria-expanded', String(!collapsed));
    toggle.setAttribute('aria-label', collapsed ? 'Desplegar menú lateral' : 'Plegar menú lateral');
  }

  try {
    setSidebarCollapsed(localStorage.getItem(storageKey) === 'collapsed');
  } catch {
    setSidebarCollapsed(false);
  }
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const collapsed = !links.hidden;
    setSidebarCollapsed(collapsed);
    try {
      localStorage.setItem(storageKey, collapsed ? 'collapsed' : 'expanded');
    } catch {
      // The sidebar still works when the browser blocks local storage.
    }
  });
}

const accountMenu = document.querySelector('.account-menu');
if (accountMenu) {
  document.addEventListener('click', event => {
    if (accountMenu.open && !accountMenu.contains(event.target)) accountMenu.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !accountMenu.open) return;
    accountMenu.open = false;
    accountMenu.querySelector('summary').focus();
  });
}

const reportFilters = document.querySelector('[data-report-filters]');
if (reportFilters) {
  reportFilters.elements.center.addEventListener('change', () => {
    reportFilters.elements.activity.value = '';
  });
}

const confirmation = document.querySelector('.ks-confirm-dialog');
if (confirmation && typeof confirmation.showModal === 'function') {
  let pendingAction;
  let approvedForm;
  const title = confirmation.querySelector('#confirm-dialog-title');
  const message = confirmation.querySelector('#confirm-dialog-message');
  const confirmAction = confirmation.querySelector('button[value="confirm"]');

  document.addEventListener('submit', event => {
    const form = event.target;
    if (!form.matches('form[data-confirm]') || form === approvedForm || event.defaultPrevented) return;
    event.preventDefault();
    if (confirmation.open || pendingAction) return;
    pendingAction = { form, submitter: event.submitter, previousFocus: document.activeElement };
    title.textContent = form.dataset.confirmTitle || 'Confirmar acción';
    message.textContent = form.dataset.confirm;
    confirmAction.textContent = form.dataset.confirmLabel || 'Confirmar';
    confirmation.dataset.tone = form.dataset.confirmTone || 'standard';
    confirmation.returnValue = '';
    confirmation.showModal();
  });

  confirmation.addEventListener('close', () => {
    const action = pendingAction;
    pendingAction = undefined;
    if (!action) return;
    if (confirmation.returnValue !== 'confirm') {
      action.previousFocus?.focus();
      return;
    }
    approvedForm = action.form;
    try {
      if (action.submitter) {
        action.form.requestSubmit(action.submitter);
      } else {
        action.form.requestSubmit();
      }
    } finally {
      approvedForm = undefined;
    }
  });
} else {
  document.addEventListener('submit', event => {
    if (event.target.matches('form[data-confirm]') && !window.confirm(event.target.dataset.confirm)) {
      event.preventDefault();
    }
  });
}
document.querySelectorAll('input[data-sparks]').forEach(input => {
  input.addEventListener('change', () => {
    const sum = [...document.querySelectorAll('input[data-sparks]:checked')].reduce((n, item) => n + Number(item.dataset.sparks), 0);
    document.querySelector('#calc-total').textContent = String(sum);
  });
});
