import { useState, useEffect, type FormEvent } from 'react';
import createClient from 'openapi-fetch';
import type { paths } from '@/api_schema';
import styles from './TodoPage.module.css';

const client = createClient<paths>({ baseUrl: '' });

interface Todo {
  id: number;
  title: string;
  is_done: boolean;
  created_at: string;
  assigned_to_id: number | null;
}

interface Person {
  id: number;
  name: string;
}

export function TodoPage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [people, setPeople] = useState<Person[]>([]);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoAssignedTo, setNewTodoAssignedTo] = useState<number | null>(null);
  const [filterPersonId, setFilterPersonId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPeople = async () => {
    try {
      const { data } = await client.GET('/api/people');
      setPeople(data || []);
    } catch (err) {
      console.error('Failed to fetch people:', err);
    }
  };

  const fetchTodos = async (assignedToId: number | null = null) => {
    setLoading(true);
    setError(null);
    try {
      const { data, error: fetchError } = await client.GET('/api/todos', {
        params: assignedToId !== null ? { query: { assigned_to_id: assignedToId } } : {},
      });
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
    fetchTodos();
  }, []);

  useEffect(() => {
    fetchTodos(filterPersonId);
  }, [filterPersonId]);

  const handleAddTodo = async (e: FormEvent) => {
    e.preventDefault();
    if (!newTodoTitle.trim()) return;

    setError(null);
    try {
      const { data, error: createError } = await client.POST('/api/todos', {
        body: { 
          title: newTodoTitle,
          assigned_to_id: newTodoAssignedTo,
        },
      });
      if (createError) {
        setError('Failed to create todo');
        return;
      }
      if (data) {
        setTodos([data, ...todos]);
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

  const handleAssign = async (todoId: number, personId: number | null) => {
    setError(null);
    try {
      const { data, error: assignError } = await client.PATCH('/api/todos/{todo_id}/assign', {
        params: { path: { todo_id: todoId } },
        body: { assigned_to_id: personId },
      });
      if (assignError) {
        setError('Failed to assign todo');
        return;
      }
      if (data) {
        setTodos(todos.map((todo) => (todo.id === todoId ? data : todo)));
      }
    } catch (err) {
      setError('Failed to assign todo');
      console.error(err);
    }
  };

  const getPersonName = (personId: number | null): string => {
    if (personId === null) return 'Unassigned';
    const person = people.find((p) => p.id === personId);
    return person ? person.name : 'Unknown';
  };

  return (
    <div className={styles.todoPage}>
      <h1>Todo Management</h1>

      {error && (
        <div className={styles.errorMessage}>
          {error}
        </div>
      )}

      <div className={styles.filterSection}>
        <label htmlFor="filter">Filter by person:</label>
        <select
          id="filter"
          value={filterPersonId ?? ''}
          onChange={(e) => setFilterPersonId(e.target.value ? Number(e.target.value) : null)}
          className={styles.filterSelect}
        >
          <option value="">All todos</option>
          <option value="0">Unassigned</option>
          {people.map((person) => (
            <option key={person.id} value={person.id}>
              {person.name}
            </option>
          ))}
        </select>
      </div>

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
          onChange={(e) => setNewTodoAssignedTo(e.target.value ? Number(e.target.value) : null)}
          className={styles.assignSelect}
          disabled={loading}
        >
          <option value="">Unassigned</option>
          {people.map((person) => (
            <option key={person.id} value={person.id}>
              {person.name}
            </option>
          ))}
        </select>
        <button type="submit" disabled={loading || !newTodoTitle.trim()}>
          Add Todo
        </button>
      </form>

      {loading && todos.length === 0 ? (
        <p>Loading todos...</p>
      ) : (
        <div className={styles.todoList}>
          {todos.length === 0 ? (
            <p className={styles.emptyState}>No todos yet. Add one above!</p>
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
                      <span className={styles.todoAssignment}>
                        Assigned to: {getPersonName(todo.assigned_to_id)}
                      </span>
                    </div>
                  </div>
                  <div className={styles.todoActions}>
                    <select
                      value={todo.assigned_to_id ?? ''}
                      onChange={(e) => handleAssign(todo.id, e.target.value ? Number(e.target.value) : null)}
                      className={styles.assignSelect}
                      disabled={loading}
                      title="Assign to person"
                    >
                      <option value="">Unassigned</option>
                      {people.map((person) => (
                        <option key={person.id} value={person.id}>
                          {person.name}
                        </option>
                      ))}
                    </select>
                    {!todo.is_done && (
                      <button
                        onClick={() => handleMarkDone(todo.id)}
                        className={styles.btnDone}
                        disabled={loading}
                      >
                        ✓ Done
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
