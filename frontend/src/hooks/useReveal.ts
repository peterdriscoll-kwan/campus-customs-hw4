import { useEffect, useRef, useState } from "react";

/** Scroll-triggered entrance: returns a ref to attach and whether the element
 * has entered the viewport yet. Pair with the `.reveal` / `.reveal--visible`
 * CSS classes. Fires once, then disconnects — this is decoration, not a
 * repeating animation. */
export function useReveal<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return { ref, visible };
}
