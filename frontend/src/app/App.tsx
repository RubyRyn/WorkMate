import { Routes, Route } from "react-router-dom";
import { ChatPage } from "./pages/ChatPage";
import { AdminPage } from "./pages/AdminPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminRoute } from "./components/AdminRoute";
import { Sidebar } from "./components/Sidebar";

export default function App() {
  return (
    <ProtectedRoute>
      <Routes>
        <Route
          path="admin"
          element={
            <AdminRoute>
              <div className="flex h-screen overflow-hidden bg-white dark:bg-slate-900">
                <Sidebar
                  activeConversationId={null}
                  onSelectConversation={() => {}}
                  refreshKey={0}
                />
                <AdminPage />
              </div>
            </AdminRoute>
          }
        />
        <Route
          path="settings"
          element={
            <div className="flex h-screen overflow-hidden bg-white dark:bg-slate-900">
              <Sidebar
                activeConversationId={null}
                onSelectConversation={() => {}}
                refreshKey={0}
              />
              <SettingsPage />
            </div>
          }
        />
        <Route path="*" element={<ChatPage />} />
      </Routes>
    </ProtectedRoute>
  );
}
