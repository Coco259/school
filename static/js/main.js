// 登录处理
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (data.success) {
          window.location.href = '/index';
        } else {
          alert(data.message || '登录失败');
        }
      } catch (err) {
        console.error(err);
        alert('请求失败');
      }
    });
  }

  // 登出按钮
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async function() {
      await fetch('/logout');
      window.location.href = '/';
    });
  }

  // 学生页面逻辑
  if (document.getElementById('studentPage')) {
    loadStudents();

    const addStudentForm = document.getElementById('addStudentForm');
    addStudentForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const form = new FormData(addStudentForm);
      const data = {
        name: form.get('name'),
        gender: form.get('gender'),
        age: form.get('age'),
        class: form.get('class')
      };
      try {
        const res = await fetch('/api/students', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
          alert('添加成功');
          addStudentForm.reset();
          loadStudents();
        }
      } catch (err) {
        console.error(err);
      }
    });
  }
});

// 加载学生列表
async function loadStudents() {
  try {
    const res = await fetch('/api/students');
    const students = await res.json();
    const tbody = document.getElementById('studentTableBody');
    tbody.innerHTML = '';
    students.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${s.student_id}</td>
        <td>${s.name}</td>
        <td>${s.gender}</td>
        <td>${s.age}</td>
        <td>${s.class}</td>
        <td>
          <button class="btn btn-sm btn-primary" onclick="editStudent(${s.student_id})">编辑</button>
          <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.student_id})">删除</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('加载学生列表失败', err);
  }
}

// 编辑/保存逻辑（保留原有函数名以兼容模板中的调用）
async function editStudent(studentId) {
  try {
    const response = await fetch(`/api/students/${studentId}`);
    const student = await response.json();
    if (student) {
      document.getElementById('editStudentId').value = student.student_id;
      document.getElementById('editName').value = student.name;
      document.getElementById('editGender').value = student.gender;
      document.getElementById('editAge').value = student.age;
      document.getElementById('editClass').value = student.class;
      const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
      modal.show();
    }
  } catch (error) {
    console.error('加载编辑数据失败:', error);
  }
}

async function saveEditStudent() {
  const studentId = document.getElementById('editStudentId').value;
  const data = {
    name: document.getElementById('editName').value,
    gender: document.getElementById('editGender').value,
    age: document.getElementById('editAge').value,
    class: document.getElementById('editClass').value
  };
  try {
    const response = await fetch(`/api/students/${studentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    if (result.success) {
      alert('修改成功');
      const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentModal'));
      modal.hide();
      loadStudents();
    }
  } catch (error) {
    console.error('保存修改失败:', error);
  }
}

// 删除学生
async function deleteStudent(studentId) {
  if (!confirm('确认删除该学生吗？')) return;
  try {
    const res = await fetch(`/api/students/${studentId}`, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) {
      loadStudents();
    }
  } catch (err) {
    console.error(err);
  }
}
