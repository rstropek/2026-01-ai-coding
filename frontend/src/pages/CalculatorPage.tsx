import { useState, type FormEvent } from 'react';
import createClient from 'openapi-fetch';
import type { paths } from '@/api_schema';
import styles from './CalculatorPage.module.css';

const client = createClient<paths>({ baseUrl: '' });

type State =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; result: number }
  | { status: 'error'; message: string };

export function CalculatorPage() {
  const [a, setA] = useState('');
  const [b, setB] = useState('');
  const [state, setState] = useState<State>({ status: 'idle' });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setState({ status: 'loading' });
    try {
      const { data, error } = await client.POST('/api/calculator/add', {
        body: { a: Number(a), b: Number(b) },
      });
      if (error) {
        setState({ status: 'error', message: 'Failed to calculate. Please try again.' });
        return;
      }
      setState({ status: 'success', result: data.result });
    } catch (err) {
      setState({
        status: 'error',
        message: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  };

  const isValid = a !== '' && b !== '' && !isNaN(Number(a)) && !isNaN(Number(b));

  return (
    <div className={styles.calculatorPage}>
      <h1>Calculator</h1>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.inputs}>
          <label htmlFor="number-a">First number</label>
          <input
            id="number-a"
            type="number"
            step="any"
            value={a}
            onChange={(e) => setA(e.target.value)}
            placeholder="e.g. 3"
            className={styles.input}
            disabled={state.status === 'loading'}
          />
          <label htmlFor="number-b">Second number</label>
          <input
            id="number-b"
            type="number"
            step="any"
            value={b}
            onChange={(e) => setB(e.target.value)}
            placeholder="e.g. 4"
            className={styles.input}
            disabled={state.status === 'loading'}
          />
        </div>
        <button type="submit" disabled={!isValid || state.status === 'loading'}>
          {state.status === 'loading' ? 'Calculating…' : 'Add'}
        </button>
      </form>

      {state.status === 'error' && (
        <p className={styles.error}>{state.message}</p>
      )}
      {state.status === 'success' && (
        <p className={styles.result} id="calculator-result">
          Result: <strong>{state.result}</strong>
        </p>
      )}
    </div>
  );
}
