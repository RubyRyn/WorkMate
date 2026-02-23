import { Routes, Route } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { ChatWindow } from "./components/ChatWindow";
import { LoginPage } from "./pages/LoginPage";
import { AdminPage } from "./pages/AdminPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminRoute } from "./components/AdminRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminRoute>
              <div className="flex h-screen overflow-hidden bg-white">
                <Sidebar />
                <AdminPage />
              </div>
            </AdminRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <div className="flex h-screen overflow-hidden bg-white">
              <Sidebar />
              <ChatWindow />
            </div>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
