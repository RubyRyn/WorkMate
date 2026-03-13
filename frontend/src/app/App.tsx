import { Routes, Route } from "react-router-dom";
import { LoginPage } from "./pages/LoginPage";
import { ChatPage } from "./pages/ChatPage";
import { AdminPage } from "./pages/AdminPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminRoute } from "./components/AdminRoute";
import { Sidebar } from "./components/Sidebar";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
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
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <div className="flex h-screen overflow-hidden bg-white dark:bg-slate-900">
              <Sidebar
                activeConversationId={null}
                onSelectConversation={() => {}}
                refreshKey={0}
              />
              <SettingsPage />
            </div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
