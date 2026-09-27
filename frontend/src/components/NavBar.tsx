import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import logo from "../assets/campus-customs-logo.webp";
import "./NavBar.css";

const guestLinks = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
  { to: "/login", label: "Login" },
  { to: "/create-account", label: "Create Account" },
];

const memberLinks = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
];

function CartLink({ itemCount, onClick }: { itemCount: number; onClick?: () => void }) {
  return (
    <NavLink to="/cart" className="navbar__cart" aria-label="Review cart" onClick={onClick}>
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="9" cy="21" r="1.4" fill="currentColor" stroke="none" />
        <circle cx="19" cy="21" r="1.4" fill="currentColor" stroke="none" />
        <path d="M2.5 3h2l2.2 12.2a2 2 0 0 0 2 1.65h8.6a2 2 0 0 0 2-1.62L21 8H6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      {itemCount > 0 && <span className="navbar__cart-badge">{itemCount}</span>}
    </NavLink>
  );
}

export default function NavBar() {
  const { user, logout } = useAuth();
  const { itemCount } = useCart();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const links = user ? memberLinks : guestLinks;

  function handleLogout() {
    logout();
    setMobileOpen(false);
    navigate("/");
  }

  return (
    <header className="navbar">
      <div className="navbar__bar">
        <NavLink to="/" className="navbar__brand" end>
          <img className="navbar__logo" src={logo} alt="Campus Customs" />
          <span className="navbar__title">Campus Customs</span>
        </NavLink>

        <div className="navbar__bar-actions">
          <CartLink itemCount={itemCount} />
          <button
            className="navbar__mobile-toggle"
            onClick={() => setMobileOpen((prev) => !prev)}
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
          >
            <span />
            <span />
            <span />
          </button>
        </div>

        <nav className="navbar__links navbar__links--desktop">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                isActive ? "navbar__link navbar__link--active" : "navbar__link"
              }
            >
              {link.label}
            </NavLink>
          ))}
          <CartLink itemCount={itemCount} />
          {user && (
            <>
              <span className="navbar__greeting">Hi, {user.first_name}</span>
              <button className="navbar__link navbar__logout" onClick={handleLogout}>
                Log Out
              </button>
            </>
          )}
        </nav>
      </div>

      {mobileOpen && (
        <nav className="navbar__links navbar__links--mobile">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                isActive ? "navbar__link navbar__link--active" : "navbar__link"
              }
            >
              {link.label}
            </NavLink>
          ))}
          {user && (
            <>
              <span className="navbar__greeting">Hi, {user.first_name}</span>
              <button className="navbar__link navbar__logout" onClick={handleLogout}>
                Log Out
              </button>
            </>
          )}
        </nav>
      )}
    </header>
  );
}
