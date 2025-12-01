import { Card, Row, Col, ProgressBar } from 'react-bootstrap';
import useRequest from '../hooks/useRequest';
import { useMemo } from 'react';

function StatisticsPage() {
  const { data: scores = [], loading } = useRequest('/scores', {}, []);

  const aggregated = useMemo(() => {
    const groups = {};
    scores.forEach((score) => {
      if (!groups[score.course_id]) {
        groups[score.course_id] = { total: 0, count: 0 };
      }
      groups[score.course_id].total += Number(score.score);
      groups[score.course_id].count += 1;
    });
    return Object.entries(groups).map(([course_id, meta]) => ({
      course_id,
      average: meta.total / Math.max(meta.count, 1)
    }));
  }, [scores]);

  return (
    <section>
      <header className="mb-4">
        <h2>统计看板</h2>
      </header>
      {loading && <p>加载中...</p>}
      <Row className="g-3">
        {aggregated.map((item) => (
          <Col md={4} key={item.course_id}>
            <Card>
              <Card.Body>
                <Card.Title>课程 {item.course_id}</Card.Title>
                <Card.Text>平均分：{item.average.toFixed(2)}</Card.Text>
                <ProgressBar now={(item.average / 100) * 100} label={`${item.average.toFixed(0)}分`} />
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </section>
  );
}

export default StatisticsPage;
