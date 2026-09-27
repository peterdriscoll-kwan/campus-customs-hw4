import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { fetchProduct, productImageUrl, type Product } from "../api/products";
import { formatProductName } from "../utils/productNames";
import { useCart } from "../context/CartContext";
import "./ProductDetailPage.css";

export default function ProductDetailPage() {
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [justAdded, setJustAdded] = useState(false);
  const { addToCart } = useCart();
  const navigate = useNavigate();

  useEffect(() => {
    if (!productId) return;
    let cancelled = false;
    setStatus("loading");
    setSelectedSize(null);
    setQuantity(1);
    setJustAdded(false);
    fetchProduct(productId)
      .then((data) => {
        if (!cancelled) {
          setProduct(data);
          setStatus("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [productId]);

  if (status === "loading") return <p>Loading product…</p>;
  if (status === "error" || !product) {
    return (
      <div>
        <p className="products-page__error">Couldn't find that product.</p>
        <Link to="/products" className="button-primary">
          Back to Products
        </Link>
      </div>
    );
  }

  const displayName = formatProductName(product.name);
  const selectedLine = product.inventory.find((line) => line.size === selectedSize);
  const canAdd = selectedLine !== undefined && selectedLine.quantity > 0;

  function handleAddToCart() {
    if (!product || !selectedLine || !canAdd) return;
    addToCart(
      {
        productId: product.product_id,
        name: product.name,
        imageUrl: productImageUrl(product.image_url),
        price: product.price,
        size: selectedLine.size,
      },
      quantity,
    );
    setJustAdded(true);
    setTimeout(() => setJustAdded(false), 2200);
  }

  return (
    <div className="product-detail">
      <Link to="/products" className="product-detail__back">
        ← Back to Products
      </Link>
      <div className="product-detail__layout">
        <div className="product-detail__image-frame">
          <img src={productImageUrl(product.image_url)} alt={displayName} />
        </div>
        <div className="product-detail__info">
          <h1>{displayName}</h1>
          <p className="product-detail__type">{product.garment_type}</p>
          <p className="product-detail__price">${product.price.toFixed(2)}</p>
          <p className="product-detail__description">{product.description}</p>

          <div className="product-detail__colors">
            <h3>Colors</h3>
            <div className="product-detail__tag-row">
              {product.colors.map((color) => (
                <span key={color} className="product-detail__tag">
                  {color}
                </span>
              ))}
            </div>
          </div>

          <div className="product-detail__stock">
            <h3>Size</h3>
            <div className="product-detail__size-row">
              {product.inventory.map((line) => {
                const outOfStock = line.quantity === 0;
                const isSelected = selectedSize === line.size;
                return (
                  <button
                    key={line.size}
                    type="button"
                    disabled={outOfStock}
                    className={
                      "size-pill" +
                      (isSelected ? " size-pill--selected" : "") +
                      (outOfStock ? " size-pill--out" : "")
                    }
                    onClick={() => setSelectedSize(line.size)}
                    title={outOfStock ? "Out of stock" : `${line.quantity} available`}
                  >
                    {line.size}
                  </button>
                );
              })}
            </div>
            {selectedLine && (
              <p className={`product-detail__stock-note${selectedLine.quantity === 0 ? " product-detail__out" : ""}`}>
                {selectedLine.quantity === 0
                  ? "Out of stock in this size."
                  : `${selectedLine.quantity} left in size ${selectedLine.size}.`}
              </p>
            )}
          </div>

          <div className="product-detail__add-row">
            <div className="qty-stepper">
              <button type="button" onClick={() => setQuantity((q) => Math.max(1, q - 1))} aria-label="Decrease quantity">
                −
              </button>
              <span>{quantity}</span>
              <button type="button" onClick={() => setQuantity((q) => q + 1)} aria-label="Increase quantity">
                +
              </button>
            </div>
            <button
              type="button"
              className="button-gold"
              disabled={!canAdd}
              onClick={handleAddToCart}
            >
              {selectedSize ? "Add to Cart" : "Select a size"}
            </button>
          </div>

          {justAdded && (
            <div className="product-detail__added-toast">
              Added to cart!{" "}
              <button type="button" onClick={() => navigate("/cart")}>
                Review cart →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
