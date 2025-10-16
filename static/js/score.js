document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('scorePage')) {
    loadScores();

    const addScoreForm = document.getElementById('addScoreForm');
    addScoreForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const form = new FormData(addScoreForm);
      const data = {
        student_id: form.get('student_id'),
        course_id: form.get('course_id'),
        score: form.get('score')
      };
      try {
        const res = await fetch('/api/scores', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
          alert('添加成功');
          addScoreForm.reset();
          loadScores();
        }
      } catch (err) {
        console.error(err);
      }
    });
  }
});

async function loadScores() {
  try {
    const res = await fetch('/api/scores');
    const scores = await res.json();
    const tbody = document.getElementById('scoreTableBody');
    tbody.innerHTML = '';
    scores.forEach(s => {
      const id = s.id || s.score_id || '';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${id}</td>
        <td>${s.student_id}</td>
        <td>${s.course_id}</td>
        <td>${s.score}</td>
        <td>
          <button class="btn btn-sm btn-primary" onclick="editScore(${id}, ${s.student_id}, ${s.course_id}, ${s.score})">编辑</button>
          <button class="btn btn-sm btn-danger" onclick="deleteScore(${id})">删除</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('加载成绩失败', err);
  }
}

function editScore(id, student_id, course_id, score) {
  document.getElementById('editScoreId').value = id;
  document.getElementById('editStudentId').value = student_id;
  document.getElementById('editCourseId').value = course_id;
  document.getElementById('editScore').value = score;
  const modal = new bootstrap.Modal(document.getElementById('editScoreModal'));
  modal.show();
}

async function saveEditScore() {
  const id = document.getElementById('editScoreId').value;
  const data = {
    student_id: document.getElementById('editStudentId').value,
    course_id: document.getElementById('editCourseId').value,
    score: document.getElementById('editScore').value
  };
  try {
    const res = await fetch(`/api/scores/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.success) {
      alert('保存成功');
      const modal = bootstrap.Modal.getInstance(document.getElementById('editScoreModal'));
      modal.hide();
      loadScores();
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteScore(id) {
  if (!confirm('确认删除该成绩吗？')) return;
  try {
    const res = await fetch(`/api/scores/${id}`, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) loadScores();
  } catch (err) {
    console.error(err);
  }
}
