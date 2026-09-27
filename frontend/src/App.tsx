import { Route, Routes, useLocation } from "react-router-dom";
import NavBar from "./components/NavBar";
import ChatWidget from "./components/ChatWidget";
import ChatResultsPanel from "./components/ChatResultsPanel";
import HomePage from "./pages/HomePage";
import AboutPage from "./pages/AboutPage";
import ProductsPage from "./pages/ProductsPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import LoginPage from "./pages/LoginPage";
import CreateAccountPage from "./pages/CreateAccountPage";
import CartPage from "./pages/CartPage";

export default function App() {
  const location = useLocation();
  const isProductDetail = /^\/products\/[^/]+$/.test(location.pathname);

  return (
    <div className="app-shell">
      <NavBar />
      <main className="app-main">
        {!isProductDetail && <ChatResultsPanel />}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/create-account" element={<CreateAccountPage />} />
          <Route path="/cart" element={<CartPage />} />
        </Routes>
      </main>
      <ChatWidget />
    </div>
  );
}
