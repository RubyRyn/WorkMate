import { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ChatWindow } from '../components/ChatWindow';

export function ChatPage() {
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [activeConversationTitle, setActiveConversationTitle] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-slate-900">
      <Sidebar
        activeConversationId={activeConversationId}
        onSelectConversation={(id, title) => {
          setActiveConversationId(id);
          setActiveConversationTitle(title ?? null);
          setSidebarOpen(false);
        }}
        refreshKey={refreshKey}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <ChatWindow
        conversationId={activeConversationId}
        conversationTitle={activeConversationTitle}
        onConversationCreated={(id) => {
          setActiveConversationId(id);
          setRefreshKey((k) => k + 1);
        }}
        onTitleChange={setActiveConversationTitle}
        onMenuClick={() => setSidebarOpen(true)}
      />
    </div>
  );
}
