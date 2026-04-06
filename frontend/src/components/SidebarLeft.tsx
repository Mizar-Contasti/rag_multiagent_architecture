import React from 'react';
import { Plus, MessageSquare, Trash2, FileText, Activity } from 'lucide-react';
import type { ChatSession } from '../types';
import { translations } from '../i18n';
import type { Lang } from '../i18n';

interface Props {
  sessions: ChatSession[];
  currentSessionId: string;
  setCurrentSessionId: (id: string) => void;
  handleNewChat: (title: string) => void;
  deleteSession: (e: React.MouseEvent, id: string) => void;
  lang: Lang;
  setLang: (l: Lang) => void;
  theme: 'dark' | 'light';
  setTheme: (th: 'dark' | 'light') => void;
}

const SidebarLeft: React.FC<Props> = ({
  sessions, currentSessionId, setCurrentSessionId,
  handleNewChat, deleteSession,
  lang, setLang, theme, setTheme,
}) => {
  const t = translations[lang];

  return (
    <aside className="sidebar-left">
      <div className="logo">
        <FileText size={18} />
        AI Document Assistant
      </div>

      <button className="new-chat-btn" onClick={() => handleNewChat(t.newChatN(sessions.length + 1))}>
        <Plus size={18} /> {t.newChat}
      </button>

      <div className="sessions-list">
        {[...sessions].reverse().map(s => (
          <div
            key={s.id}
            className={`session-item ${currentSessionId === s.id ? 'active' : ''}`}
            onClick={() => setCurrentSessionId(s.id)}
          >
            <MessageSquare size={16} />
            <span className="session-title" style={{ flex: 1 }}>{s.title}</span>
            <Trash2 size={14} className="delete-icon" onClick={(e) => deleteSession(e, s.id)} />
          </div>
        ))}
      </div>

      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          <Activity size={12} color="#22c55e" />
          <span>{t.qdrantStatus}</span>
        </div>
        <div className="theme-lang-controls">
          <button onClick={() => setLang(lang === 'es' ? 'en' : 'es')}>
            {lang === 'es' ? 'EN' : 'ES'}
          </button>
          <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default SidebarLeft;
