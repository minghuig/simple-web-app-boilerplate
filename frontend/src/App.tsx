import React, { useState, useEffect } from 'react';
import './App.css';

interface ApiResponse {
  message?: string;
  status?: string;
  database?: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
}

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  user_id: number;
}

function App() {
  const [message, setMessage] = useState<string>('');
  const [health, setHealth] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [users, setUsers] = useState<User[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newUsername, setNewUsername] = useState<string>('');
  const [newEmail, setNewEmail] = useState<string>('');
  const [newTaskTitle, setNewTaskTitle] = useState<string>('');
  const [newTaskDescription, setNewTaskDescription] = useState<string>('');
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  const fetchFromAPI = async (endpoint: string, options?: RequestInit): Promise<any> => {
    const response = await fetch(`http://localhost:8000${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });
    return response.json();
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await loadUsers();
      await loadTasks();
      
      const healthResponse = await fetchFromAPI('/api/health');
      setHealth(`${healthResponse.status} - ${healthResponse.database}`);
    } catch (error) {
      setHealth('connection failed');
    }
    setLoading(false);
  };

  const handleTestConnection = async () => {
    setLoading(true);
    try {
      const rootResponse = await fetchFromAPI('/');
      setMessage(rootResponse.message || '');
      
      const healthResponse = await fetchFromAPI('/api/health');
      setHealth(`${healthResponse.status} - ${healthResponse.database}`);
    } catch (error) {
      setMessage('Error connecting to API');
      setHealth('unhealthy');
    }
    setLoading(false);
  };

  const loadUsers = async () => {
    try {
      const users = await fetchFromAPI('/api/users');
      setUsers(users);
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const loadTasks = async () => {
    try {
      const tasks = await fetchFromAPI('/api/tasks');
      setTasks(tasks);
    } catch (error) {
      console.error('Error loading tasks:', error);
    }
  };

  const createUser = async () => {
    if (!newUsername || !newEmail) return;
    
    try {
      await fetchFromAPI('/api/users', {
        method: 'POST',
        body: JSON.stringify({ username: newUsername, email: newEmail }),
      });
      setNewUsername('');
      setNewEmail('');
      await loadUsers();
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  const createTask = async () => {
    if (!newTaskTitle || !selectedUserId) return;
    
    try {
      await fetchFromAPI('/api/tasks', {
        method: 'POST',
        body: JSON.stringify({
          title: newTaskTitle,
          description: newTaskDescription,
          user_id: selectedUserId
        }),
      });
      setNewTaskTitle('');
      setNewTaskDescription('');
      setSelectedUserId(null);
      await loadTasks();
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  const toggleTaskCompletion = async (taskId: number, currentStatus: boolean) => {
    try {
      await fetchFromAPI(`/api/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify({
          completed: !currentStatus
        }),
      });
      await loadTasks();
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Full Stack React + FastAPI + Postgres</h1>
        
        <button 
          onClick={handleTestConnection} 
          disabled={loading}
          style={{ margin: '20px', padding: '10px 20px', fontSize: '16px' }}
        >
          {loading ? 'Testing...' : 'Test Database Connection'}
        </button>

        {message && (
          <div style={{ margin: '10px' }}>
            <strong>API Message:</strong> {message}
          </div>
        )}

        {health && (
          <div style={{ margin: '10px' }}>
            <strong>Health Status:</strong> {health}
          </div>
        )}

        <div style={{ margin: '30px', textAlign: 'left', maxWidth: '800px' }}>
          <h3>Create New User</h3>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <input
              type="text"
              placeholder="Username"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              style={{ padding: '8px' }}
            />
            <input
              type="email"
              placeholder="Email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              style={{ padding: '8px' }}
            />
            <button onClick={createUser} style={{ padding: '8px 16px' }}>
              Create User
            </button>
          </div>

          <h3>Create New Task</h3>
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
              <input
                type="text"
                placeholder="Task title"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                style={{ padding: '8px', minWidth: '200px' }}
              />
              <select
                value={selectedUserId || ''}
                onChange={(e) => setSelectedUserId(e.target.value ? Number(e.target.value) : null)}
                style={{ padding: '8px', minWidth: '150px' }}
              >
                <option value="">Select User</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.username}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
              <textarea
                placeholder="Task description (optional)"
                value={newTaskDescription}
                onChange={(e) => setNewTaskDescription(e.target.value)}
                style={{ padding: '8px', minWidth: '300px', minHeight: '60px' }}
              />
              <button 
                onClick={createTask} 
                disabled={!newTaskTitle || !selectedUserId}
                style={{ padding: '8px 16px', alignSelf: 'flex-start' }}
              >
                Create Task
              </button>
            </div>
          </div>

          <h3>Users ({users.length})</h3>
          <div style={{ marginBottom: '30px' }}>
            {users.map((user) => (
              <div key={user.id} style={{ 
                border: '1px solid #ccc', 
                padding: '10px', 
                margin: '5px 0',
                color: 'black',
                backgroundColor: '#f9f9f9'
              }}>
                <strong>{user.username}</strong> ({user.email})
              </div>
            ))}
          </div>

          <h3>Tasks ({tasks.length})</h3>
          <div>
            {tasks.map((task) => (
              <div key={task.id} style={{ 
                border: '1px solid #ccc', 
                padding: '15px', 
                margin: '5px 0',
                color: 'black',
                backgroundColor: task.completed ? '#e8f5e8' : '#fff3cd',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '15px'
              }}>
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => toggleTaskCompletion(task.id, task.completed)}
                  style={{ marginTop: '2px', transform: 'scale(1.2)' }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <strong style={{ textDecoration: task.completed ? 'line-through' : 'none' }}>
                      {task.title}
                    </strong>
                    {task.completed ? '✅' : '⏳'}
                  </div>
                  {task.description && (
                    <div style={{ 
                      marginTop: '5px', 
                      fontStyle: 'italic',
                      textDecoration: task.completed ? 'line-through' : 'none'
                    }}>
                      {task.description}
                    </div>
                  )}
                  <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
                    User: {users.find(u => u.id === task.user_id)?.username || `ID ${task.user_id}`}
                  </small>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginTop: '40px', fontSize: '14px' }}>
          <p>Frontend: React (Port 3000)</p>
          <p>Backend: FastAPI (Port 8000)</p>
          <p>Database: Postgres</p>
        </div>
      </header>
    </div>
  );
}

export default App;
