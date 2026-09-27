export interface InventoryLine {
  size: string;
  quantity: number;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  inventory: InventoryLine[];
  total_stock: number;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/api/products`);
  if (!res.ok) throw new Error(`Failed to load products (${res.status})`);
  return res.json();
}

export async function fetchProduct(productId: string): Promise<Product> {
  const res = await fetch(`${API_BASE}/api/products/${encodeURIComponent(productId)}`);
  if (!res.ok) throw new Error(`Failed to load product (${res.status})`);
  return res.json();
}

export function productImageUrl(imageUrl: string): string {
  return `${API_BASE}${imageUrl}`;
}
