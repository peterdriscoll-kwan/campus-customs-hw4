import type { Product } from "./products";

export interface ChatResponse {
  reply: string;
  products: Product[];
  model_used: string;
}

export interface ChatHistoryEntry {
  role: "user" | "assistant";
  content: string;
  products: Product[];
  created_at: string;
}

export interface PageContext {
  current_product_id?: string | null;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function sendChatMessage(
  message: string,
  userId?: number | null,
  pageContext?: PageContext | null,
  useSmartModel?: boolean,
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      user_id: userId ?? null,
      page_context: pageContext ?? null,
      use_smart_model: useSmartModel ?? false,
    }),
  });
  if (!res.ok) throw new Error(`Chat request failed (${res.status})`);
  return res.json();
}

export async function fetchChatHistory(userId: number): Promise<ChatHistoryEntry[]> {
  const res = await fetch(`${API_BASE}/api/chat/history/${userId}`);
  if (!res.ok) throw new Error(`Failed to load chat history (${res.status})`);
  return res.json();
}
