import { useState, useEffect, type FormEvent } from 'react';
import createClient from 'openapi-fetch';
import type { paths } from '@/api_schema';
import styles from './PeoplePage.module.css';

const client = createClient<paths>({ baseUrl: '' });

interface Person {
  id: number;
  name: string;
}

export function PeoplePage() {
  const [people, setPeople] = useState<Person[]>([]);
  const [newPersonName, setNewPersonName] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPeople = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data, error: fetchError } = await client.GET('/api/people');
      if (fetchError) {
        setError('Failed to fetch people');
        return;
      }
      setPeople(data || []);
    } catch (err) {
      setError('Failed to fetch people');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPeople();
  }, []);

  const handleAddPerson = async (e: FormEvent) => {
    e.preventDefault();
    if (!newPersonName.trim()) return;

    setError(null);
    try {
      const { data, error: createError, response } = await client.POST('/api/people', {
        body: { name: newPersonName },
      });
      if (createError) {
        if (response.status === 409) {
          setError('A person with this name already exists');
        } else {
          setError('Failed to create person');
        }
        return;
      }
      if (data) {
        setPeople([...people, data].sort((a, b) => a.name.localeCompare(b.name)));
        setNewPersonName('');
      }
    } catch (err) {
      setError('Failed to create person');
      console.error(err);
    }
  };

  const handleStartEdit = (person: Person) => {
    setEditingId(person.id);
    setEditingName(person.name);
    setError(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingName('');
    setError(null);
  };

  const handleSaveEdit = async (id: number) => {
    if (!editingName.trim()) return;

    setError(null);
    try {
      const { data, error: updateError, response } = await client.PATCH('/api/people/{person_id}', {
        params: { path: { person_id: id } },
        body: { name: editingName },
      });
      if (updateError) {
        if (response.status === 409) {
          setError('A person with this name already exists');
        } else if (response.status === 404) {
          setError('Person not found');
        } else {
          setError('Failed to update person');
        }
        return;
      }
      if (data) {
        setPeople(people.map((p) => (p.id === id ? data : p)).sort((a, b) => a.name.localeCompare(b.name)));
        setEditingId(null);
        setEditingName('');
      }
    } catch (err) {
      setError('Failed to update person');
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    setError(null);
    try {
      const { error: deleteError, response } = await client.DELETE('/api/people/{person_id}', {
        params: { path: { person_id: id } },
      });
      if (deleteError) {
        if (response.status === 409) {
          setError('Cannot delete person who is assigned to tasks');
        } else if (response.status === 404) {
          setError('Person not found');
        } else {
          setError('Failed to delete person');
        }
        return;
      }
      setPeople(people.filter((p) => p.id !== id));
    } catch (err) {
      setError('Failed to delete person');
      console.error(err);
    }
  };

  return (
    <div className={styles.peoplePage}>
      <h1>Team Members</h1>

      {error && (
        <div className={styles.errorMessage}>
          {error}
        </div>
      )}

      <form onSubmit={handleAddPerson} className={styles.personForm}>
        <input
          type="text"
          value={newPersonName}
          onChange={(e) => setNewPersonName(e.target.value)}
          placeholder="Enter person's name..."
          className={styles.personInput}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !newPersonName.trim()}>
          Add Person
        </button>
      </form>

      {loading && people.length === 0 ? (
        <p>Loading people...</p>
      ) : (
        <div className={styles.peopleList}>
          {people.length === 0 ? (
            <p className={styles.emptyState}>No team members yet. Add one above!</p>
          ) : (
            <ul>
              {people.map((person) => (
                <li key={person.id} className={styles.personItem}>
                  {editingId === person.id ? (
                    <div className={styles.editForm}>
                      <input
                        type="text"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        className={styles.editInput}
                        autoFocus
                      />
                      <div className={styles.editActions}>
                        <button
                          onClick={() => handleSaveEdit(person.id)}
                          className={styles.btnSave}
                          disabled={!editingName.trim()}
                        >
                          Save
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className={styles.btnCancel}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <span className={styles.personName}>{person.name}</span>
                      <div className={styles.personActions}>
                        <button
                          onClick={() => handleStartEdit(person)}
                          className={styles.btnEdit}
                          disabled={loading}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(person.id)}
                          className={styles.btnDelete}
                          disabled={loading}
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
