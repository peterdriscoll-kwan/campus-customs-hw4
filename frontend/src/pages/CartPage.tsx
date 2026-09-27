import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { formatProductName } from "../utils/productNames";
import "./CartPage.css";

export default function CartPage() {
  const { lines, subtotal, updateQuantity, removeLine, clearCart } = useCart();

  return (
    <div>
      <span className="eyebrow">Review Cart</span>
      <h1 className="page-title">Your Cart</h1>
      <p className="page-subtitle">
        Everything you've added is saved right here in your browser, ready to review.
      </p>

      <div className="cart-notice">
        🚧 <strong>This is a class project preview.</strong> Checkout isn't built yet, so nothing
        below can actually be purchased — this page is here to show what reviewing a cart would
        feel like.
      </div>

      {lines.length === 0 ? (
        <div className="cart-empty">
          <p>Your cart is empty.</p>
          <Link to="/products" className="button-gold">
            Browse the Catalogue
          </Link>
        </div>
      ) : (
        <div className="cart-layout">
          <div className="cart-lines">
            {lines.map((line) => (
              <div className="cart-line" key={`${line.productId}-${line.size}`}>
                <Link to={`/products/${line.productId}`} className="cart-line__image">
                  <img src={line.imageUrl} alt={line.name} />
                </Link>
                <div className="cart-line__info">
                  <Link to={`/products/${line.productId}`} className="cart-line__name">
                    {formatProductName(line.name)}
                  </Link>
                  <div className="cart-line__size">Size {line.size}</div>
                  <button
                    className="cart-line__remove"
                    onClick={() => removeLine(line.productId, line.size)}
                  >
                    Remove
                  </button>
                </div>
                <div className="cart-line__qty">
                  <button
                    aria-label="Decrease quantity"
                    onClick={() => updateQuantity(line.productId, line.size, line.quantity - 1)}
                  >
                    −
                  </button>
                  <span>{line.quantity}</span>
                  <button
                    aria-label="Increase quantity"
                    onClick={() => updateQuantity(line.productId, line.size, line.quantity + 1)}
                  >
                    +
                  </button>
                </div>
                <div className="cart-line__price">${(line.price * line.quantity).toFixed(2)}</div>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <h2>Order Summary</h2>
            <div className="cart-summary__row">
              <span>Subtotal</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <p className="cart-summary__note">Shipping and tax aren't calculated in this preview.</p>
            <button className="button-gold cart-summary__checkout" disabled title="Checkout is under construction">
              Checkout — Coming Soon
            </button>
            <button className="cart-summary__clear" onClick={clearCart}>
              Clear cart
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
