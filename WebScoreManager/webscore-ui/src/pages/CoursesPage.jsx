import { Card, Row, Col } from 'react-bootstrap';
import useRequest from '../hooks/useRequest';

function CoursesPage() {
  const { data: courses = [], loading, error } = useRequest('/courses', {}, []);

  return (
    <section>
      <header className="mb-4">
        <h2>课程管理</h2>
      </header>
      {loading && <p>加载中...</p>}
      {error && <p className="text-danger">加载失败，请稍后重试。</p>}
      <Row>
        {courses.map((course) => (
          <Col md={4} key={course.course_id} className="mb-3">
            <Card>
              <Card.Body>
                <Card.Title>{course.course_name}</Card.Title>
                <Card.Text>授课教师：{course.teacher}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </section>
  );
}

export default CoursesPage;
