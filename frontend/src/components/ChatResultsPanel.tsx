import { useChatResults } from "../context/ChatResultsContext";
import ProductCard from "./ProductCard";
import "./ChatResultsPanel.css";

export default function ChatResultsPanel() {
  const { query, products, clear } = useChatResults();
  if (products.length === 0) return null;

  return (
    <section className="chat-results-panel">
      <div className="chat-results-panel__header">
        <div>
          <span className="chat-results-panel__badge">✨ From your chat</span>
          <h2>
            {products.length} match{products.length === 1 ? "" : "es"} for “{query}”
          </h2>
        </div>
        <button
          className="chat-results-panel__clear"
          onClick={clear}
          aria-label="Clear chat results"
        >
          Clear
        </button>
      </div>
      <div className="chat-results-panel__grid">
        {products.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </section>
  );
}
