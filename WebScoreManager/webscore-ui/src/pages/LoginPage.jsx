import { useState } from 'react';
import { Form, Button, Alert } from 'react-bootstrap';
import httpClient from '../services/httpClient';

function LoginPage() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setCredentials((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      await httpClient.post('/admin/login', credentials);
      window.location.href = '/';
    } catch (err) {
      setError('登录失败，请检查账号密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="p-4">
      <h2>管理员登录</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit} className="w-100" style={{ maxWidth: 360 }}>
        <Form.Group className="mb-2">
          <Form.Label>用户名</Form.Label>
          <Form.Control name="username" value={credentials.username} onChange={handleChange} required />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Label>密码</Form.Label>
          <Form.Control type="password" name="password" value={credentials.password} onChange={handleChange} required />
        </Form.Group>
        <Button type="submit" disabled={loading}>
          {loading ? '处理中...' : '登录'}
        </Button>
      </Form>
    </section>
  );
}

export default LoginPage;
