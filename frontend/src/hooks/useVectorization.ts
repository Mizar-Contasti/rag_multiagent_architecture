import { useEffect } from 'react';
import type { ChatSession } from '../types';
import { API_BASE } from '../constants';

export function useVectorization(
  sessions: ChatSession[],
  setSessions: React.Dispatch<React.SetStateAction<ChatSession[]>>,
) {
  useEffect(() => {
    const activeSessions = sessions.filter(s => s.vectorizationStatus === 'processing');
    if (activeSessions.length === 0) return;

    const interval = setInterval(async () => {
      for (const session of activeSessions) {
        try {
          const resp = await fetch(`${API_BASE}/sessions/${session.id}/status`);
          const data = await resp.json();

          if (data.status !== session.vectorizationStatus || data.progress !== session.vectorizationProgress) {
            setSessions(prev => prev.map(s =>
              s.id === session.id
                ? {
                    ...s,
                    vectorizationStatus: data.status,
                    vectorizationProgress: data.progress,
                    documents: data.status === 'completed'
                      ? s.documents.map(d => ({ ...d, status: 'ready' as const }))
                      : s.documents,
                  }
                : s
            ));
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [sessions]);
}
