# Usability Improvements

Two front-end improvements (look better / easier to use) and two agent/backend improvements (more accurate / safer), built and verified live in the running app.

## Front-end 1: Product search and filter bar (easier to use)

**What I added:** A filter bar above the `/products` grid with a live text search (matches name, description, and search tags), a garment-type dropdown, a sort control (name A–Z, price low→high, price high→low), a running "X of Y shown" count, and a one-click "Clear filters" button. All client-side over the already-fetched catalogue — no new backend endpoint needed.

**Why it helps Campus Customs shoppers:** With 102 products and no way to narrow them before, finding "just the navy hoodies" or "the cheapest option" meant scrolling and reading every card. Now that's an instant filter/sort instead of a scroll.

**Why it helps the business:** Faster discovery reduces the chance a shopper gives up scrolling before finding something they want, and price-sorting surfaces budget-friendly options to price-sensitive shoppers — both should help conversion on a long catalogue page.

## Front-end 2: Responsive mobile navigation menu (easier to use)

**What I added:** Below 720px wide, the nav bar's link row (which previously just wrapped awkwardly onto multiple lines) collapses behind a hamburger button. Tapping it opens a stacked dropdown menu with the same links (Home/Products/About/Login or the greeting+Log Out for a logged-in shopper). Desktop layout is unchanged above that breakpoint.

**Why it helps Campus Customs shoppers:** Anyone browsing on a phone (a very likely way to shop for merch, e.g. at a tailgate or in line at the store) previously got a cramped, wrapped nav bar eating up screen space above the fold. Now they get a clean single-line header and a normal mobile menu pattern.

**Why it helps the business:** Mobile visitors who hit an awkward, unpolished header on arrival are more likely to bounce before ever seeing the catalogue — a broken first impression costs sales on a channel (phones) that a New Haven foot-traffic-adjacent shop should expect a lot of.

## Frontend 3: Real campus photography on Home and About (looks better)

*Note: this one was actually built ahead of schedule — I started on it thinking it was part of this problem, but it's really Problem 10's "style the website" territory. Keeping the entry here since it's already live, but it's a bonus, not one of this problem's two required frontend improvements (those are Frontend 1 and 2 above).*

**What I added:** Replaced the plain navy gradient hero banner with a two-column split layout — a real photo on one side, heading/copy/call-to-action buttons on a navy panel on the other. Home uses a photo of Sterling Memorial Library; About Us uses a photo of the actual Campus Customs storefront. Both are real photos the user supplied directly (not AI-generated imagery — this project's convention is to use HTML/CSS rendering instead of generated image assets for pictures, but a real photo the user owns and asked to feature is a different case, so it was used directly as a static asset in `frontend/src/assets/`). Iterated live per user feedback: first tried a CSS/SVG skyline illustration, then a full-bleed photo with a text-overlay scrim, before landing on this side-by-side split layout.

**Why it helps Campus Customs shoppers:** It immediately signals "this is a real Yale-area shop, not a generic template store" — the About page literally shows the storefront a shopper could walk into, building trust before they ever read a word of copy.

**Why it helps the business:** Recognizable, professional campus imagery strengthens the Yale/New Haven brand connection and looks more credible than a flat color banner, which should improve time-on-page and click-through into "Shop the Catalogue" / "Our Story."

## Agent/Backend 1: On-demand smarter model (`gpt-6-astra` via Portkey), requested conversationally

**What I added:** No visible "advanced settings" toggle for this — instead, the chat's opening greeting tells the shopper up front that `gpt-5.6-luna` answers by default, and invites them to just ask for the smarter model if they're not happy with an answer. `backend/agent.py`'s `wants_smart_model()` scans the shopper's own message for a plain-language request ("smarter model," "better model," "use astra," naming `gpt-6-astra` directly, etc.) and escalates that turn to `gpt-6-astra` — no explicit UI control to discover or flip. This needed real architecture changes, not just a config flag:
- Agents are cached per model name (`agent.py`'s `_agent_cache`) instead of one single module-level agent, so switching models per-request doesn't rebuild a client every time.
- `gpt-6-astra` is a reasoning model. Live testing surfaced a real integration problem: Azure/Portkey rejects function-tool calls for this model over the Chat Completions API ("Function tools with reasoning_effort are not supported... use /v1/responses"). Fixed by routing `gpt-6`-series models through `OpenAIResponsesModel` (the Responses API) instead of `OpenAIChatModel`, while `gpt-5.6-luna` keeps using Chat Completions — both cached and selected by model name.
- The escalation decision happens in `main.py` *before* the agent runs (so the right model answers, rather than answering twice), and a `ChatDeps.escalated` flag tells the model itself it's running as the upgraded model this turn, so it can naturally confirm the switch instead of denying it can change models (an inconsistency caught and fixed during live testing).

**Verification (the user asked whether it's faster/better/stronger):** Confirmed `gpt-6-astra` is a genuinely available model on the account (not a typo/placeholder) via a direct Portkey call before wiring it in. Side-by-side on a trivial factual question, latency was comparable to `luna` (~2.3s vs ~2.5s) — not obviously faster. On a real store question ("Baseball Left Chest Crewneck in stock in XS?"), Astra's answer was *more precise*: it scoped its alternative suggestions specifically to other crewnecks that were in stock in that exact size, where Luna's default answer offered general alternatives without checking size-availability first.

**Why it helps Campus Customs shoppers:** For harder or more nuanced questions (comparisons, "what's a good gift," multi-constraint stock questions), a shopper can just say so in plain language and get a model that reasons more carefully, without needing to know or find a setting.

**Why it helps the business:** Keeping the inexpensive `gpt-5.6-luna` as the default for everyday Q&A controls routine model cost, while the stronger (likely pricier) model is only invoked when a shopper actually asks for it in conversation — better answers on high-consideration questions without paying for them on every single message, and without training shoppers to go looking for an "advanced mode" switch.

## Agent/Backend 2: Automatic price-accuracy guardrail with self-correcting retry

**What I added:** `backend/guardrails.py` scans every chat reply for dollar amounts and cross-checks each one against the real prices of the products the agent actually resolved that turn. If the model states a price that doesn't match anything real, `main.py` logs a warning and automatically retries the same question once with a corrective instruction telling the model to recheck via its tools rather than answer from memory. If the retry still doesn't check out, the shopper gets an honest "let me double-check that price" message instead of ever seeing a wrong number.

**Why it helps Campus Customs shoppers:** Problem 6 already established "lying to customers about price is bad" as a rule for the model to follow — this is the automated backstop behind that rule, so a shopper is protected even in the rare case the model doesn't follow its own instructions.

**Why it helps the business:** An AI misquoting a price is a real liability (price-dispute refunds, broken trust, screenshots on social media). Catching and auto-correcting this server-side, silently, means no one has to manually monitor every chat transcript for pricing mistakes.
