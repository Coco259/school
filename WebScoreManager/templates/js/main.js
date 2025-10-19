// 加载学生数据到编辑模态框
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
      // 显示模态框
      const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
      modal.show();
    }
  } catch (error) {
    console.error('加载编辑数据失败:', error);
  }
}

// 保存编辑后的学生信息
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
      // 关闭模态框并刷新列表
      const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentModal'));
      modal.hide();
      loadStudents();
    }
  } catch (error) {
    console.error('保存修改失败:', error);
  }
}