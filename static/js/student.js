document.addEventListener('DOMContentLoaded', function() {
  // 学生登录表单
  const loginForm = document.getElementById('studentLoginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const form = new FormData(loginForm);
      const data = {
        student_id: form.get('student_id'),
        password: form.get('password')
      };
      try {
        const res = await fetch('/api/student_login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
          window.location.href = '/student_portal';
        } else {
          alert(result.message || '登录失败');
        }
      } catch (err) {
        console.error(err);
        alert('请求失败');
      }
    });
  }

  // 学生门户页面加载成绩
  if (document.getElementById('myScoresBody')) {
    loadMyScores();

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async function() {
        await fetch('/logout');
        window.location.href = '/';
      });
    }
  }
});

async function loadMyScores() {
  try {
    const res = await fetch('/api/student_scores/me');
    if (res.status === 401) {
      window.location.href = '/student_login';
      return;
    }
    const scores = await res.json();
    const tbody = document.getElementById('myScoresBody');
    tbody.innerHTML = '';
    scores.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${s.course_id}</td>
        <td>${s.score}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('加载成绩失败', err);
  }
}