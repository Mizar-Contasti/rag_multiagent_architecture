import { useState, useEffect } from 'react';
import type { ChatSession } from '../types';
import { API_BASE, DEFAULT_MODEL } from '../constants';

export function useSessions(defaultTitle: string) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // Load sessions and ensure a new one exists if needed
  useEffect(() => {
    fetch(`${API_BASE}/sessions`)
      .then(r => r.json())
      .then((data: ChatSession[]) => {
        const sorted = data.sort((a, b) => a.id.localeCompare(b.id));
        const lastSession = sorted[sorted.length - 1];
        const isEmpty = lastSession && lastSession.messages.length === 0 && lastSession.documents.length === 0;

        if (data.length === 0 || !isEmpty) {
          // If no sessions, or the last one is not empty, create a new one
          const id = `session-${Date.now()}`;
          const title = defaultTitle || 'Nuevo Chat';
          fetch(`${API_BASE}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, title, selectedModel: DEFAULT_MODEL }),
          }).then(() => {
            const newSession: ChatSession = { id, title, messages: [], documents: [], selectedModel: DEFAULT_MODEL };
            setSessions(prev => [...prev, newSession]);
            setCurrentSessionId(id);
            setLoading(false);
          });
        } else {
          setSessions(data);
          setCurrentSessionId(lastSession.id);
          setLoading(false);
        }
      })
      .catch(() => setLoading(false));
  }, [defaultTitle]);

  const handleNewChat = (title: string) => {
    const id = `session-${Date.now()}`;
    const newSession: ChatSession = { id, title, messages: [], documents: [], selectedModel: DEFAULT_MODEL };
    fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, title, selectedModel: DEFAULT_MODEL }),
    });
    setSessions(prev => [...prev, newSession]);
    setCurrentSessionId(id);
  };

  const deleteSession = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (sessions.length === 1) return;
    fetch(`${API_BASE}/sessions/${id}`, { method: 'DELETE' });
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== id);
      if (currentSessionId === id && filtered.length > 0) {
        setCurrentSessionId(filtered[0].id);
      }
      return filtered;
    });
  };

  const handleModelChange = (currentSessionId: string, modelId: string) => {
    setSessions(prev => prev.map(s =>
      s.id === currentSessionId ? { ...s, selectedModel: modelId } : s
    ));
    fetch(`${API_BASE}/sessions/${currentSessionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ selectedModel: modelId }),
    });
  };

  return {
    sessions,
    setSessions,
    currentSessionId,
    setCurrentSessionId,
    loading,
    handleNewChat,
    deleteSession,
    handleModelChange,
  };
}
