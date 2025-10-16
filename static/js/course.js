document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('coursePage')) {
    loadCourses();

    const addCourseForm = document.getElementById('addCourseForm');
    addCourseForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const form = new FormData(addCourseForm);
      const data = {
        course_name: form.get('course_name'),
        teacher: form.get('teacher')
      };
      try {
        const res = await fetch('/api/courses', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
          alert('添加成功');
          addCourseForm.reset();
          loadCourses();
        }
      } catch (err) {
        console.error(err);
      }
    });
  }
});

async function loadCourses() {
  try {
    const res = await fetch('/api/courses');
    const courses = await res.json();
    const tbody = document.getElementById('courseTableBody');
    tbody.innerHTML = '';
    courses.forEach(c => {
      const id = c.course_id || c.id || '';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${id}</td>
        <td>${c.course_name}</td>
        <td>${c.teacher}</td>
        <td>
          <button class="btn btn-sm btn-primary" onclick="editCourse(${id}, '${escapeHtml(c.course_name)}', '${escapeHtml(c.teacher)}')">编辑</button>
          <button class="btn btn-sm btn-danger" onclick="deleteCourse(${id})">删除</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('加载课程失败', err);
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function editCourse(id, name, teacher) {
  document.getElementById('editCourseId').value = id;
  document.getElementById('editCourseName').value = name;
  document.getElementById('editTeacher').value = teacher;
  const modal = new bootstrap.Modal(document.getElementById('editCourseModal'));
  modal.show();
}

async function saveEditCourse() {
  const id = document.getElementById('editCourseId').value;
  const data = {
    course_name: document.getElementById('editCourseName').value,
    teacher: document.getElementById('editTeacher').value
  };
  try {
    const res = await fetch(`/api/courses/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.success) {
      alert('保存成功');
      const modal = bootstrap.Modal.getInstance(document.getElementById('editCourseModal'));
      modal.hide();
      loadCourses();
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteCourse(id) {
  if (!confirm('确认删除该课程吗？')) return;
  try {
    const res = await fetch(`/api/courses/${id}`, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) loadCourses();
  } catch (err) {
    console.error(err);
  }
}
