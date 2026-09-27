import { useEffect, useMemo, useState } from "react";
import { fetchProducts, type Product } from "../api/products";
import ProductCard from "../components/ProductCard";
import { formatProductName } from "../utils/productNames";
import "./ProductsPage.css";

type SortOption = "name" | "price-low" | "price-high";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [query, setQuery] = useState("");
  const [garmentType, setGarmentType] = useState("all");
  const [sort, setSort] = useState<SortOption>("name");

  useEffect(() => {
    let cancelled = false;
    fetchProducts()
      .then((data) => {
        if (!cancelled) {
          setProducts(data);
          setStatus("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const garmentTypes = useMemo(() => {
    const unique = new Set(products.map((p) => p.garment_type));
    return Array.from(unique).sort();
  }, [products]);

  const visibleProducts = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    let result = products.filter((product) => {
      const matchesType = garmentType === "all" || product.garment_type === garmentType;
      if (!matchesType) return false;
      if (!normalizedQuery) return true;
      const haystack = `${product.name} ${product.description} ${product.search_tags.join(" ")}`.toLowerCase();
      return haystack.includes(normalizedQuery);
    });

    result = [...result].sort((a, b) => {
      if (sort === "price-low") return a.price - b.price;
      if (sort === "price-high") return b.price - a.price;
      return formatProductName(a.name).localeCompare(formatProductName(b.name));
    });

    return result;
  }, [products, query, garmentType, sort]);

  const hasActiveFilters = query.trim() !== "" || garmentType !== "all";

  return (
    <div>
      <span className="eyebrow">The Full Lineup</span>
      <h1 className="page-title">Shop the Catalogue</h1>
      <p className="page-subtitle">
        Every item below is pulled live from our inventory database, so prices and stock
        stay accurate.
      </p>

      {status === "loading" && <p>Loading products…</p>}
      {status === "error" && (
        <p className="products-page__error">
          Couldn't reach the Campus Customs API. Make sure the backend is running on
          port 8000.
        </p>
      )}
      {status === "ready" && (
        <>
          <div className="products-filter-bar">
            <input
              type="search"
              className="products-filter-bar__search"
              placeholder="Search products…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search products"
            />
            <select
              className="products-filter-bar__select"
              value={garmentType}
              onChange={(e) => setGarmentType(e.target.value)}
              aria-label="Filter by garment type"
            >
              <option value="all">All types</option>
              {garmentTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            <select
              className="products-filter-bar__select"
              value={sort}
              onChange={(e) => setSort(e.target.value as SortOption)}
              aria-label="Sort products"
            >
              <option value="name">Sort: Name (A–Z)</option>
              <option value="price-low">Sort: Price (low to high)</option>
              <option value="price-high">Sort: Price (high to low)</option>
            </select>
            <span className="products-filter-bar__count">
              {visibleProducts.length} of {products.length} shown
            </span>
            {hasActiveFilters && (
              <button
                type="button"
                className="products-filter-bar__clear"
                onClick={() => {
                  setQuery("");
                  setGarmentType("all");
                }}
              >
                Clear filters
              </button>
            )}
          </div>

          {visibleProducts.length === 0 ? (
            <p className="products-page__empty">
              No products match your search. Try a different term or clear your filters.
            </p>
          ) : (
            <div className="products-grid">
              {visibleProducts.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
