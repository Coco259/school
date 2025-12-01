import { useEffect, useState } from 'react';
import { Table, Button, Form, Spinner, Row, Col } from 'react-bootstrap';
import { fetchStudents, createStudent } from '../services/studentService';

function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ name: '', age: '', gender: 'male', class: '' });
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await createStudent(form);
      await loadStudents();
      setForm({ name: '', age: '', gender: 'male', class: '' });
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const loadStudents = async () => {
    setLoading(true);
    try {
      const data = await fetchStudents();
      setStudents(data || []);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, []);

  return (
    <section>
      <header className="d-flex justify-content-between align-items-center mb-4">
        <h2>学生管理</h2>
      </header>
      <Form onSubmit={handleSubmit} className="mb-4">
        <Form.Group className="mb-2">
          <Form.Label>姓名</Form.Label>
          <Form.Control name="name" value={form.name} onChange={handleChange} required />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Label>学号/班级</Form.Label>
          <Form.Control name="class" value={form.class} onChange={handleChange} required />
        </Form.Group>
        <Row className="g-2">
          <Col>
            <Form.Group>
              <Form.Label>年龄</Form.Label>
              <Form.Control type="number" name="age" value={form.age} onChange={handleChange} required />
            </Form.Group>
          </Col>
          <Col>
            <Form.Group>
              <Form.Label>性别</Form.Label>
              <Form.Select name="gender" value={form.gender} onChange={handleChange}>
                <option value="male">男</option>
                <option value="female">女</option>
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>
        <Button type="submit" className="mt-3" disabled={submitting}>
          {submitting ? <Spinner animation="border" size="sm" /> : '新增学生'}
        </Button>
      </Form>
      {error && <p className="text-danger">列表加载异常，请重试。</p>}
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>姓名</th>
            <th>性别</th>
            <th>年龄</th>
            <th>班级</th>
          </tr>
        </thead>
        <tbody>
          {students.map((student) => (
            <tr key={student.student_id}>
              <td>{student.name}</td>
              <td>{student.gender}</td>
              <td>{student.age}</td>
              <td>{student.class}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </section>
  );
}

export default StudentsPage;
