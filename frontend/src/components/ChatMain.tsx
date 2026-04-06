import React from 'react';
import { Send, FileText, Loader2 } from 'lucide-react';
import type { ChatSession } from '../types';
import { GROQ_MODELS } from '../constants';
import { translations } from '../i18n';
import type { Lang } from '../i18n';

interface Props {
  currentSession: ChatSession | undefined;
  currentSessionId: string;
  currentAgentStatus: string;
  isLoading: boolean;
  input: string;
  setInput: (v: string) => void;
  handleSend: () => void;
  handleModelChange: (sessionId: string, modelId: string) => void;
  chatEndRef: React.RefObject<HTMLDivElement | null>;
  lang: Lang;
}

const ChatMain: React.FC<Props> = ({
  currentSession, currentSessionId, currentAgentStatus, isLoading,
  input, setInput, handleSend, handleModelChange, chatEndRef, lang,
}) => {
  const t = translations[lang];

  return (
    <main className="chat-main">
      <header className="agent-status">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div className={`status-dot ${currentAgentStatus !== t.connected ? 'processing-pulse' : ''}`}></div>
          <span>Status: <strong>{currentAgentStatus}</strong></span>
        </div>
        <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>Thread: {currentSessionId}</span>
      </header>

      <div className="chat-container">
        {currentSession?.messages.length === 0 && (
          <div className="empty-state">
            <FileText size={48} style={{ opacity: 0.1, marginBottom: '1.5rem' }} />
            <p style={{ opacity: 0.5 }}>{t.emptyState}</p>
          </div>
        )}
        {currentSession?.messages.map(msg => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div style={{ fontSize: '0.65rem', marginBottom: '0.4rem', opacity: 0.6, fontWeight: 700, textTransform: 'uppercase' }}>
              {msg.sender === 'user' ? t.user : msg.agent}
            </div>
            <div>{msg.text}</div>
            {msg.sender === 'assistant' && (msg.model || msg.executionTime) && (
              <div style={{ 
                marginTop: '0.6rem', 
                fontSize: '0.65rem', 
                opacity: 0.4, 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem',
                borderTop: '1px solid rgba(255,255,255,0.05)',
                paddingTop: '0.4rem'
              }}>
                {msg.model && <span>{msg.model}</span>}
                {msg.executionTime && <span>• {msg.executionTime}s</span>}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div style={{ fontSize: '0.65rem', marginBottom: '0.4rem', opacity: 0.6, fontWeight: 700, textTransform: 'uppercase' }}>
              {t.agentThinking}
            </div>
            <div style={{ display: 'flex', gap: '0.3rem', alignItems: 'center' }}>
              <Loader2 size={14} className="processing-pulse" />
              <span style={{ opacity: 0.6 }}>{t.thinking}</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="input-area">
        <div className="input-wrapper">
          <select
            className="model-selector"
            value={currentSession?.selectedModel}
            onChange={(e) => handleModelChange(currentSessionId, e.target.value)}
          >
            {GROQ_MODELS.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder={t.placeholder}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <button className="send-btn" onClick={handleSend} disabled={isLoading}>
            {isLoading ? <Loader2 size={18} className="processing-pulse" /> : <Send size={18} />}
          </button>
        </div>
      </div>
    </main>
  );
};

export default ChatMain;
