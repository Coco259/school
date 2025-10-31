let classChart;

document.addEventListener('DOMContentLoaded', () => {
  const { apiFetch, showToast, setLoading, attachValidation, validateForm } = window.AppUtils || {};

  const loginForm = document.getElementById('loginForm');
  if (loginForm && attachValidation && validateForm) {
    attachValidation(loginForm);
    loginForm.addEventListener('submit', async event => {
      event.preventDefault();
      if (!validateForm(loginForm)) {
        showToast('请检查表单填写', 'danger');
        return;
      }
      const submitBtn = loginForm.querySelector('button[type="submit"]');
      setLoading(submitBtn, true);
      const payload = {
        username: loginForm.querySelector('#username').value,
        password: loginForm.querySelector('#password').value
      };
      try {
        const res = await apiFetch('/api/login', { method: 'POST', body: payload });
        const data = await res.json();
        if (data.success) {
          showToast('登录成功');
          window.location.href = '/index';
        } else {
          showToast(data.message || '登录失败', 'danger');
        }
      } catch (error) {
        console.error('登录失败', error);
        showToast('请求失败，请稍后再试', 'danger');
      } finally {
        setLoading(submitBtn, false);
      }
    });
  }

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn && apiFetch) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await apiFetch('/logout', { method: 'GET' });
      } catch (error) {
        console.error('登出失败', error);
      }
      window.location.href = '/';
    });
  }

  const studentPage = document.getElementById('studentPage');
  if (studentPage) {
    initStudentsPage();
    initClassDistribution();
  }
});

async function loadStudents() {
  const { apiFetch, showToast } = window.AppUtils || {};
  try {
    const res = await apiFetch('/api/students');
    const students = await res.json();
    const tbody = document.getElementById('studentTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    students.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${s.student_id}</td>
        <td>${s.name || ''}</td>
        <td>${s.gender || ''}</td>
        <td>${s.age ?? ''}</td>
        <td>${s.class || ''}</td>
        <td>
          <button class="btn btn-sm btn-primary me-2" data-action="edit" data-id="${s.student_id}">编辑</button>
          <button class="btn btn-sm btn-danger" data-action="delete" data-id="${s.student_id}">删除</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
    tbody.querySelectorAll('button[data-action="edit"]').forEach(btn => {
      btn.addEventListener('click', () => editStudent(btn.dataset.id));
    });
    tbody.querySelectorAll('button[data-action="delete"]').forEach(btn => {
      btn.addEventListener('click', () => deleteStudent(btn.dataset.id));
    });
  } catch (error) {
    console.error('加载学生列表失败', error);
    showToast('加载学生列表失败', 'danger');
  }
}

function initStudentsPage() {
  const { attachValidation, validateForm, setLoading, showToast, apiFetch } = window.AppUtils || {};
  const addStudentForm = document.getElementById('addStudentForm');
  if (!addStudentForm) return;

  attachValidation(addStudentForm);
  loadStudents();

  addStudentForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (!validateForm(addStudentForm)) {
      showToast('请检查学生信息填写', 'danger');
      return;
    }
    const submitBtn = addStudentForm.querySelector('button[type="submit"]');
    setLoading(submitBtn, true);
    const formData = new FormData(addStudentForm);
    const payload = {
      name: formData.get('name'),
      gender: formData.get('gender'),
      age: Number(formData.get('age')),
      class: formData.get('class')
    };
    try {
      const res = await apiFetch('/api/students', { method: 'POST', body: payload });
      const data = await res.json();
      if (data.success) {
        showToast('学生添加成功');
        addStudentForm.reset();
        loadStudents();
      } else {
        showToast(data.message || '添加失败', 'danger');
      }
    } catch (error) {
      console.error('添加学生失败', error);
      showToast('添加学生失败', 'danger');
    } finally {
      setLoading(submitBtn, false);
    }
  });
}

async function initClassDistribution() {
  const { apiFetch, showToast } = window.AppUtils || {};
  const container = document.getElementById('classScoreChart');
  const selectEl = document.getElementById('classSelect');
  const emptyHint = document.getElementById('classChartEmpty');
  if (!container || !selectEl || typeof echarts === 'undefined' || !apiFetch) {
    return;
  }

  classChart = echarts.init(container);
  window.addEventListener('resize', () => {
    if (classChart) {
      classChart.resize();
    }
  });

  try {
    const res = await apiFetch('/api/statistics/classes');
    if (!res.ok) throw new Error('加载班级失败');
    const classes = await res.json();
    selectEl.innerHTML = '';
    if (!classes.length) {
      toggleClassChartEmpty(true, emptyHint);
      return;
    }
    classes.forEach(className => {
      const option = document.createElement('option');
      option.value = className;
      option.textContent = className;
      selectEl.appendChild(option);
    });
    selectEl.addEventListener('change', () => {
      updateClassDistribution(selectEl.value, emptyHint);
    });
    await updateClassDistribution(selectEl.value, emptyHint);
  } catch (error) {
    console.error('加载班级列表失败', error);
    showToast && showToast('加载班级列表失败', 'danger');
    toggleClassChartEmpty(true, emptyHint);
  }
}

async function updateClassDistribution(className, emptyHint) {
  const { apiFetch, showToast } = window.AppUtils || {};
  if (!className || !classChart || !apiFetch) {
    toggleClassChartEmpty(true, emptyHint);
    return;
  }
  try {
    const res = await apiFetch(`/api/statistics/class/${encodeURIComponent(className)}`);
    if (!res.ok) throw new Error('获取班级成绩失败');
    const data = await res.json();
    renderClassDistribution(data?.distribution || [], className, emptyHint);
  } catch (error) {
    console.error('加载班级成绩分布失败', error);
    showToast && showToast('加载班级成绩分布失败', 'danger');
    toggleClassChartEmpty(true, emptyHint);
  }
}

function renderClassDistribution(distribution, className, emptyHint) {
  if (!classChart) return;
  const xAxisData = Array.isArray(distribution) ? distribution.map(item => item.label) : [];
  const seriesData = Array.isArray(distribution) ? distribution.map(item => item.count || 0) : [];
  const hasData = seriesData.some(count => count > 0);
  toggleClassChartEmpty(!hasData, emptyHint);
  const option = {
    title: {
      text: hasData ? `${className} 班级成绩区间人数` : `${className} 暂无成绩数据`,
      left: 'center',
      textStyle: {
        fontSize: 14,
      },
    },
    tooltip: {
      trigger: 'axis',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '6%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisTick: { alignWithLabel: true },
    },
    yAxis: {
      type: 'value',
      name: '人数',
      minInterval: 1,
    },
    series: [
      {
        type: 'bar',
        data: seriesData,
        itemStyle: {
          color: '#4c8bf5',
        },
        barWidth: '50%',
      },
    ],
  };
  classChart.setOption(option, true);
  classChart.resize();
}

function toggleClassChartEmpty(show, emptyHint) {
  if (!emptyHint) return;
  if (show) {
    emptyHint.classList.remove('d-none');
  } else {
    emptyHint.classList.add('d-none');
  }
}

async function editStudent(studentId) {
  const { apiFetch, showToast } = window.AppUtils || {};
  try {
    const res = await apiFetch(`/api/students/${studentId}`);
    if (!res.ok) throw new Error('加载学生失败');
    const student = await res.json();
    if (!student) {
      showToast('未找到该学生', 'danger');
      return;
    }
    document.getElementById('editStudentId').value = student.student_id;
    document.getElementById('editName').value = student.name || '';
    document.getElementById('editGender').value = student.gender || '男';
    document.getElementById('editAge').value = student.age ?? '';
    document.getElementById('editClass').value = student.class || '';
    const form = document.getElementById('editStudentForm');
    if (window.AppUtils && window.AppUtils.attachValidation) {
      window.AppUtils.attachValidation(form);
    }
    const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
    modal.show();
  } catch (error) {
    console.error('加载编辑数据失败', error);
    showToast('加载学生信息失败', 'danger');
  }
}

async function saveEditStudent() {
  const { apiFetch, showToast, setLoading, validateForm, attachValidation } = window.AppUtils || {};
  const form = document.getElementById('editStudentForm');
  attachValidation(form);
  if (!validateForm(form)) {
    showToast('请检查学生信息', 'danger');
    return;
  }
  const studentId = document.getElementById('editStudentId').value;
  const submitBtn = document.querySelector('#editStudentModal .btn-primary');
  setLoading(submitBtn, true);
  const payload = {
    name: document.getElementById('editName').value,
    gender: document.getElementById('editGender').value,
    age: Number(document.getElementById('editAge').value),
    class: document.getElementById('editClass').value
  };
  try {
    const res = await apiFetch(`/api/students/${studentId}`, { method: 'PUT', body: payload });
    const data = await res.json();
    if (data.success) {
      showToast('学生信息已更新');
      const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentModal'));
      modal.hide();
      loadStudents();
    } else {
      showToast(data.message || '更新失败', 'danger');
    }
  } catch (error) {
    console.error('保存修改失败', error);
    showToast('保存失败', 'danger');
  } finally {
    setLoading(submitBtn, false);
  }
}

async function deleteStudent(studentId) {
  const { apiFetch, showToast } = window.AppUtils || {};
  if (!confirm('确认删除该学生吗？')) return;
  try {
    const res = await apiFetch(`/api/students/${studentId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('学生已删除', 'success');
      loadStudents();
    } else {
      showToast(data.message || '删除失败', 'danger');
    }
  } catch (error) {
    console.error('删除学生失败', error);
    showToast('删除失败', 'danger');
  }
}
