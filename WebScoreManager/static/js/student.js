document.addEventListener('DOMContentLoaded', () => {
  const { attachValidation, validateForm, setLoading, apiFetch, showToast } = window.AppUtils || {};

  const loginForm = document.getElementById('studentLoginForm');
  if (loginForm) {
    attachValidation(loginForm);
    loginForm.addEventListener('submit', async event => {
      event.preventDefault();
      if (!validateForm(loginForm)) {
        showToast('请检查学号和密码', 'danger');
        return;
      }
      const submitBtn = loginForm.querySelector('button[type="submit"]');
      setLoading(submitBtn, true);
      const form = new FormData(loginForm);
      const payload = {
        student_id: form.get('student_id'),
        password: form.get('password')
      };
      try {
        const res = await apiFetch('/api/student_login', { method: 'POST', body: payload });
        const data = await res.json();
        if (data.success) {
          showToast('登录成功');
          window.location.href = '/student_portal';
        } else {
          showToast(data.message || '登录失败', 'danger');
        }
      } catch (error) {
        console.error('学生登录失败', error);
        showToast('请求失败，请稍后重试', 'danger');
      } finally {
        setLoading(submitBtn, false);
      }
    });
  }

  if (document.getElementById('myScoresBody')) {
    loadMyScores();
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async () => {
        try {
          await apiFetch('/logout', { method: 'GET' });
        } finally {
          window.location.href = '/';
        }
      });
    }
  }
});

async function loadMyScores() {
  const { apiFetch, showToast } = window.AppUtils || {};
  try {
    const res = await apiFetch('/api/student_scores/me');
    if (res.status === 401) {
      window.location.href = '/student_login';
      return;
    }
    const scores = await res.json();
    const tbody = document.getElementById('myScoresBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    scores.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${s.course_id}</td>
        <td>${s.score}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (error) {
    console.error('加载成绩失败', error);
    showToast('加载成绩失败', 'danger');
  }
}