import { useMemo, useState } from 'react';
import { Table, Form, Button, Spinner } from 'react-bootstrap';
import useRequest from '../hooks/useRequest';
import { saveScore } from '../services/scoresService';

function ScoresPage() {
  const [form, setForm] = useState({ student_id: '', course_id: '', score: 0 });
  const [submitting, setSubmitting] = useState(false);
  const { data: scores = [], loading } = useRequest('/scores', {}, []);

  const summaries = useMemo(() => {
    return scores.reduce(
      (acc, { score }) => {
        acc.total += Number(score);
        acc.count += 1;
        return acc;
      },
      { total: 0, count: 0 }
    );
  }, [scores]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await saveScore(form);
      setForm({ student_id: '', course_id: '', score: 0 });
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <section>
      <header className="d-flex justify-content-between align-items-center mb-4">
        <h2>成绩录入</h2>
        <p className="text-muted">平均分：{summaries.count ? (summaries.total / summaries.count).toFixed(1) : '--'}</p>
      </header>
      <Form onSubmit={handleSubmit} className="mb-4 d-flex gap-2 flex-wrap">
        <Form.Control
          placeholder="学生ID"
          name="student_id"
          value={form.student_id}
          onChange={handleChange}
          required
        />
        <Form.Control
          placeholder="课程ID"
          name="course_id"
          value={form.course_id}
          onChange={handleChange}
          required
        />
        <Form.Control
          placeholder="分数"
          type="number"
          name="score"
          value={form.score}
          onChange={handleChange}
          required
        />
        <Button type="submit" disabled={submitting}>
          {submitting ? <Spinner animation="border" size="sm" /> : '保存'}
        </Button>
      </Form>
      {loading ? (
        <p>加载成绩中...</p>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>学生ID</th>
              <th>课程ID</th>
              <th>分数</th>
            </tr>
          </thead>
          <tbody>
            {scores.map((item) => (
              <tr key={`${item.student_id}-${item.course_id}`}>
                <td>{item.student_id}</td>
                <td>{item.course_id}</td>
                <td>{item.score}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </section>
  );
}

export default ScoresPage;
