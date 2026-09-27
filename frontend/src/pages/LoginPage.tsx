import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { loginAccount } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import "./AuthForm.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setPending(true);
    try {
      const user = await loginAccount({ email, password });
      login(user);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="auth-page">
      <h1 className="page-title">Log In</h1>
      <p className="page-subtitle">
        Sign in with your email and password to see your saved sizes and chat history.
      </p>
      <form className="auth-form" onSubmit={handleSubmit}>
        {error && <p className="auth-form__error">{error}</p>}
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <button type="submit" className="button-primary" disabled={pending}>
          {pending ? "Logging in…" : "Log In"}
        </button>
      </form>
    </div>
  );
}
