# Design: Making Campus Customs Feel Real

Concrete changes made and why each should help a shopper stick around and actually buy something.

## Typography & color
- Swapped the system-font look for a **Fraunces** (serif, display) + **Inter** (sans, body) pairing — headings now read like a real collegiate retail brand, not a bootstrap template.
- Refined the existing blue/gold/silver palette into consistent tokens (shadows, radii, an easing curve) used everywhere, so buttons, cards, and panels feel like one designed system instead of default browser styling.
- **Why:** a store that looks intentional reads as trustworthy; shoppers judge credibility in the first second, before reading a word of copy.

## Hierarchy
- Added small gold "eyebrow" labels above page headings (New Haven, CT · The Full Lineup · Fan Favorites) to give every page a clear entry point instead of a flat title.
- Real navigation logo (`campus-customs-logo.webp`) replacing the placeholder "CC" badge.
- **Why:** clear visual hierarchy tells a scanning visitor where they are and what matters most on the page, instead of making them read every line to orient themselves.

## Motion
- Scroll-triggered fade/slide-in for product cards and homepage highlight cards (`useReveal`, IntersectionObserver-based, respects `prefers-reduced-motion`).
- Hover interactions: product images zoom slightly, cards lift with a stronger shadow, buttons nudge up on hover/press.
- **Why:** subtle motion makes scrolling through 100+ products feel alive instead of static, and hover feedback makes the whole site feel responsive and modern — both increase the chance someone keeps browsing instead of bouncing.

## Product presentation
- Product cards now show color swatches and a "Only N left" urgency badge when stock is low (≤8).
- Product detail page replaced the plain stock table with clickable size pills (in-stock sizes selectable, out-of-stock sizes struck through and disabled) plus a quantity stepper.
- Added a "Fan Favorites" product strip to the homepage so shoppers see real merchandise before they ever click into the catalogue.
- **Why:** urgency badges and real size-picking (vs. reading a table) are proven conversion patterns — they nudge hesitant browsers toward a decision instead of leaving to "think about it."

## Shopping cart (new)
- Added a lightweight cart: pick a size on the product page, add to cart, see a live cart-count badge in the nav, and review everything on a dedicated `/cart` page (quantity adjust, remove, subtotal).
- Cart state lives in the browser (`localStorage`) — no backend order table, no payment flow.
- The cart page carries a clear, impossible-to-miss notice: **checkout isn't built yet and nothing can be purchased** — by design, since this is a class project, not a live store.
- **Why:** letting a shopper actually build a cart (instead of only browsing) makes the site feel like a real store and gives a much better sense of "would I buy this," while the explicit under-construction notice prevents anyone from mistaking it for a working checkout.
