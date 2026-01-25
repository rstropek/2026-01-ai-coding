import { useEffect, useState } from 'react';
import createClient from 'openapi-fetch';
import type { paths } from '@/api_schema';

const client = createClient<paths>({ baseUrl: '/' });

export function PingDemo() {
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchPing = async () => {
      try {
        setLoading(true);
        const { data, error } = await client.GET('/api/ping');

        if (error) {
          setError(`Error: ${JSON.stringify(error)}`);
          setMessage('');
        } else if (data) {
          setMessage(data.message);
          setError('');
        }
      } catch (err) {
        setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
        setMessage('');
      } finally {
        setLoading(false);
      }
    };

    fetchPing();
  }, []);

  return (
    <div id="api-result">
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {message && <p style={{ color: 'green' }}>Ping response: {message}</p>}
    </div>
  );
}
