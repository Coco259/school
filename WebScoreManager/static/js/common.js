(function () {
  const AppUtils = {};
  let csrfToken = null;

  const validators = {
    required(value) {
      return value !== null && value !== undefined && String(value).trim() !== '';
    },
    integer(value) {
      if (value === '' || value === null || value === undefined) return true;
      return /^-?\d+$/.test(String(value).trim());
    },
    positiveInteger(value) {
      if (!validators.integer(value)) return false;
      return parseInt(value, 10) > 0;
    },
    age(value) {
      if (!validators.integer(value)) return false;
      const num = parseInt(value, 10);
      return num >= 1 && num <= 100;
    },
    score(value) {
      if (value === '' || value === null || value === undefined) return true;
      const num = Number(value);
      return !Number.isNaN(num) && num >= 0 && num <= 100;
    }
  };

  const errorMessages = {
    required: '该字段不能为空',
    integer: '请输入整数',
    positiveInteger: '请输入正整数',
    age: '年龄需为 1-100 的整数',
    score: '成绩需为 0-100 的数字'
  };

  function toLabel(input) {
    return input.dataset.label || input.placeholder || input.name || '该字段';
  }

  function ensureFeedbackElement(input) {
    let feedback = input.nextElementSibling;
    if (!feedback || !feedback.classList || !feedback.classList.contains('invalid-feedback')) {
      feedback = document.createElement('div');
      feedback.className = 'invalid-feedback';
      input.insertAdjacentElement('afterend', feedback);
    }
    return feedback;
  }

  function validateField(input, showMessage = true) {
    const rules = (input.dataset.rules || '').split('|').map(rule => rule.trim()).filter(Boolean);
    if (rules.length === 0) return true;
    const value = input.value;
    for (const rule of rules) {
      const validator = validators[rule];
      if (!validator) continue;
      if (!validator(value)) {
        if (showMessage) {
          const feedback = ensureFeedbackElement(input);
          feedback.textContent = `${toLabel(input)}：${errorMessages[rule] || '格式不正确'}`;
          input.classList.add('is-invalid');
        }
        return false;
      }
    }
    if (showMessage) {
      input.classList.remove('is-invalid');
    }
    return true;
  }

  function validateForm(form) {
    let ok = true;
    const inputs = form.querySelectorAll('[data-rules]');
    inputs.forEach(input => {
      if (!validateField(input, true)) {
        ok = false;
      }
    });
    return ok;
  }

  function attachValidation(form) {
    const inputs = form.querySelectorAll('[data-rules]');
    inputs.forEach(input => {
      input.addEventListener('input', () => validateField(input, false));
      input.addEventListener('blur', () => validateField(input, true));
    });
  }

  async function fetchCsrfToken() {
    if (csrfToken) return csrfToken;
    try {
      const res = await fetch('/api/csrf-token', { credentials: 'same-origin' });
      if (!res.ok) throw new Error('获取 CSRF 令牌失败');
      const data = await res.json();
      csrfToken = data.csrf_token;
      return csrfToken;
    } catch (err) {
      console.error('CSRF 初始化失败', err);
      throw err;
    }
  }

  async function apiFetch(url, options = {}) {
    const opts = { credentials: 'same-origin', ...options };
    const method = (opts.method || 'GET').toUpperCase();
    opts.headers = { ...(opts.headers || {}) };

    if (opts.body && !(opts.body instanceof FormData)) {
      if (typeof opts.body === 'object') {
        opts.headers['Content-Type'] = opts.headers['Content-Type'] || 'application/json';
        if (opts.headers['Content-Type'].includes('application/json')) {
          opts.body = JSON.stringify(opts.body);
        }
      }
    }

    if (method !== 'GET' && method !== 'HEAD') {
      const token = await fetchCsrfToken();
      opts.headers['X-CSRFToken'] = token;
    }

    const response = await fetch(url, opts);
    return response;
  }

  function getToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container position-fixed top-0 end-0 p-3';
      container.style.zIndex = '1080';
      document.body.appendChild(container);
    }
    return container;
  }

  function showToast(message, variant = 'success', delay = 2500) {
    if (typeof bootstrap === 'undefined' || !bootstrap.Toast) {
      alert(message);
      return;
    }
    const container = getToastContainer();
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-bg-${variant} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>`;
    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => {
      toastEl.remove();
    });
  }

  function setLoading(button, loading) {
    if (!button) return;
    if (loading) {
      if (!button.dataset.originalHtml) {
        button.dataset.originalHtml = button.innerHTML;
      }
      button.disabled = true;
      const spinner = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>';
      const text = button.dataset.loadingText || button.textContent.trim() || '提交中';
      button.innerHTML = `${spinner}${text}`;
    } else {
      button.disabled = false;
      if (button.dataset.originalHtml) {
        button.innerHTML = button.dataset.originalHtml;
      }
    }
  }

  AppUtils.ensureCsrfToken = fetchCsrfToken;
  AppUtils.apiFetch = apiFetch;
  AppUtils.showToast = showToast;
  AppUtils.setLoading = setLoading;
  AppUtils.attachValidation = attachValidation;
  AppUtils.validateForm = validateForm;
  AppUtils.validateField = input => validateField(input, true);

  window.AppUtils = AppUtils;
})();
