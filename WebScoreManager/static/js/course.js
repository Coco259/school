document.addEventListener('DOMContentLoaded', () => {
  const pageRoot = document.getElementById('coursePage');
  if (!pageRoot) return;
  const { apiFetch, showToast, setLoading, attachValidation, validateForm } = window.AppUtils || {};

  const addCourseForm = document.getElementById('addCourseForm');
  attachValidation(addCourseForm);
  loadCourses();

  addCourseForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (!validateForm(addCourseForm)) {
      showToast('请检查课程信息', 'danger');
      return;
    }
    const submitBtn = addCourseForm.querySelector('button[type="submit"]');
    setLoading(submitBtn, true);
    const form = new FormData(addCourseForm);
    const payload = {
      course_name: form.get('course_name'),
      teacher: form.get('teacher')
    };
    try {
      const res = await apiFetch('/api/courses', { method: 'POST', body: payload });
      const data = await res.json();
      if (data.success) {
        showToast('课程添加成功');
        addCourseForm.reset();
        loadCourses();
      } else {
        showToast(data.message || '添加失败', 'danger');
      }
    } catch (error) {
      console.error('添加课程失败', error);
      showToast('添加课程失败', 'danger');
    } finally {
      setLoading(submitBtn, false);
    }
  });
});

async function loadCourses() {
  const { apiFetch, showToast } = window.AppUtils || {};
  try {
    const res = await apiFetch('/api/courses');
    const courses = await res.json();
    const tbody = document.getElementById('courseTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    courses.forEach(c => {
      const id = c.course_id || c.id || '';
      const name = c.course_name || '';
      const teacher = c.teacher || '';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${id}</td>
        <td>${name}</td>
        <td>${teacher}</td>
        <td>
          <button class="btn btn-sm btn-primary me-2" data-action="edit" data-id="${id}" data-name="${encodeURIComponent(name)}" data-teacher="${encodeURIComponent(teacher)}">编辑</button>
          <button class="btn btn-sm btn-danger" data-action="delete" data-id="${id}">删除</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
    tbody.querySelectorAll('button[data-action="edit"]').forEach(btn => {
      btn.addEventListener('click', () => editCourse(btn.dataset.id, btn.dataset.name, btn.dataset.teacher));
    });
    tbody.querySelectorAll('button[data-action="delete"]').forEach(btn => {
      btn.addEventListener('click', () => deleteCourse(btn.dataset.id));
    });
  } catch (error) {
    console.error('加载课程失败', error);
    showToast('加载课程失败', 'danger');
  }
}

function editCourse(id, name, teacher) {
  document.getElementById('editCourseId').value = id;
  document.getElementById('editCourseName').value = name ? decodeURIComponent(name) : '';
  document.getElementById('editTeacher').value = teacher ? decodeURIComponent(teacher) : '';
  const form = document.getElementById('editCourseForm');
  if (window.AppUtils && window.AppUtils.attachValidation) {
    window.AppUtils.attachValidation(form);
  }
  const modal = new bootstrap.Modal(document.getElementById('editCourseModal'));
  modal.show();
}

async function saveEditCourse() {
  const { apiFetch, showToast, validateForm, setLoading, attachValidation } = window.AppUtils || {};
  const form = document.getElementById('editCourseForm');
  attachValidation(form);
  if (!validateForm(form)) {
    showToast('请检查课程信息', 'danger');
    return;
  }
  const id = document.getElementById('editCourseId').value;
  const submitBtn = document.querySelector('#editCourseModal .btn-primary');
  setLoading(submitBtn, true);
  const payload = {
    course_name: document.getElementById('editCourseName').value,
    teacher: document.getElementById('editTeacher').value
  };
  try {
    const res = await apiFetch(`/api/courses/${id}`, { method: 'PUT', body: payload });
    const data = await res.json();
    if (data.success) {
      showToast('课程信息已更新');
      const modal = bootstrap.Modal.getInstance(document.getElementById('editCourseModal'));
      modal.hide();
      loadCourses();
    } else {
      showToast(data.message || '更新失败', 'danger');
    }
  } catch (error) {
    console.error('保存课程失败', error);
    showToast('保存失败', 'danger');
  } finally {
    setLoading(submitBtn, false);
  }
}

async function deleteCourse(id) {
  const { apiFetch, showToast } = window.AppUtils || {};
  if (!confirm('确认删除该课程吗？')) return;
  try {
    const res = await apiFetch(`/api/courses/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('课程已删除', 'success');
      loadCourses();
    } else {
      showToast(data.message || '删除失败', 'danger');
    }
  } catch (error) {
    console.error('删除课程失败', error);
    showToast('删除失败', 'danger');
  }
}
