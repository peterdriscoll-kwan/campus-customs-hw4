import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProducts, type Product } from "../api/products";
import ProductCard from "../components/ProductCard";
import { useReveal } from "../hooks/useReveal";
import heroPhoto from "../assets/sterling-library.webp";
import "./HomePage.css";

const HIGHLIGHTS = [
  {
    icon: "🎓",
    title: "Handpicked Yale Gear",
    body: "Hoodies, crewnecks, and tees carrying the colleges, teams, and traditions you know.",
  },
  {
    icon: "📦",
    title: "Real Stock, No Surprises",
    body: "Every size you see is checked against our live inventory before you check out.",
  },
  {
    icon: "💬",
    title: "A Little Help Along the Way",
    body: "Our chat assistant is in the corner whenever you need a hand finding the right fit.",
  },
];

function HighlightCard({ icon, title, body, delay }: { icon: string; title: string; body: string; delay: number }) {
  const { ref, visible } = useReveal<HTMLDivElement>();
  return (
    <div
      ref={ref}
      className={`home__highlight-card reveal${visible ? " reveal--visible" : ""}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <span className="home__highlight-icon">{icon}</span>
      <h2>{title}</h2>
      <p>{body}</p>
    </div>
  );
}

export default function HomePage() {
  const [featured, setFeatured] = useState<Product[]>([]);

  useEffect(() => {
    let cancelled = false;
    fetchProducts()
      .then((data) => {
        if (!cancelled) setFeatured(data.slice(0, 4));
      })
      .catch(() => {
        /* home page still works without the featured strip */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="home">
      <section className="home__hero">
        <div className="home__hero-media">
          <img src={heroPhoto} alt="Sterling Memorial Library on Yale's Central Campus" />
        </div>
        <div className="home__hero-content">
          <span className="eyebrow">New Haven, CT</span>
          <h1>Gear up in Bulldog Blue.</h1>
          <p>
            Campus Customs is the New Haven shop built for anyone who bleeds blue — students,
            alumni, parents, and every fan who's ever chanted for the Bulldogs. From game-day
            hoodies to everyday tees, every piece is picked to feel like home turf.
          </p>
          <div className="home__hero-actions">
            <Link to="/products" className="button-gold">
              Shop the Catalogue
            </Link>
            <Link to="/about" className="button-primary">
              Our Story
            </Link>
          </div>
        </div>
      </section>

      <section className="home__highlights">
        {HIGHLIGHTS.map((item, index) => (
          <HighlightCard key={item.title} icon={item.icon} title={item.title} body={item.body} delay={index * 80} />
        ))}
      </section>

      {featured.length > 0 && (
        <section className="home__featured">
          <div className="home__featured-header">
            <div>
              <span className="eyebrow">Fan Favorites</span>
              <h2>A Few To Get You Started</h2>
            </div>
            <Link to="/products" className="home__featured-link">
              Shop all →
            </Link>
          </div>
          <div className="home__featured-grid">
            {featured.map((product) => (
              <ProductCard key={product.product_id} product={product} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
