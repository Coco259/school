document.addEventListener('DOMContentLoaded', () => {
  const pageRoot = document.getElementById('scorePage');
  if (!pageRoot) return;
  const { attachValidation, validateForm, setLoading, apiFetch, showToast } = window.AppUtils || {};
  const addScoreForm = document.getElementById('addScoreForm');
  attachValidation(addScoreForm);
  loadScores();

  addScoreForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (!validateForm(addScoreForm)) {
      showToast('请检查成绩信息', 'danger');
      return;
    }
    const submitBtn = addScoreForm.querySelector('button[type="submit"]');
    setLoading(submitBtn, true);
    const form = new FormData(addScoreForm);
    const payload = {
      student_id: Number(form.get('student_id')),
      course_id: Number(form.get('course_id')),
      score: Number(form.get('score'))
    };
    try {
      const res = await apiFetch('/api/scores', { method: 'POST', body: payload });
      const data = await res.json();
      if (data.success) {
        showToast('成绩添加成功');
        addScoreForm.reset();
        loadScores();
      } else {
        showToast(data.message || '添加失败', 'danger');
      }
    } catch (error) {
      console.error('添加成绩失败', error);
      showToast('添加成绩失败', 'danger');
    } finally {
      setLoading(submitBtn, false);
    }
  });
});

async function loadScores() {
  const { apiFetch, showToast } = window.AppUtils || {};
  try {
    const res = await apiFetch('/api/scores');
    const scores = await res.json();
    const tbody = document.getElementById('scoreTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    scores.forEach(s => {
      const id = s.score_id || s.id || '';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${id}</td>
        <td>${s.student_id}</td>
        <td>${s.course_id}</td>
        <td>${s.score}</td>
        <td>
          <button class="btn btn-sm btn-primary me-2" data-action="edit" data-id="${id}" data-student="${s.student_id}" data-course="${s.course_id}" data-score="${s.score}">编辑</button>
          <button class="btn btn-sm btn-danger" data-action="delete" data-id="${id}">删除</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
    tbody.querySelectorAll('button[data-action="edit"]').forEach(btn => {
      btn.addEventListener('click', () => editScore(btn.dataset.id, btn.dataset.student, btn.dataset.course, btn.dataset.score));
    });
    tbody.querySelectorAll('button[data-action="delete"]').forEach(btn => {
      btn.addEventListener('click', () => deleteScore(btn.dataset.id));
    });
  } catch (error) {
    console.error('加载成绩失败', error);
    showToast('加载成绩失败', 'danger');
  }
}

function editScore(id, studentId, courseId, score) {
  document.getElementById('editScoreId').value = id;
  document.getElementById('editStudentId').value = studentId;
  document.getElementById('editCourseId').value = courseId;
  document.getElementById('editScore').value = score;
  const form = document.getElementById('editScoreForm');
  if (window.AppUtils && window.AppUtils.attachValidation) {
    window.AppUtils.attachValidation(form);
  }
  const modal = new bootstrap.Modal(document.getElementById('editScoreModal'));
  modal.show();
}

async function saveEditScore() {
  const { apiFetch, showToast, validateForm, setLoading, attachValidation } = window.AppUtils || {};
  const form = document.getElementById('editScoreForm');
  attachValidation(form);
  if (!validateForm(form)) {
    showToast('请检查成绩信息', 'danger');
    return;
  }
  const id = document.getElementById('editScoreId').value;
  const submitBtn = document.querySelector('#editScoreModal .btn-primary');
  setLoading(submitBtn, true);
  const payload = {
    student_id: Number(document.getElementById('editStudentId').value),
    course_id: Number(document.getElementById('editCourseId').value),
    score: Number(document.getElementById('editScore').value)
  };
  try {
    const res = await apiFetch(`/api/scores/${id}`, { method: 'PUT', body: payload });
    const data = await res.json();
    if (data.success) {
      showToast('成绩已更新');
      const modal = bootstrap.Modal.getInstance(document.getElementById('editScoreModal'));
      modal.hide();
      loadScores();
    } else {
      showToast(data.message || '更新失败', 'danger');
    }
  } catch (error) {
    console.error('保存成绩失败', error);
    showToast('保存失败', 'danger');
  } finally {
    setLoading(submitBtn, false);
  }
}

async function deleteScore(id) {
  const { apiFetch, showToast } = window.AppUtils || {};
  if (!confirm('确认删除该成绩吗？')) return;
  try {
    const res = await apiFetch(`/api/scores/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('成绩已删除', 'success');
      loadScores();
    } else {
      showToast(data.message || '删除失败', 'danger');
    }
  } catch (error) {
    console.error('删除成绩失败', error);
    showToast('删除失败', 'danger');
  }
}
