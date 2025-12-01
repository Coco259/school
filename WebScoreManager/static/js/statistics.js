document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('statisticsPage');
  if (!root) return;
  const { apiFetch, showToast } = window.AppUtils || {};

  const classSelect = document.getElementById('classSelect');
  const courseSelect = document.getElementById('courseSelect');
  const classSummary = document.getElementById('classSummary');
  const courseSummary = document.getElementById('courseSummary');
  const courseTopTable = document.getElementById('courseTopTable');

  let classDistributionChart;
  let classRankingChart;
  let courseDistributionChart;

  init();

  async function init() {
    await Promise.all([loadClassOptions(), loadCourseOptions()]);
  }

  async function loadClassOptions() {
    try {
      const res = await apiFetch('/api/statistics/classes');
      if (!res.ok) throw new Error('加载班级列表失败');
      const classes = await res.json();
      classSelect.innerHTML = '';
      if (classes.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = '暂无班级数据';
        classSelect.appendChild(option);
        return;
      }
      classes.forEach(c => {
        const option = document.createElement('option');
        option.value = c;
        option.textContent = c;
        classSelect.appendChild(option);
      });
      classSelect.addEventListener('change', () => {
        if (classSelect.value) {
          loadClassStatistics(classSelect.value);
        }
      });
      loadClassStatistics(classSelect.value);
    } catch (error) {
      console.error('加载班级失败', error);
      showToast('加载班级列表失败', 'danger');
    }
  }

  async function loadCourseOptions() {
    try {
      const res = await apiFetch('/api/statistics/courses');
      if (!res.ok) throw new Error('加载课程失败');
      const courses = await res.json();
      courseSelect.innerHTML = '';
      if (!courses.length) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = '暂无课程数据';
        courseSelect.appendChild(option);
        return;
      }
      courses.forEach(course => {
        const option = document.createElement('option');
        option.value = course.course_id;
        option.textContent = `${course.course_name || '未命名'} (#${course.course_id})`;
        courseSelect.appendChild(option);
      });
      courseSelect.addEventListener('change', () => {
        if (courseSelect.value) {
          loadCourseStatistics(courseSelect.value);
        }
      });
      loadCourseStatistics(courseSelect.value);
    } catch (error) {
      console.error('加载课程失败', error);
      showToast('加载课程列表失败', 'danger');
    }
  }

  async function loadClassStatistics(className) {
    if (!className) return;
    try {
      const res = await apiFetch(`/api/statistics/class/${encodeURIComponent(className)}`);
      if (!res.ok) throw new Error('获取班级统计失败');
      const data = await res.json();
      renderSummary(classSummary, [
        { label: '平均分', value: formatNumber(data.summary.average_score) },
        { label: '最高分', value: formatNumber(data.summary.max_score) },
        { label: '最低分', value: formatNumber(data.summary.min_score) },
        { label: '成绩数量', value: data.summary.count_entries }
      ]);
      renderClassDistribution(data.distribution);
      renderClassRanking(data.students);
    } catch (error) {
      console.error('加载班级统计失败', error);
      showToast('加载班级统计失败', 'danger');
    }
  }

  async function loadCourseStatistics(courseId) {
    if (!courseId) return;
    try {
      const res = await apiFetch(`/api/statistics/course/${courseId}`);
      if (res.status === 404) {
        showToast('课程不存在', 'danger');
        return;
      }
      if (!res.ok) throw new Error('获取课程统计失败');
      const data = await res.json();
      renderSummary(courseSummary, [
        { label: '课程', value: data.course_name },
        { label: '平均分', value: formatNumber(data.summary.average_score) },
        { label: '最高分', value: formatNumber(data.summary.max_score) },
        { label: '最低分', value: formatNumber(data.summary.min_score) },
        { label: '成绩数量', value: data.summary.count_entries }
      ]);
      renderCourseDistribution(data.distribution);
      renderTopStudents(data.top_students);
    } catch (error) {
      console.error('加载课程统计失败', error);
      showToast('加载课程统计失败', 'danger');
    }
  }

  function renderSummary(container, items) {
    container.innerHTML = '';
    items.forEach(item => {
      const col = document.createElement('div');
      col.className = 'col-6 col-lg-3';
      col.innerHTML = `
        <div class="border rounded py-2">
          <div class="small text-muted">${item.label}</div>
          <div class="fw-semibold fs-5">${item.value ?? '-'}</div>
        </div>`;
      container.appendChild(col);
    });
  }

  function renderClassDistribution(distribution) {
    const ctx = document.getElementById('classDistributionChart');
    if (!ctx) return;
    if (classDistributionChart) classDistributionChart.destroy();
    classDistributionChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: distribution.map(d => d.label),
        datasets: [{
          label: '人数',
          data: distribution.map(d => d.count),
          backgroundColor: '#0d6efd'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, precision: 0 } }
      }
    });
  }

  function renderClassRanking(students) {
    const ctx = document.getElementById('classRankingChart');
    if (!ctx) return;
    if (classRankingChart) classRankingChart.destroy();
    const labels = students.map(item => `${item.name || item.student_id}`);
    const data = students.map(item => item.total_score);
    classRankingChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: '总分',
          data,
          backgroundColor: '#20c997'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  function renderCourseDistribution(distribution) {
    const ctx = document.getElementById('courseDistributionChart');
    if (!ctx) return;
    if (courseDistributionChart) courseDistributionChart.destroy();
    courseDistributionChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: distribution.map(d => d.label),
        datasets: [{
          label: '人数',
          data: distribution.map(d => d.count),
          backgroundColor: '#6610f2'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, precision: 0 } }
      }
    });
  }

  function renderTopStudents(topStudents) {
    courseTopTable.innerHTML = '';
    if (!topStudents.length) {
      const row = document.createElement('tr');
      row.innerHTML = '<td colspan="3" class="text-center text-muted">暂无数据</td>';
      courseTopTable.appendChild(row);
      return;
    }
    topStudents.forEach((item, index) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${index + 1}</td>
        <td>${item.name || item.student_id}</td>
        <td>${formatNumber(item.score)}</td>`;
      courseTopTable.appendChild(row);
    });
  }

  function formatNumber(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return '-';
    return Number(value).toFixed(2);
  }
});
