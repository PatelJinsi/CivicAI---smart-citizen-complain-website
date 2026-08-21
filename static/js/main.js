/* ─────────────────────────────────────────────
   CivicAI — Main JavaScript
   ───────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {

  /* ── AUTO-DISMISS ALERTS ──────────────────── */
  document.querySelectorAll('.civic-alert').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  /* ── COMPLAINT FORM: Live character count ─── */
  const descField = document.querySelector('textarea[name="description"]');
  if (descField) {
    const counter = document.createElement('div');
    counter.className = 'form-text text-end';
    counter.style.marginTop = '4px';
    descField.parentNode.appendChild(counter);

    function updateCount() {
      const len = descField.value.length;
      counter.textContent = len + ' characters';
      counter.style.color = len < 30 ? '#ef4444' : '#94a3b8';
    }
    descField.addEventListener('input', updateCount);
    updateCount();
  }

  /* ── ADMIN DASHBOARD: confirm status change ── */
  document.querySelectorAll('.status-select').forEach(function (sel) {
    sel.dataset.original = sel.value;
    sel.addEventListener('change', function () {
      const id = this.dataset.id;
      const newStatus = this.value;
      const csrfToken = getCookie('csrftoken');

      // Visual feedback: show spinner
      const row = this.closest('tr');
      if (row) row.style.opacity = '0.6';

      fetch('/complaint/' + id + '/status/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
        },
        body: 'status=' + encodeURIComponent(newStatus),
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (row) row.style.opacity = '1';
          if (data.success) {
            sel.style.borderColor = '#10b981';
            showToast('Status updated to: ' + data.status, 'success');
            setTimeout(function () { sel.style.borderColor = ''; }, 2500);
          } else {
            sel.value = sel.dataset.original;
            showToast('Failed to update status.', 'danger');
          }
        })
        .catch(function () {
          if (row) row.style.opacity = '1';
          sel.value = sel.dataset.original;
          showToast('Network error. Please try again.', 'danger');
        });
    });
  });

  /* ── URGENCY PROGRESS BAR ANIMATION ─────── */
  document.querySelectorAll('.progress-bar').forEach(function (bar) {
    const target = bar.style.width;
    bar.style.width = '0%';
    setTimeout(function () {
      bar.style.transition = 'width 1s ease';
      bar.style.width = target;
    }, 300);
  });

  /* ── IMAGE PREVIEW ON FILE SELECT ────────── */
  const imageInput = document.querySelector('input[name="image"]');
  if (imageInput) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;
      const existing = document.getElementById('image-preview');
      if (existing) existing.remove();

      const reader = new FileReader();
      reader.onload = function (e) {
        const preview = document.createElement('div');
        preview.id = 'image-preview';
        preview.style.cssText = 'margin-top:10px;';
        preview.innerHTML = '<img src="' + e.target.result + '" style="max-height:180px;border-radius:8px;border:1px solid #e2e8f0;" alt="Preview">';
        imageInput.parentNode.appendChild(preview);
      };
      reader.readAsDataURL(file);
    });
  }

  /* ── SUBMIT BUTTON LOADING STATE ─────────── */
  const complaintForm = document.getElementById('complaintForm');
  if (complaintForm) {
    complaintForm.addEventListener('submit', function (e) {
      const title = complaintForm.querySelector('[name="title"]');
      const desc = complaintForm.querySelector('[name="description"]');
      const loc = complaintForm.querySelector('[name="location"]');

      if (!title.value.trim() || !desc.value.trim() || !loc.value.trim()) {
        e.preventDefault();
        showToast('Please fill in all required fields.', 'warning');
        return;
      }

      const btn = document.getElementById('submitBtn');
      if (btn) {
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>AI Analyzing…';
        btn.disabled = true;
      }
    });
  }

  /* ── DASHBOARD SEARCH: submit on clear ────── */
  const searchInput = document.querySelector('input[name="search"]');
  if (searchInput) {
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        this.value = '';
        this.closest('form').submit();
      }
    });
  }

  /* ── TOOLTIP INIT ─────────────────────────── */
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  /* ── SMOOTH SCROLL ────────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

});

/* ── HELPERS ────────────────────────────────── */

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(function (cookie) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(trimmed.slice(name.length + 1));
      }
    });
  }
  return cookieValue;
}

function showToast(message, type) {
  type = type || 'info';
  const colorMap = {
    success: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6',
  };
  const toast = document.createElement('div');
  toast.style.cssText = [
    'position:fixed', 'bottom:24px', 'right:24px', 'z-index:9999',
    'background:' + (colorMap[type] || colorMap.info),
    'color:#fff', 'padding:0.7rem 1.4rem',
    'border-radius:10px', 'font-size:0.9rem',
    'font-family:DM Sans,sans-serif', 'font-weight:500',
    'box-shadow:0 4px 20px rgba(0,0,0,0.15)',
    'transition:opacity 0.4s ease',
  ].join(';');
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(function () {
    toast.style.opacity = '0';
    setTimeout(function () { toast.remove(); }, 400);
  }, 3000);
}