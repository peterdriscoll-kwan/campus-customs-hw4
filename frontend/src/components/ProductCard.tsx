import { Link } from "react-router-dom";
import type { Product } from "../api/products";
import { productImageUrl } from "../api/products";
import { formatProductName } from "../utils/productNames";
import { useReveal } from "../hooks/useReveal";
import "./ProductCard.css";

const SWATCH_COLORS: Record<string, string> = {
  navy: "#0f2a4a",
  "navy blue": "#0f2a4a",
  white: "#ffffff",
  gray: "#9aa2ab",
  "heather gray": "#9aa2ab",
  "dark heather gray": "#6b7480",
  "charcoal gray": "#4a5560",
  black: "#111318",
  gold: "#c9a646",
  red: "#a33636",
  green: "#2f7a3d",
};

function swatchColor(name: string): string {
  return SWATCH_COLORS[name.toLowerCase()] ?? "#c8ccd1";
}

export default function ProductCard({ product }: { product: Product }) {
  const displayName = formatProductName(product.name);
  const { ref, visible } = useReveal<HTMLAnchorElement>();
  const lowStock = product.total_stock > 0 && product.total_stock <= 8;

  return (
    <Link
      to={`/products/${product.product_id}`}
      className={`product-card reveal${visible ? " reveal--visible" : ""}`}
      ref={ref}
    >
      <div className="product-card__image-frame">
        <img src={productImageUrl(product.image_url)} alt={displayName} loading="lazy" />
        {lowStock && <span className="product-card__urgency">Only {product.total_stock} left</span>}
      </div>
      <div className="product-card__body">
        <h3 className="product-card__name">{displayName}</h3>
        <p className="product-card__description">{product.description}</p>
        <div className="product-card__swatches">
          {product.colors.slice(0, 5).map((color) => (
            <span
              key={color}
              className="product-card__swatch"
              style={{ background: swatchColor(color) }}
              title={color}
            />
          ))}
        </div>
        <div className="product-card__footer">
          <span className="product-card__price">${product.price.toFixed(2)}</span>
          <span
            className={
              product.total_stock > 0
                ? "product-card__stock"
                : "product-card__stock product-card__stock--out"
            }
          >
            {product.total_stock > 0 ? "In stock" : "Out of stock"}
          </span>
        </div>
      </div>
    </Link>
  );
}
