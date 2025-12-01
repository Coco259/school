import { Card, Row, Col } from 'react-bootstrap';
import useRequest from '../hooks/useRequest';

function DashboardPage() {
  const { data: students, loading } = useRequest('/students', {}, []);

  return (
    <div>
      <Row className="g-4">
        <Col md={6}>
          <Card>
            <Card.Body>
              <Card.Title>学生总数</Card.Title>
              <Card.Text className="display-6">{loading ? '加载中...' : students?.length ?? '0'}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Body>
              <Card.Title>快速任务</Card.Title>
              <Card.Text>跳转到学生管理、成绩录入等页面。</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default DashboardPage;
