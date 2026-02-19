import { Link, Outlet } from 'react-router-dom';

export function Layout() {
  return (
    <div>
      <header style={{ 
        padding: '1rem', 
        borderBottom: '1px solid #ccc',
        marginBottom: '2rem'
      }}>
        <nav>
          <ul style={{ 
            listStyle: 'none', 
            display: 'flex', 
            gap: '1rem',
            padding: 0,
            margin: 0
          }}>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/ping">Ping Demo</Link>
            </li>
            <li>
              <Link to="/todos">Todos</Link>
            </li>
            <li>
              <Link to="/people">People</Link>
            </li>
            <li>
              <Link to="/calculator">Calculator</Link>
            </li>
          </ul>
        </nav>
      </header>
      <main style={{ padding: '0 1rem' }}>
        <Outlet />
      </main>
    </div>
  );
}
