import React from 'react';
import { Upload, Activity, FileText, CheckCircle, Loader2 } from 'lucide-react';
import type { ChatSession } from '../types';
import { translations } from '../i18n';
import type { Lang } from '../i18n';

interface Props {
  currentSession: ChatSession | undefined;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  lang: Lang;
}

const SidebarRight: React.FC<Props> = ({ currentSession, fileInputRef, handleFileUpload, lang }) => {
  const t = translations[lang];

  return (
    <aside className="sidebar-right">
      <div className="docs-header">{t.knowledgeTitle}</div>

      <div className="upload-button" onClick={() => fileInputRef.current?.click()}>
        <Upload size={24} color="var(--text-muted)" style={{ marginBottom: '0.75rem' }} />
        <p style={{ fontSize: '0.85rem', fontWeight: 600 }}>{t.uploadTitle}</p>
        <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{t.uploadSub}</p>
      </div>
      <input type="file" hidden ref={fileInputRef} accept=".pdf" onChange={handleFileUpload} />

      <div className="doc-list">
        <h3 style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          {t.docsSection}
        </h3>
        {currentSession?.documents.length === 0 && (
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '1rem', fontStyle: 'italic' }}>
            {t.noDocs}
          </p>
        )}
        {currentSession?.documents.map(doc => (
          <div key={doc.id} className="doc-item">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <FileText size={16} />
              <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {doc.name}
              </span>
            </div>
            <div className="doc-status">
              {currentSession.vectorizationStatus === 'failed' ? (
                <span className="status-badge failed">{t.uploadFailed}</span>
              ) : (currentSession.vectorizationStatus === 'processing' || doc.status === 'processing') ? (
                <div style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.65rem' }}>
                    <span className="status-badge processing" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Loader2 size={10} className="processing-pulse" />
                      {t.vectorizing}
                    </span>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>
                      {currentSession.vectorizationProgress || 0}%
                    </span>
                  </div>
                  <div className="progress-bar-container">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${currentSession.vectorizationProgress || 0}%` }}
                    ></div>
                  </div>
                </div>
              ) : (
                <>
                  <CheckCircle size={12} color="#16a34a" />
                  <span className="status-badge ready">{t.ready}</span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(128,128,128,0.05)', borderRadius: '12px', fontSize: '0.7rem' }}>
        <Activity size={14} style={{ marginBottom: '0.5rem' }} />
        <p><strong>{t.dataIsolation}</strong> {t.dataIsolationVal}</p>
        <p style={{ opacity: 0.6, marginTop: '0.25rem' }}>{t.dataIsolationDesc}</p>
      </div>
    </aside>
  );
};

export default SidebarRight;
