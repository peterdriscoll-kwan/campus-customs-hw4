import { createContext, useContext, useState, type ReactNode } from "react";
import type { Product } from "../api/products";

interface ChatResultsValue {
  query: string | null;
  products: Product[];
  setResults: (query: string, products: Product[]) => void;
  clear: () => void;
}

const ChatResultsContext = createContext<ChatResultsValue | null>(null);

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);

  function setResults(nextQuery: string, nextProducts: Product[]) {
    setQuery(nextQuery);
    setProducts(nextProducts);
  }

  function clear() {
    setQuery(null);
    setProducts([]);
  }

  return (
    <ChatResultsContext.Provider value={{ query, products, setResults, clear }}>
      {children}
    </ChatResultsContext.Provider>
  );
}

export function useChatResults(): ChatResultsValue {
  const ctx = useContext(ChatResultsContext);
  if (!ctx) throw new Error("useChatResults must be used within ChatResultsProvider");
  return ctx;
}
