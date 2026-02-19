import { useState, useEffect, type FormEvent } from 'react';
import createClient from 'openapi-fetch';
import type { paths } from '@/api_schema';
import styles from './TodoPage.module.css';

const client = createClient<paths>({ baseUrl: '' });

interface Person {
  id: number;
  name: string;
}

interface Todo {
  id: number;
  title: string;
  is_done: boolean;
  created_at: string;
  assigned_to_id: number | null;
  assigned_to_name: string | null;
}

type FilterValue = 'all' | 'null' | number;

export function TodoPage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [people, setPeople] = useState<Person[]>([]);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoAssignedTo, setNewTodoAssignedTo] = useState<number | null>(null);
  const [filter, setFilter] = useState<FilterValue>('all');
  const [editingAssignId, setEditingAssignId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPeople = async () => {
    const { data } = await client.GET('/api/persons');
    setPeople(data || []);
  };

  const fetchTodos = async (activeFilter: FilterValue) => {
    setLoading(true);
    setError(null);
    try {
      const query: { assigned_to?: string } = {};
      if (activeFilter === 'null') {
        query.assigned_to = 'null';
      } else if (activeFilter !== 'all') {
        query.assigned_to = String(activeFilter);
      }
      const { data, error: fetchError } = await client.GET('/api/todos', { params: { query } });
      if (fetchError) {
        setError('Failed to fetch todos');
        return;
      }
      setTodos(data || []);
    } catch (err) {
      setError('Failed to fetch todos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPeople();
    fetchTodos('all');
  }, []);

  const handleFilterChange = (newFilter: FilterValue) => {
    setFilter(newFilter);
    fetchTodos(newFilter);
  };

  const handleAddTodo = async (e: FormEvent) => {
    e.preventDefault();
    if (!newTodoTitle.trim()) return;

    setError(null);
    try {
      const { data, error: createError } = await client.POST('/api/todos', {
        body: { title: newTodoTitle, assigned_to_id: newTodoAssignedTo },
      });
      if (createError) {
        setError('Failed to create todo');
        return;
      }
      if (data) {
        const shouldShow =
          filter === 'all' ||
          (filter === 'null' && data.assigned_to_id === null) ||
          (typeof filter === 'number' && data.assigned_to_id === filter);
        if (shouldShow) {
          setTodos([data, ...todos]);
        }
        setNewTodoTitle('');
        setNewTodoAssignedTo(null);
      }
    } catch (err) {
      setError('Failed to create todo');
      console.error(err);
    }
  };

  const handleMarkDone = async (id: number) => {
    setError(null);
    try {
      const { data, error: updateError } = await client.PATCH('/api/todos/{todo_id}/done', {
        params: { path: { todo_id: id } },
      });
      if (updateError) {
        setError('Failed to mark todo as done');
        return;
      }
      if (data) {
        setTodos(todos.map((todo) => (todo.id === id ? data : todo)));
      }
    } catch (err) {
      setError('Failed to mark todo as done');
      console.error(err);
    }
  };

  const handleAssignChange = async (todoId: number, assignedToId: number | null) => {
    setError(null);
    try {
      const { data, error: updateError } = await client.PATCH('/api/todos/{todo_id}/assign', {
        params: { path: { todo_id: todoId } },
        body: { assigned_to_id: assignedToId },
      });
      if (updateError) {
        setError('Failed to update assignment');
        return;
      }
      if (data) {
        const shouldRemove =
          (filter === 'null' && data.assigned_to_id !== null) ||
          (typeof filter === 'number' && data.assigned_to_id !== filter);
        if (shouldRemove) {
          setTodos(todos.filter((t) => t.id !== todoId));
        } else {
          setTodos(todos.map((t) => (t.id === todoId ? data : t)));
        }
      }
    } catch (err) {
      setError('Failed to update assignment');
      console.error(err);
    } finally {
      setEditingAssignId(null);
    }
  };

  const handleDelete = async (id: number) => {
    setError(null);
    try {
      const { error: deleteError } = await client.DELETE('/api/todos/{todo_id}', {
        params: { path: { todo_id: id } },
      });
      if (deleteError) {
        setError('Failed to delete todo');
        return;
      }
      setTodos(todos.filter((todo) => todo.id !== id));
    } catch (err) {
      setError('Failed to delete todo');
      console.error(err);
    }
  };

  const filterLabel = () => {
    if (filter === 'all') return 'All tasks';
    if (filter === 'null') return 'Unassigned tasks';
    const person = people.find((p) => p.id === filter);
    return person ? `Tasks for ${person.name}` : 'Filtered tasks';
  };

  return (
    <div className={styles.todoPage}>
      <h1>Todo Management</h1>

      {error && <div className={styles.errorMessage}>{error}</div>}

      <form onSubmit={handleAddTodo} className={styles.todoForm}>
        <input
          type="text"
          value={newTodoTitle}
          onChange={(e) => setNewTodoTitle(e.target.value)}
          placeholder="Enter a new todo..."
          className={styles.todoInput}
          disabled={loading}
        />
        <select
          value={newTodoAssignedTo ?? ''}
          onChange={(e) =>
            setNewTodoAssignedTo(e.target.value === '' ? null : Number(e.target.value))
          }
          className={styles.assignSelect}
          disabled={loading}
        >
          <option value="">Unassigned</option>
          {people.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <button type="submit" disabled={loading || !newTodoTitle.trim()}>
          Add Todo
        </button>
      </form>

      <div className={styles.filterBar}>
        <span className={styles.filterLabel}>Filter by person:</span>
        <button
          className={`${styles.filterBtn} ${filter === 'all' ? styles.filterBtnActive : ''}`}
          onClick={() => handleFilterChange('all')}
        >
          All
        </button>
        <button
          className={`${styles.filterBtn} ${filter === 'null' ? styles.filterBtnActive : ''}`}
          onClick={() => handleFilterChange('null')}
        >
          Unassigned
        </button>
        {people.map((p) => (
          <button
            key={p.id}
            className={`${styles.filterBtn} ${filter === p.id ? styles.filterBtnActive : ''}`}
            onClick={() => handleFilterChange(p.id)}
          >
            {p.name}
          </button>
        ))}
      </div>

      <p className={styles.filterSummary}>
        Showing: <strong>{filterLabel()}</strong> ({todos.length} task{todos.length !== 1 ? 's' : ''})
      </p>

      {loading && todos.length === 0 ? (
        <p>Loading todos...</p>
      ) : (
        <div className={styles.todoList}>
          {todos.length === 0 ? (
            <p className={styles.emptyState}>No todos here. Add one above!</p>
          ) : (
            <ul>
              {todos.map((todo) => (
                <li key={todo.id} className={`${styles.todoItem} ${todo.is_done ? styles.done : ''}`}>
                  <div className={styles.todoContent}>
                    <span className={todo.is_done ? styles.todoTitleDone : styles.todoTitle}>
                      {todo.title}
                    </span>
                    <div className={styles.todoMeta}>
                      <span className={styles.todoDate}>
                        {new Date(todo.created_at).toLocaleDateString()}
                      </span>
                      {editingAssignId === todo.id ? (
                        <select
                          className={styles.assignSelectInline}
                          defaultValue={todo.assigned_to_id ?? ''}
                          autoFocus
                          onChange={(e) => {
                            const val = e.target.value;
                            handleAssignChange(todo.id, val === '' ? null : Number(val));
                          }}
                          onBlur={() => setEditingAssignId(null)}
                        >
                          <option value="">Unassigned</option>
                          {people.map((p) => (
                            <option key={p.id} value={p.id}>
                              {p.name}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <button
                          className={styles.assignedBadge}
                          onClick={() => setEditingAssignId(todo.id)}
                          title="Click to change assignment"
                        >
                          {todo.assigned_to_name ? `Assigned: ${todo.assigned_to_name}` : 'Unassigned'}
                        </button>
                      )}
                    </div>
                  </div>
                  <div className={styles.todoActions}>
                    {!todo.is_done && (
                      <button
                        onClick={() => handleMarkDone(todo.id)}
                        className={styles.btnDone}
                        disabled={loading}
                      >
                        Done
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(todo.id)}
                      className={styles.btnDelete}
                      disabled={loading}
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
