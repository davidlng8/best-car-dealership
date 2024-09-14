import LoginPanel from "./components/Login/Login"
import RegisterForm from "./components/Register/Register"
import { Routes, Route } from "react-router-dom";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPanel />} />
      <Route path="/register" element={<RegisterForm />} />
    </Routes>
  );
}
export default App;
