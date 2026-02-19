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
  const [newName, setNewName] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPeople = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data, error: fetchError } = await client.GET('/api/persons');
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
    if (!newName.trim()) return;

    setError(null);
    try {
      const { data, error: createError } = await client.POST('/api/persons', {
        body: { name: newName.trim() },
      });
      if (createError) {
        setError('Failed to create person. Name may already exist.');
        return;
      }
      if (data) {
        setPeople([...people, data].sort((a, b) => a.name.localeCompare(b.name)));
        setNewName('');
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
  };

  const handleSaveEdit = async (id: number) => {
    if (!editingName.trim()) return;

    setError(null);
    try {
      const { data, error: updateError } = await client.PUT('/api/persons/{person_id}', {
        params: { path: { person_id: id } },
        body: { name: editingName.trim() },
      });
      if (updateError) {
        setError('Failed to update person. Name may already exist.');
        return;
      }
      if (data) {
        setPeople(
          people
            .map((p) => (p.id === id ? data : p))
            .sort((a, b) => a.name.localeCompare(b.name)),
        );
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
      const { error: deleteError } = await client.DELETE('/api/persons/{person_id}', {
        params: { path: { person_id: id } },
      });
      if (deleteError) {
        setError('Cannot delete this person. They may still be assigned to tasks.');
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
      <h1>People Management</h1>
      <p className={styles.subtitle}>Manage team members who can be assigned to tasks.</p>

      {error && <div className={styles.errorMessage}>{error}</div>}

      <form onSubmit={handleAddPerson} className={styles.addForm}>
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Enter person's name..."
          className={styles.nameInput}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !newName.trim()} className={styles.btnAdd}>
          Add Person
        </button>
      </form>

      {loading && people.length === 0 ? (
        <p>Loading people...</p>
      ) : (
        <div className={styles.peopleList}>
          {people.length === 0 ? (
            <p className={styles.emptyState}>No people yet. Add one above!</p>
          ) : (
            <ul>
              {people.map((person) => (
                <li key={person.id} className={styles.personItem}>
                  {editingId === person.id ? (
                    <div className={styles.editRow}>
                      <input
                        type="text"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        className={styles.nameInput}
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveEdit(person.id);
                          if (e.key === 'Escape') handleCancelEdit();
                        }}
                      />
                      <button
                        onClick={() => handleSaveEdit(person.id)}
                        className={styles.btnSave}
                        disabled={!editingName.trim()}
                      >
                        Save
                      </button>
                      <button onClick={handleCancelEdit} className={styles.btnCancel}>
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className={styles.personRow}>
                      <span className={styles.personName}>{person.name}</span>
                      <div className={styles.personActions}>
                        <button
                          onClick={() => handleStartEdit(person)}
                          className={styles.btnEdit}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(person.id)}
                          className={styles.btnDelete}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
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
