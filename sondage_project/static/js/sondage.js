/* SondageApp — JavaScript global */

// ── Auto-dismiss alerts ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
});

// ── Copier le lien de partage ──────────────────────────────────────────────
function copierLien(url) {
  navigator.clipboard.writeText(url).then(() => {
    const btn = document.getElementById('btn-copier');
    if (btn) {
      btn.textContent = '✅ Copié !';
      setTimeout(() => { btn.textContent = '📋 Copier le lien'; }, 2000);
    }
  });
}

// ── Confirmation avant suppression ────────────────────────────────────────
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});
