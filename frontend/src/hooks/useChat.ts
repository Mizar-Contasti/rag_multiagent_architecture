import { useState, useRef } from 'react';
import type { ChatSession, Message, DocumentInfo } from '../types';
import { API_BASE, DEFAULT_MODEL } from '../constants';
import { translations } from '../i18n';
import type { Lang } from '../i18n';

export function useChat(
  currentSession: ChatSession | undefined,
  currentSessionId: string,
  setSessions: React.Dispatch<React.SetStateAction<ChatSession[]>>,
  lang: Lang,
) {
  const t = translations[lang];
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgentStatus, setCurrentAgentStatus] = useState<string>(t.connected);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!input.trim() || !currentSession || isLoading) return;

    const userMsg: Message = { id: Date.now().toString(), text: input, sender: 'user' };
    const tempInput = input;
    setInput('');

    const updatedMessages = [...currentSession.messages, userMsg];
    const isFirstMessage = currentSession.messages.length === 0;

    setSessions(prev => prev.map(s =>
      s.id === currentSessionId ? { ...s, messages: updatedMessages } : s
    ));

    setCurrentAgentStatus(t.working);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: tempInput,
          thread_id: currentSessionId,
          model: currentSession.selectedModel || DEFAULT_MODEL,
          is_first_message: isFirstMessage,
        }),
      });
      const data = await response.json();

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: data.reply,
        sender: 'assistant',
        agent: data.agent,
        model: data.model,
        executionTime: data.execution_time,
      };

      setSessions(prev => prev.map(s => {
        if (s.id === currentSessionId) {
          return { 
            ...s, 
            messages: [...updatedMessages, assistantMsg],
            title: data.generated_title || s.title
          };
        }
        return s;
      }));
      setCurrentAgentStatus(t.connected);
    } catch (error) {
      console.error('Chat error:', error);
      setCurrentAgentStatus(t.connError);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !currentSession) return;

    const docId = Date.now().toString();
    const newDoc: DocumentInfo = { id: docId, name: file.name, status: 'processing' };

    const updatedDocs = [...currentSession.documents, newDoc];
    const isFirstDoc = currentSession.documents.length === 0 && currentSession.messages.length === 0;

    setSessions(prev => prev.map(s => {
      if (s.id === currentSessionId) {
        return { 
          ...s, 
          documents: updatedDocs,
          title: isFirstDoc ? file.name.replace(/\.[^/.]+$/, "") : s.title
        };
      }
      return s;
    }));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', currentSessionId);

    try {
      const response = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
      const data = await response.json();

      setSessions(prev => prev.map(s =>
        s.id === currentSessionId ? { ...s, vectorizationStatus: 'processing', vectorizationProgress: 10 } : s
      ));

      const systemMsg: Message = {
        id: Date.now().toString(),
        text: t.processed(data.filename),
        sender: 'assistant',
        agent: t.system,
      };
      setSessions(prev => prev.map(s =>
        s.id === currentSessionId ? { ...s, messages: [...s.messages, systemMsg] } : s
      ));
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  return { input, setInput, currentAgentStatus, isLoading, handleSend, handleFileUpload, fileInputRef };
}
