export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  agent?: string;
  model?: string;
  executionTime?: number;
}

export interface DocumentInfo {
  id: string;
  name: string;
  status: 'processing' | 'ready';
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  documents: DocumentInfo[];
  selectedModel: string;
  vectorizationStatus?: 'idle' | 'processing' | 'completed' | 'failed';
  vectorizationProgress?: number;
}
