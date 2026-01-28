import './styles.css';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { Home } from '@/pages/Home';
import { PingPage } from '@/pages/PingPage';
import { TodoPage } from '@/pages/TodoPage';
import { PeoplePage } from '@/pages/PeoplePage';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="ping" element={<PingPage />} />
        <Route path="todos" element={<TodoPage />} />
        <Route path="people" element={<PeoplePage />} />
      </Route>
    </Routes>
  );
}
