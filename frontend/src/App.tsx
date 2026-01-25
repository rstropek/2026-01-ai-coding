import './styles.css';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { Home } from '@/pages/Home';
import { PingPage } from '@/pages/PingPage';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="ping" element={<PingPage />} />
      </Route>
    </Routes>
  );
}
