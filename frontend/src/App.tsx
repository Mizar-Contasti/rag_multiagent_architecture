import React, { useState, useRef, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import './index.css';

import { translations } from './i18n';
import type { Lang } from './i18n';
import { useSessions } from './hooks/useSessions';
import { useVectorization } from './hooks/useVectorization';
import { useChat } from './hooks/useChat';
import SidebarLeft from './components/SidebarLeft';
import ChatMain from './components/ChatMain';
import SidebarRight from './components/SidebarRight';

const App: React.FC = () => {
  const [lang, setLang] = useState<Lang>(() =>
    (localStorage.getItem('ai_lang') as Lang) || 'es'
  );
  const [theme, setTheme] = useState<'dark' | 'light'>(() =>
    (localStorage.getItem('ai_theme') as 'dark' | 'light') || 'dark'
  );

  const t = translations[lang];

  // Theme / lang persistence
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ai_theme', theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('ai_lang', lang);
  }, [lang]);

  const {
    sessions, setSessions,
    currentSessionId, setCurrentSessionId,
    loading,
    handleNewChat, deleteSession, handleModelChange,
  } = useSessions(t.newChat);

  useVectorization(sessions, setSessions);

  const currentSession = sessions.find(s => s.id === currentSessionId) || sessions[0];

  const { input, setInput, currentAgentStatus, isLoading, handleSend, handleFileUpload, fileInputRef } =
    useChat(currentSession, currentSessionId, setSessions, lang);

  const chatEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);

  if (loading) {
    return (
      <div className="dashboard" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Loader2 size={32} className="processing-pulse" style={{ opacity: 0.3 }} />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <SidebarLeft
        sessions={sessions}
        currentSessionId={currentSessionId}
        setCurrentSessionId={setCurrentSessionId}
        handleNewChat={handleNewChat}
        deleteSession={deleteSession}
        lang={lang}
        setLang={setLang}
        theme={theme}
        setTheme={setTheme}
      />
      <ChatMain
        currentSession={currentSession}
        currentSessionId={currentSessionId}
        currentAgentStatus={currentAgentStatus}
        isLoading={isLoading}
        input={input}
        setInput={setInput}
        handleSend={handleSend}
        handleModelChange={handleModelChange}
        chatEndRef={chatEndRef}
        lang={lang}
      />
      <SidebarRight
        currentSession={currentSession}
        fileInputRef={fileInputRef}
        handleFileUpload={handleFileUpload}
        lang={lang}
      />
    </div>
  );
};

export default App;
