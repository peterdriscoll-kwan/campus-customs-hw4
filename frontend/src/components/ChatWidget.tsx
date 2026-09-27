import { useEffect, useState, type FormEvent } from "react";
import { Link, useLocation } from "react-router-dom";
import { fetchChatHistory, sendChatMessage } from "../api/chat";
import { productImageUrl, type Product } from "../api/products";
import { formatProductName } from "../utils/productNames";
import { useChatResults } from "../context/ChatResultsContext";
import { useAuth } from "../context/AuthContext";
import "./ChatWidget.css";

interface ChatEntry {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  modelUsed?: string;
}

const GREETING: ChatEntry = {
  role: "assistant",
  content:
    "Hi! I'm the Campus Customs assistant, running on gpt-5.6-luna by default. Ask me about " +
    "hoodies, tees, or anything in the shop — and if you're ever not happy with an answer, just " +
    "ask me to use the smarter model.",
};

function currentProductIdFromPath(pathname: string): string | null {
  const match = pathname.match(/^\/products\/([^/]+)$/);
  return match ? match[1] : null;
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [history, setHistory] = useState<ChatEntry[]>([GREETING]);
  const { setResults } = useChatResults();
  const { user } = useAuth();
  const location = useLocation();

  // Logged-in shoppers pick up their saved conversation; guests always start
  // fresh (guest chats are never persisted server-side, per Problem 8 scope).
  useEffect(() => {
    if (!user) {
      setHistory([GREETING]);
      return;
    }
    let cancelled = false;
    fetchChatHistory(user.id)
      .then((entries) => {
        if (cancelled) return;
        if (entries.length === 0) {
          setHistory([GREETING]);
          return;
        }
        setHistory(entries.map((e) => ({ role: e.role, content: e.content, products: e.products })));
      })
      .catch(() => {
        if (!cancelled) setHistory([GREETING]);
      });
    return () => {
      cancelled = true;
    };
  }, [user]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || pending) return;

    setHistory((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setPending(true);
    try {
      const currentProductId = currentProductIdFromPath(location.pathname);
      const { reply, products, model_used } = await sendChatMessage(
        trimmed,
        user?.id,
        currentProductId ? { current_product_id: currentProductId } : undefined,
      );
      setHistory((prev) => [...prev, { role: "assistant", content: reply, products, modelUsed: model_used }]);
      if (products.length > 0) {
        setResults(trimmed, products);
      }
    } catch {
      setHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't reach the shop assistant right now. Please try again in a moment.",
        },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <div className="chat-widget__panel">
          <div className="chat-widget__header">
            <span>Campus Customs Assistant</span>
            <button
              className="chat-widget__close"
              onClick={() => setOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className="chat-widget__messages">
            {history.map((entry, index) => (
              <div key={index} className={`chat-bubble chat-bubble--${entry.role}`}>
                {entry.modelUsed === "gpt-6-astra" && (
                  <div className="chat-bubble__model-badge">⚡ Answered by gpt-6-astra</div>
                )}
                {entry.content}
                {entry.products && entry.products.length > 0 && (
                  <div className="chat-bubble__products">
                    {entry.products.map((product) => (
                      <Link
                        key={product.product_id}
                        to={`/products/${product.product_id}`}
                        className="chat-product-card"
                      >
                        <img src={productImageUrl(product.image_url)} alt={product.name} />
                        <div>
                          <div className="chat-product-card__name">
                            {formatProductName(product.name)}
                          </div>
                          <div className="chat-product-card__price">
                            ${product.price.toFixed(2)}
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {pending && <div className="chat-bubble chat-bubble--assistant">Thinking…</div>}
          </div>
          <form className="chat-widget__input-row" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about products…"
              aria-label="Chat message"
            />
            <button type="submit" className="button-gold" disabled={pending}>
              Send
            </button>
          </form>
        </div>
      )}
      <button
        className="chat-widget__toggle"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Toggle chat"
      >
        {open ? "Close chat" : "Chat with us"}
      </button>
    </div>
  );
}
