import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export interface CartLine {
  productId: string;
  name: string;
  imageUrl: string;
  price: number;
  size: string;
  quantity: number;
}

interface CartContextValue {
  lines: CartLine[];
  itemCount: number;
  subtotal: number;
  addToCart: (line: Omit<CartLine, "quantity">, quantity?: number) => void;
  updateQuantity: (productId: string, size: string, quantity: number) => void;
  removeLine: (productId: string, size: string) => void;
  clearCart: () => void;
}

const STORAGE_KEY = "cc_cart";

const CartContext = createContext<CartContextValue | null>(null);

function loadCart(): CartLine[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>(() => loadCart());

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(lines));
  }, [lines]);

  function addToCart(line: Omit<CartLine, "quantity">, quantity = 1) {
    setLines((prev) => {
      const existing = prev.find((l) => l.productId === line.productId && l.size === line.size);
      if (existing) {
        return prev.map((l) =>
          l.productId === line.productId && l.size === line.size
            ? { ...l, quantity: l.quantity + quantity }
            : l,
        );
      }
      return [...prev, { ...line, quantity }];
    });
  }

  function updateQuantity(productId: string, size: string, quantity: number) {
    setLines((prev) =>
      prev
        .map((l) => (l.productId === productId && l.size === size ? { ...l, quantity } : l))
        .filter((l) => l.quantity > 0),
    );
  }

  function removeLine(productId: string, size: string) {
    setLines((prev) => prev.filter((l) => !(l.productId === productId && l.size === size)));
  }

  function clearCart() {
    setLines([]);
  }

  const itemCount = lines.reduce((sum, l) => sum + l.quantity, 0);
  const subtotal = lines.reduce((sum, l) => sum + l.quantity * l.price, 0);

  return (
    <CartContext.Provider
      value={{ lines, itemCount, subtotal, addToCart, updateQuantity, removeLine, clearCart }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
