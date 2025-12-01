import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Navbar, Nav, Button } from 'react-bootstrap';
import clsx from 'clsx';
import './Layout.css';

function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <aside className={clsx('sidebar shadow-sm', { open: sidebarOpen })}>
        <div className="p-4 border-bottom">
          <h5 className="mb-0">WebScore</h5>
          <p className="text-muted">管理台</p>
        </div>
        <Nav className="flex-column p-3 gap-2">
          {[{ to: '/', label: '仪表盘' }, { to: '/students', label: '学生' }, { to: '/courses', label: '课程' }, { to: '/scores', label: '成绩' }, { to: '/statistics', label: '统计' }].map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => clsx('nav-link', { active: isActive })}>
              {item.label}
            </NavLink>
          ))}
        </Nav>
      </aside>
      <div className="flex-grow-1">
        <Navbar bg="light" expand="lg" className="shadow-sm" style={{ height: 'var(--navbar-height)' }}>
          <Navbar.Brand as={Link} to="/">WebScoreManager</Navbar.Brand>
          <Button variant="outline-primary" onClick={() => setSidebarOpen((prev) => !prev)} className="d-lg-none">
            菜单
          </Button>
          <Nav className="ms-auto">
            <Link className="nav-link" to="/login">
              登出
            </Link>
          </Nav>
        </Navbar>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}

export default Layout;
