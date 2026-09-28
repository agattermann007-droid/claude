# Group D: which account models have NO consistency rule? For Traders, Lark Funding, Fintokei, Nordic Funder, PipFarm, Ment Funding, Funding Traders (fundingtraders.com), QT Funded

Research date: 2026-09-25. Use case: a fully automated MT5 Expert Advisor trading XAUUSD and NAS100 from a 24/7 Windows VPS.

**Source labels used below (important for the report writer):**
- **[official, snippet]**: the text comes from the firm's own domain, but I only saw it as a search-result snippet or AI search summary. **The page itself could not be opened** because the egress proxy blocked every firm domain.
- **[secondary, unverified]**: third-party review or aggregator site, seen only as a snippet. Treat as **unverified (secondary source)**.
- None of the pages could be opened (see section 0 Gaps), so **no fact below was read in its original page context**. Search summaries are machine-generated and can mix text from several result pages. Where attribution to a specific URL is uncertain, I say so.

---

## 0. Cross-firm overview: which models have no consistency rule, and what limited this research?

### Takeaway
The firms' own help/marketing text documents only a few models as free of a consistency rule:
- **Lark Funding** 1-Step and 3-Step. Lark states "no consistency rules" firm-wide. Instant Master has no % rule but has a $10,000 daily/per-trade gain cap.
- **Nordic Funder** standard 1-Step / 2-Step. There is no consistency rule to pass, and these models are not in its list of funded consistency caps.
- **Ment Funding** Forex accounts from $25K to $1M.
- **Funding Traders** 2-Step PRO6 / PRO10.
- **PipFarm** Classic Mode, as launched. A secondary source says a funded-side rule was later added to every mode.

Two firms drop out:
- **For Traders** is excluded for this use case because its help center forbids EAs that open or close trades autonomously.
- **Fintokei** has no model confirmed free of a consistency rule: StartTrader applies 40% in its evaluation phases, and funded ProTrader/SwiftTrader are subject to a 40% payout-cycle rule.

**QT Funded** has no clean "no-consistency" model confirmed. QT 2 Step Elite shows only a profitable-days requirement; Instant uses 25%; Prime on-demand payouts reportedly use 35%.

### Cited Findings
- See the firm sections 1–8 for every cited fact. This section only summarizes them. The overview table under Inferences is a synthesis of those cited findings.

### Inferences
Overview table. "Consistency" covers evaluation (E) and funded (F). "EA" means fully automated EA allowed. "?" means unknown.

| Firm | Model (status) | Consistency / profit-distribution rule | Automated EA? | MT5? | Section |
|---|---|---|---|---|---|
| For Traders | CLASSIC forex (ex-Two-Step; current) | No % rule found. Min. profitable days instead (3 per phase at 0.5%, 3 on Master) | **NO (autonomous EAs banned)** | Yes (not for US) | 1 |
| For Traders | Two-Step PRO forex | Yes: best day <15% (snippet) + "Daily Profit Cap" | NO | Yes | 1 |
| For Traders | STRIKE forex (ex-Three-Step) | Yes: a consistency-score article exists | NO | Yes | 1 |
| For Traders | INSTANT forex (NEW) | Yes, F: best day <15%, 7 profitable days | NO | Yes | 1 |
| For Traders | One-Step forex, INSTANT PRO forex | ? | NO | Yes | 1 |
| Lark Funding | 1-Step Evaluation | None (firm-wide claim) | Yes (no HFT/arbitrage) | MT4/MT5 via EightCap per FAQ (current status unverified) | 2 |
| Lark Funding | 3-Step Evaluation | None (firm-wide claim) | Yes | same | 2 |
| Lark Funding | Instant Master | No % rule, but $10,000 daily and/or per-trade gain limit | Yes | same | 2 |
| Lark Funding | 1-Step Career Evaluation | None stated. Max 1% loss per trade setup | Yes | same | 2 |
| Lark Funding | Lark Base (monthly subscription) | Consistency reportedly applies (secondary) | ? | ? | 2 |
| Lark Funding | 2-Step | Discontinued early 2026 (secondary) | – | – | 2 |
| Fintokei | StartTrader | Yes, E: max 40% of the phase profit target from one day, all 3 phases | Own EA only | MT4/MT5/cTrader | 3 |
| Fintokei | ProTrader (+ ProTrader Swing) | E: none found. F: 40% of payout-cycle profit per day (official FAQ; possibly discretionary) | Own EA only | Yes | 3 |
| Fintokei | SwiftTrader | Same as ProTrader | Own EA only | Yes | 3 |
| Nordic Funder | Standard 1-Step / 2-Step | E: none. F: none listed | Yes (own EAs, no approval) | ? | 4 |
| Nordic Funder | Lite | E: none. F: 50% | Yes | ? | 4 |
| Nordic Funder | Instant Funding | 20% | Yes | ? | 4 |
| Nordic Funder | Equities / Crypto | 20% / 25% (not forex/CFD-relevant) | – | – | 4 |
| PipFarm | Classic Mode | None to pass or for payout (launch post). Secondary: funded-side rule since added to all modes | ? | ? | 5 |
| PipFarm | Endurance Mode | ? | ? | ? | 5 |
| PipFarm | Consistency Mode | E+F: 50% (100k: 40%, 200k: 30%, 300k: 20%) | ? | ? | 5 |
| PipFarm | Instant Funding | 25% | ? | ? | 5 |
| PipFarm | Pay with Profits | ? | ? | ? | 5 |
| Ment Funding | Forex $25K–$1M | None | Yes (EAs and copiers; $1M cap per strategy/EA) | ? | 6 |
| Ment Funding | Funded > $1M | 35% before withdrawal | Yes | ? | 6 |
| Funding Traders | 2-Step PRO6 / PRO10 | None | ? | ? | 7 |
| Funding Traders | 1-Step PRO | F: 50% | ? | ? | 7 |
| Funding Traders | Instant | 15% (a 30% add-on exists) | ? | ? | 7 |
| Funding Traders | 2-Step Next-Gen | No longer available | – | – | 7 |
| QT Funded | QT Instant (current version?) | 25% at withdrawal | ? | ? | 8 |
| QT Funded | QT 2 Step Elite | No % found. Payout needs 4 min days + 2 days of +0.5% per cycle | ? | ? | 8 |
| QT Funded | QT Prime | On-demand payouts: 35% (secondary). Exposure caps | ? | ? | 8 |
| QT Funded | QT 1 Step (BNPL), QT Power | ? | ? | ? | 8 |
| QT Funded | QT 2 Step, QT Instant (Old) | Marked "Discontinued" | – | – | 8 |

Shortlist to verify first, for an MT5 EA on gold and NAS100 with no consistency rule:
1. Lark Funding 1-Step / 3-Step. Check that MT5 is still offered in 2026. VPS is "allowed but discouraged". Trades must be closed on Friday unless the weekend add-on is bought.
2. Nordic Funder standard 1-Step / 2-Step. EAs are explicitly allowed; the platform is unknown.
3. Ment Funding Forex ≤ $1M. EAs are allowed; the platform is unknown.
4. Funding Traders 2-Step PRO6 / PRO10. EA and platform policy are unknown.
5. PipFarm Classic. The funded-side rule and the platform are unknown.

### Gaps
- **Research was cut short by tooling.**
  - WebFetch was refused ("EGRESS_BLOCKED") for every domain tried: fundingtraders.com, nordicfunder.com, support.fintokei.com, www.larkfunding.com, www.fortraders.com, propfirmmatch.com, tradingfinder.com, tradetanto.com, lunefi.com, propnavi.io, h2tfunding.com, propvator.com, www.trustpilot.com and www.fxempire.com. curl to all firm and review domains also failed.
  - The session-wide WebSearch budget (200 calls, shared with the parallel researchers) ran out after this researcher's 40th query. This is why sections 4–8 lack platform, VPS, price and risk-rule details.
  - Follow-up would need a raised `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` or allow-listed domains.
- No page could be opened, so **no fact could be checked against a page date**. All "as of September 2026" statements rest on search results retrieved on 2026-09-25 plus undated help-center text.

---

## 1. For Traders (fortraders.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
For Traders is **not usable for a fully automated EA**. Its help center says EAs or bots that open, manage or close trades on their own are strictly prohibited; only assistive EAs (alerts, position sizing, order management under the trader's own decision) are allowed. Among the forex models, only **CLASSIC** (the renamed Two-Step Challenge) shows no consistency percentage in the snippets, and it has minimum-profitable-day rules instead. Two-Step PRO, STRIKE/Three-Step and the new INSTANT account all carry consistency or profit-cap rules.

### Cited Findings
**Automated trading / EA policy**
- "The use of EAs and Trading Bots that automatically trade on your behalf is strictly prohibited. The essence of the Trading Challenge is to evaluate your individual trading acumen, hence, the use of scripts or software that trade autonomously, without your direct input, is not allowed." [official, snippet] — [Use of Expert Advisors (EAs), For Traders Help](https://help.fortraders.com/en/articles/9259810-use-of-expert-advisors-eas)
- **Permitted:** EAs that alert you to opportunities, calculate position sizes, or manage orders according to your pre-set, manually reviewed parameters, where you remain the decision-maker. **Forbidden:** "Any tool, script, or software (including EAs) that enters, manages, or exits trades autonomously without your active decision at the time of execution." Also: "All trades must be managed manually." [official, snippet] — [What Is Forbidden With Us](https://help.fortraders.com/en/articles/15343227-what-is-forbidden-with-us)
- The same article prohibits:
  - arbitrage, both reverse and latency;
  - HFT: "all trades must be held for a minimum of 5 seconds";
  - grid trading;
  - tick scalping, i.e. "capturing micro-movements through automated rapid execution".

  [official, snippet] — [What Is Forbidden With Us](https://help.fortraders.com/en/articles/15343227-what-is-forbidden-with-us)

**Platforms**
- MetaTrader 5, cTrader and TradeLocker are offered on web, iOS, Android and desktop. "MT5 is available for everyone except the USA." [official, snippet] — [Trading Platforms | MetaTrader 5, cTrader & TradeLocker](https://fortraders.com/trading-platforms)

**Forex models listed in the help center (titles seen in search results)**
- "CLASSIC account | forex". It uses the same article ID (10401739) as "Two–Step Challenge FOREX". [official, snippet] — [CLASSIC account | forex](https://help.fortraders.com/en/articles/10401739-two-step-challenge-forex); [Two–Step Challenge FOREX](https://help.fortraders.com/en/articles/10401739-two-step-challenge-attributes)
- "Two-Step Challenge PRO FOREX", plus a separate article "What is the Daily Profit Cap? – Two-Step Challenge PRO". [official, snippet] — [Two-Step Challenge PRO FOREX](https://help.fortraders.com/en/articles/10401845-two-step-challenge-pro-forex); [What is the Daily Profit Cap?](https://help.fortraders.com/en/articles/9545913-what-is-the-daily-profit-cap-two-step-challenge-pro)
- "One-Step Challenge FOREX". [official, snippet] — [One-Step Challenge FOREX](https://help.fortraders.com/en/articles/10401651-one-step-challenge-forex)
- "STRIKE account | forex". It uses the same article ID (11401568) as "Three-Step Challenge FOREX". There is also an article "How does the Consistency Score on our Three-Step Account work?". [official, snippet] — [STRIKE account | forex](https://help.fortraders.com/en/articles/11401568-strike-account-forex); [Three-Step Challenge FOREX](https://help.fortraders.com/en/articles/11401568-three-step-challenge-forex); [Consistency Score Three-Step](https://help.fortraders.com/en/articles/11402218-how-does-the-consistency-score-on-our-three-step-account-work)
- "⚡️ NEW: INSTANT account | Forex" and "INSTANT PRO account | forex". The earlier instant product is now titled "not available: INSTANT account | forex" (formerly "Instant Master FOREX"). [official, snippet] — [NEW INSTANT account Forex](https://help.fortraders.com/en/articles/14635307-new-instant-account-forex); [INSTANT PRO account forex](https://help.fortraders.com/en/articles/11830305-instant-pro-account-forex); [not available: INSTANT account forex](https://help.fortraders.com/en/articles/10429449-not-available-instant-account-forex)
- The firm also runs futures and crypto accounts (INSTANT / FAST / FAST PRO futures, One-Step futures, crypto). These are out of scope. — [FAST PRO account | futures](https://help.fortraders.com/en/articles/14470847-fast-pro-account-futures)
- Homepage title: "For Traders | Prop Trading Firm | Funded Accounts up to $200K". — [For Traders](https://fortraders.com/)

**CLASSIC account forex (ex-Two-Step) rules.** [official, snippet; attributed to the CLASSIC / Two-Step article] — [CLASSIC account | forex](https://help.fortraders.com/en/articles/10401739-two-step-challenge-forex)
- Profit targets: Phase 1 is 8% or 10% depending on the order; Phase 2 is "around 5%".
- A "Profitable Day" is fixed at 0.5% of starting balance. You must trade at least three days in each phase to pass, and the Master Account has "3 minimum profitable days".
- Daily drawdown is −3% of the initial balance and "causes a pause only (not a violation)". Trading resumes the next day after 00:00 CET.
- Max drawdown is 10%, 8% or 6% (chosen at order), calculated from the initial balance (static). The same limit carries over to the Master Account.
- No time limit.

**Consistency / profit-distribution rules**
- PRO version: "the Consistency Rule applies: Your best trading day must be below 15% of your total profit." The search summary may have taken this sentence from the INSTANT article instead, so attribution is uncertain. The PRO also has a "Daily Profit Cap" whose value is unknown. [official, snippet] — [Two-Step Challenge PRO FOREX](https://help.fortraders.com/en/articles/10401845-two-step-challenge-pro-forex); [Daily Profit Cap](https://help.fortraders.com/en/articles/9545913-what-is-the-daily-profit-cap-two-step-challenge-pro)
- NEW INSTANT forex:
  - Consistency: best day must be below 15% of total profit; if it is 15% or more, keep trading. Formula: "Best Day Profit ÷ 0.15 = Minimum Required Total Profit".
  - Payout conditions: at least 7 profitable days (≥0.5% of starting balance); a 3% payout buffer (only profit above it can be withdrawn); maximum $15,000 per reward cycle.
  - No challenge phase, no profit target, no time limit.
  - The trailing max drawdown locks at the starting balance when a payout is requested.

  [official, snippet] — [NEW INSTANT account Forex](https://help.fortraders.com/en/articles/14635307-new-instant-account-forex); [Consistency Score on our Instant Account](https://help.fortraders.com/en/articles/10442201-how-does-the-consistency-score-on-our-instant-account-work)
- One fortraders.com result said "a 30% consistency rule — no single trading day can account for more than 30% of total profit" without naming a model. The source page could not be identified and may be generic blog content about the industry. [official, snippet; unreliable] — e.g. [Prop Trading Rules You Must Know](https://fortraders.com/blog/prop-trading-rules-you-must-know-before-taking-a-challenge)

**Sizes, split, price**
- Two-Step: $5,000–$200,000. Instant: $2,500–$100,000. "Traders keep 80% of their profits as a standard across all challenge types, with the option to upgrade to a 100% profit split for an additional fee." [official blog, snippet; exact page not identifiable] — [Top Prop Firms with Instant Funding (2026 Edition)](https://fortraders.com/blog/prop-firms-instant-funding)
- One summary said fees "start at just $17 for a $5,000 2-Step Challenge". The same summary also contained contradictory figures ("$6,000–$100,000", "fixed 15% profit split"), so **the price is unreliable**. — [fortraders.com blog](https://fortraders.com/blog/trading-challenges-start-weekend)

### Inferences
- The EA ban (autonomous entry and exit forbidden, "all trades must be managed manually") rules For Traders out for a 24/7 VPS EA, whatever the consistency rules. The 5-second minimum hold would also matter for any fast EA.
- CLASSIC (ex-Two-Step) is the only forex model with no consistency percentage in the snippets. It still has minimum-profitable-day requirements, and its −3% daily limit is a soft pause rather than a breach.
- The EA ban article (ID 15343227) and the NEW INSTANT article (ID 14635307) have much higher help-center IDs than the older 9–11 million articles. That suggests the current EA wording is recent (probably 2026), but no date was visible.

### Gaps
- VPS policy, whether XAUUSD/NAS100 are tradable, payout frequency and first-payout timing, and the 10k price: not found.
- Whether One-Step forex and INSTANT PRO forex are still sold, and their rules: unknown.
- The value of the Two-Step PRO "Daily Profit Cap": unknown.

---

## 2. Lark Funding (larkfunding.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
Lark Funding markets itself firm-wide as having "no consistency rules, no news restrictions and no minimum trading days". It allows EAs except HFT and arbitrage, and allows a VPS but "strongly discourages" it.
- Current lineup per secondary sources: **1-Step, 3-Step, Instant (Instant Master), and Lark Base** (monthly subscription). The **2-Step was discontinued in early 2026**.
- **1-Step and 3-Step have no consistency rule.**
- **Instant Master** has no % rule, but caps gains at **$10,000 per day and/or per trade**.
- **1-Step Career** has a 1% maximum loss per trade setup.
- **Consistency rules reportedly apply only to the monthly "Lark Base" model** (secondary).
- MT5 availability rests on an undated FAQ ("MT4 and MT5 … provided by EightCap"). It must be re-verified for 2026.

### Cited Findings
**Consistency / general**
- Programs have "no consistency rules, no news restrictions and no minimum trading days". "No consistency rules" is framed as trading your own way "with no hidden profit-distribution requirements". [official, snippet] — [Lark Funding homepage](https://larkfunding.com/); [Lark Funding FAQ](https://larkfunding.com/faq/)
- "There are absolutely ZERO hidden rules… if you don't see a rule, that's because it doesn't exist." [official, snippet] — [Lark Funding FAQ](https://larkfunding.com/faq/)
- "Consistency rules apply only to specific monthly base programs rather than every challenge." This is unverified (secondary source), from a search summary over luxalgo.com, thetrustedprop.com, pickmytrade.io and other review pages; the exact page is not identifiable. — [LuxAlgo Lark Funding](https://www.luxalgo.com/prop-firms/lark-funding/); [TheTrustedProp Lark Funding](https://thetrustedprop.com/prop-firms/lark-funding)

**Current models and status**
- Lineup: "Lark 1-Step, Lark 3-Step, and Lark Instant — plus the Lark Base, the first model by monthly subscription in the industry". Lark Base is "a monthly base reward paid to eligible traders even while they are in drawdown, with no fixed duration". [secondary, unverified] — [TheTrustedProp Lark Funding](https://thetrustedprop.com/prop-firms/lark-funding)
- "Lark Funding discontinued the 2-Step program in early 2026. Traders who had funded accounts on it got them closed after a four-month grace period" (all earnings reportedly paid out). [secondary, unverified] — [TheTrustedProp Lark Funding](https://thetrustedprop.com/prop-firms/lark-funding)
- Help-center model pages exist for:
  - 1-Step Career Evaluation (article 12853883, a newer ID);
  - 1-Step Evaluation (7169767);
  - 3-Step Evaluation (8251071);
  - 2-Step Evaluation (7969789, legacy);
  - Instant Master Account (10336809).

  A "1-Step Pro Landing Page" sits at /stock-trading/, apparently a stock product. [official, snippet] — [1-Step Career](https://helpdesk.larkfunding.com/en/articles/12853883-1-step-career-evaluation-details); [1-Step](https://helpdesk.larkfunding.com/en/articles/7169767-1-step-evaluation-details); [3-Step](https://helpdesk.larkfunding.com/en/articles/8251071-3-step-evaluation-details); [2-Step](https://helpdesk.larkfunding.com/en/articles/7969789-2-step-evaluation-details); [Instant Master](https://helpdesk.larkfunding.com/en/articles/10336809-instant-master-account-details); [1-Step Pro landing](https://larkfunding.com/stock-trading/)

**1-Step Evaluation (no consistency rule).** [official, snippet] — [1-Step Evaluation Details](https://helpdesk.larkfunding.com/en/articles/7169767-1-step-evaluation-details)
- Profit target 10%. It passes automatically when floating equity reaches the target.
- Daily loss limit: 5% of balance, calculated at 5:00 pm EST. It is a hard breach.
- Max loss: 6% of the initial account balance (static).
- A separate article, "How do you calculate the 7% Max Drawdown?", suggests an older or alternative 7% variant. — [7% Max Drawdown](https://helpdesk.larkfunding.com/en/articles/7173889-how-do-you-calculate-the-7-max-drawdown)

**3-Step Evaluation (no consistency rule).** [official, snippet] — [3-Step Evaluation Details](https://helpdesk.larkfunding.com/en/articles/8251071-3-step-evaluation-details)
- Targets: Phase 1 is 5%, Phase 2 is 4%, Phase 3 is 3%. It passes on floating equity.
- "There is no daily loss limit on the 3-Step Evaluation."
- Max loss limit: unknown.

**1-Step Career Evaluation.** [official, snippet; the summary may merge text from neighbouring articles] — [1-Step Career Evaluation Details](https://helpdesk.larkfunding.com/en/articles/12853883-1-step-career-evaluation-details)
- Target 10%.
- Daily loss 5% of balance at 5:00 pm EST (hard breach).
- "The maximum overall drawdown must remain better than −5%."
- "No individual trade setup may incur a loss greater than 1% of the account balance." This is a max-risk-per-trade rule.
- Rewards can be requested every 14 days, with a $40 processing fee.

**Instant Master Account.** [official, snippet] — [Instant Master Account Details](https://helpdesk.larkfunding.com/en/articles/10336809-instant-master-account-details)
- Daily loss: 5% of starting equity or balance each day, reset at 5:00 pm EST.
- Max loss: 8% of the highest recorded equity/balance, trailing on equity. It locks at the initial balance once the account has gained 8%.
- **"The daily and/or per-trade gain limit is set to $10,000."** This is a profit cap that works like a profit-distribution rule.
- Reward 90%. The first payout is on demand; after that, every 30 days, with a $100 minimum.

**Automation, VPS, copy trading, news, weekend**
- EAs are allowed "except those that are designed for HFT (high-frequency trading) or arbitrage trading". [official, snippet] — [Can I use an Expert Advisor?](https://helpdesk.larkfunding.com/en/articles/7174115-can-i-use-an-expert-advisor); the FAQ also allows EAs and trade copiers — [Lark Funding FAQ](https://larkfunding.com/faq/)
- VPS: Lark "strongly discourages" access via VPN or VPS but allows it. If suspicious activity is found, VPN/VPS use "will be a significant factor" in deciding whether the terms were violated. [official, snippet] — [Can I use a VPN?](https://helpdesk.larkfunding.com/en/articles/7174234-can-i-use-a-vpn)
- Copy-trading services are strictly prohibited (funded accounts rejected, permanent ban). Trade copiers are allowed, but each evaluation must be passed individually. [official, snippet] — [Can I use a trade copier?](https://helpdesk.larkfunding.com/en/articles/7177023-can-i-use-a-trade-copier)
- No news restrictions. [official, snippet] — [Can I trade during news events?](https://helpdesk.larkfunding.com/en/articles/7174111-can-i-trade-during-news-events)
- Weekend: holding over the weekend costs an extra 10% of the challenge fee. Otherwise "all trades must be closed by 3:45 pm EST on Friday". [official, snippet; the exact article within the collection is not identifiable] — [Trading Rules collection](https://helpdesk.larkfunding.com/en/collections/3916922-trading-rules)

**Platforms**
- "Lark Funding's technology management is currently integrated with the MT4 and MT5 platforms… provided by their broker, EightCap." Traders choose a platform at sign-up "subject to availability", and once funded can use TradingView if they are on MT5. This is **undated and may be outdated**. [official, snippet] — [Lark Funding FAQ](https://larkfunding.com/faq/)
- The help center has a separate "Trading Platforms" collection whose contents were not visible. All trading is simulated using demo accounts with third-party liquidity providers. [official, snippet] — [Trading Platforms collection](https://helpdesk.larkfunding.com/en/collections/13860422-trading-platforms); [Who is the counterparty to my trades?](https://helpdesk.larkfunding.com/en/articles/8377872-who-is-the-counterparty-to-my-trades)

### Inferences
- For an MT5 EA with no consistency rule, the best candidates are the **1-Step** (10% target, 5% balance-based daily at 5 pm EST, 6% static max) and the **3-Step** (5/4/3% targets, no daily limit).
- The EA would have to close positions before Friday 3:45 pm EST unless the +10% weekend add-on is bought.
- VPS use is permitted but is treated as a risk factor in investigations. Keep the same IP and no shared VPS.
- Instant Master's $10,000 daily/per-trade gain cap and 8% trailing drawdown make it less attractive for a gold/NAS100 EA with occasional large winners.
- 1-Step Career's 1% maximum loss per trade setup would need to match the EA's stop sizing.

### Gaps
- Whether MT5 (EightCap) is still the platform in 2026, or has been replaced (e.g., by Match-Trader, cTrader or TradeLocker): **unknown**. The platform collection could not be read.
- XAUUSD / NAS100 availability: an article "What markets and symbols can I trade?" exists but its content was not retrieved — [link](https://helpdesk.larkfunding.com/en/articles/7210469-what-markets-and-symbols-can-i-trade)
- Payout timing and split for 1-Step and 3-Step (general "How do payouts work?" article not retrieved — [link](https://helpdesk.larkfunding.com/en/articles/8117403-how-do-payouts-work)), the 3-Step max loss, prices (10k), and the exact Lark Base consistency percentage: unknown.

---

## 3. Fintokei (fintokei.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
**No Fintokei model can be confirmed as free of a consistency rule.**
- **StartTrader** has a 40% consistency rule by default in all phases: no more than 40% of the phase profit target may come from one day.
- **ProTrader** and **SwiftTrader** show no consistency rule in evaluation. On the virtually funded account, however, Fintokei's FAQ says no more than 40% of the payout-cycle profit may come from one trading day. Secondary sources describe this as applied case by case at the risk team's discretion; the conflict is unresolved.

MT5 is available on all plans, alongside MT4 and cTrader. Own EAs are allowed; unmodified purchased or third-party EAs are not. A personal, unshared VPS is allowed.

### Cited Findings
**Consistency rules**
- StartTrader: "consistency rules applied by default on all accounts of StartTrader with a maximum daily profit monitored for each Challenge phase". In Phases 1, 2 and 3, at most 40% of the profit target can come from one day. [official, snippet] — [How does StartTrader evaluation work?](https://support.fintokei.com/en/articles/9579997-how-does-starttrader-evaluation-work-what-are-the-rules)
- ProTrader / SwiftTrader funded: "To be eligible to request a payout, no more than 40% of the total profit during the payout cycle can come from 1 trading day on a virtually funded ProTrader or SwiftTrader account."
  - Missing the rule does not breach the account, but the payout is not processed until total profit is large enough.
  - Example: $4,500 best day on $10,000 total → need $12,000 total.
  - The rule resets after every approved payout.

  [official, snippet] — [Consistency Rules – Most common application](https://support.fintokei.com/en/articles/11315966-consistency-rules-most-common-application)
- The same FAQ area says consistency rules are applied more broadly when traders show irresponsible patterns, such as repeated breaches from high-risk behaviour or flagged unsustainable trading. [official, snippet] — [Other restrictions that may be part of Consistency rules](https://support.fintokei.com/en/articles/11315971-other-restrictions-that-may-be-part-of-consistency-rules)
- Conflicting secondary view: "StartTrader plans add a consistency rule capping any single day at 40% of the phase profit target, while SwiftTrader and ProTrader skip this rule but require higher overall profit targets. However, Fintokei applies consistency restrictions case-by-case, at their risk team's discretion." [secondary, unverified] — [Lune Fintokei review](https://lunefi.com/blog/fintokei-an-in-depth-guide-rules-review-and-discount); [DealPropFirm Fintokei](https://dealpropfirm.com/prop-firms/fintokei)
- One search summary claimed ProTrader and SwiftTrader have a "(phase I • II • III)" 40%-of-target rule that "is turned off" after phase 3. ProTrader has only two phases (8% / 6%), so this looks like **StartTrader text wrongly attributed**. Treat it as unreliable. — [Which Fintokei challenge should you choose?](https://www.fintokei.com/blog/which-fintokei-challenge-should-you-choose/)

**ProTrader rules.** [official, snippet] — [How does ProTrader evaluation work?](https://support.fintokei.com/en/articles/6538822-how-does-protrader-evaluation-work-what-are-the-rules); [How are the Daily loss limit and Maximum Loss limit calculated?](https://support.fintokei.com/en/articles/6538826-how-are-the-daily-loss-limit-and-maximum-loss-limit-calculated)
- Targets: 8% in Phase 1, 6% in Phase 2.
- Daily loss −5%. A snapshot of end-of-day equity is taken every day at midnight (UTC+0), and equity may not fall more than 5% below it during the next 24 hours. This is equity-based and relative to the EOD equity snapshot.
- Max loss −10% of starting capital, static and equity-based (e.g. equity may never go below 90,000 on a 100k account).
- A breach is immediate.
- A "ProTrader Swing" variant exists. [official, snippet] — [ProTrader vs ProTrader Swing](https://support.fintokei.com/en/articles/12058210-what-is-the-difference-between-protrader-and-protrader-swing)
- SwiftTrader rules article exists; its content was not retrieved. — [How does SwiftTrader evaluation work?](https://support.fintokei.com/en/articles/12040973-how-does-swifttrader-evaluation-work-what-are-the-rules)
- Minimum trading days: "What does the rule 'Minimum trading days' mean? (3 or 5 days)". [official, title only] — [link](https://support.fintokei.com/en/articles/8428030-what-does-the-rule-minimum-trading-days-mean-3-or-5-days)

**EA / VPS policy.** [official, snippet] — [Copy trading and EAs – what is allowed and what prohibited?](https://support.fintokei.com/en/articles/10419735-copy-trading-and-eas-what-is-allowed-and-what-prohibited); [Can I use automated trading through EAs?](https://support.fintokei.com/en/articles/6538838-can-i-use-automated-trading-through-eas); [Sharing 1 electronic device](https://support.fintokei.com/en/articles/11316015-what-is-the-definition-of-sharing-1-electronic-device-used-for-trading-between-multiple-customers)
- **Allowed:**
  - your own EA, "fully created and configured by you";
  - commercial or free EAs customized "with your own parameters and your own individual setting — as long as the logic is yours and transparent";
  - "Standard EAs".
- **Prohibited:**
  - buying or copying commercial EAs or signal packages made by someone else "without any individual setting or interference from your side";
  - free public bots or black-box systems;
  - systems where you just follow third-party signals;
  - robots designed to pass a challenge;
  - HFT robots.
- **VPS:** "Using a personal VPS is allowed — but not if it's shared by other traders"; "Occasional travel or using your own VPS is fine, as long as your activity remains consistent and transparent."

**Platforms**
- MT4, MT5 and cTrader are available on all account types (Standard, ProTrader, SwiftTrader) "with no difference in pricing, leverage, or trading conditions". TradingView works only with cTrader accounts. [official, snippet] — [What trading platforms do you offer?](https://support.fintokei.com/en/articles/6538834-what-trading-platforms-do-you-offer); [How can I trade on TradingView with Fintokei?](https://support.fintokei.com/en/articles/12688210-how-can-i-trade-on-tradingview-with-fintokei); [MT5 Trading Challenge page](https://www.fintokei.com/metatrader-5/)

### Inferences
- For a trader who wants no consistency rule at all, Fintokei does not qualify. The most favourable option is ProTrader or SwiftTrader, which have no evaluation rule found but a 40% payout-cycle rule on the funded side (default or discretionary, unresolved). StartTrader is clearly excluded.
- A self-written or self-configured MT5 EA on a personal VPS fits Fintokei's EA policy. An off-the-shelf EA run with default settings does not.

### Gaps
- Payout timing and frequency, profit split, minimum payout, and 10k price for ProTrader and SwiftTrader: not found.
- SwiftTrader's targets and drawdowns, StartTrader's funded-phase consistency: not retrieved.
- XAUUSD and NAS100 availability: not found.
- Whether the funded 40% rule is default or discretionary for ProTrader/SwiftTrader: unresolved conflict.

---

## 4. Nordic Funder (nordicfunder.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
Nordic Funder's own pages say there are no consistency rules and no minimum trading days to pass its assessment, and that own EAs are allowed on every account without approval or surcharge. Its funded-side consistency caps are listed only for crypto (25%), equities and instant funding (20%), and funded Lite accounts (50%). The **standard forex 1-Step and 2-Step therefore appear to have no consistency rule in either phase**; this is an inference, because the funded side is not explicitly confirmed. Platform, VPS policy, drawdown figures, payouts and prices could not be retrieved before the search budget ran out.

### Cited Findings
- Homepage title: "Nordic Funder — Funded Trading Accounts up to $500K | 1-Step, 2-Step & Instant Funding". [official, snippet] — [Nordic Funder](https://nordicfunder.com/)
- "Your own EAs and algorithms are allowed on every account, with no approval step and no surcharge." [official, snippet; probably the FAQ] — [FAQ — rules, fees, payouts & platforms](http://nordicfunder.com/faq/)
- Nordic Funder "allows trading with expert advisors or copying from your other accounts or preferred platforms". [official, snippet] — [A guide to the Nordic Funder program rules](https://nordicfunder.com/funded-trader-program-rules/)
- "There are no other obstacles like minimum trading days or consistency rules to pass the assessment." Also "Nordic Funder does not have requirements like strict rules on scalping or consistency requirements." The second sentence may come from an older comparison page, "MyForexFunds vs Nordic Funder". [official, snippet] — [Program rules](https://nordicfunder.com/funded-trader-program-rules/); [MyForexFunds vs Nordic Funder](https://nordicfunder.com/myforexfunds-vs-nordic-funder/)
- "Lite accounts have no consistency requirement during the evaluation itself." Consistency "caps how much of your total profit can come from a single day… at 25% on crypto, 20% on equities and instant funding, and 50% on funded Lite accounts." [official, snippet; probably the FAQ] — [FAQ](http://nordicfunder.com/faq/)
- Other official pages that exist but whose content was not seen: [Prohibited Trading Practices](https://nordicfunder.com/prohibited-trading-practices/), [Funded Trader Accounts](https://nordicfunder.com/accounts/), [Profit share and payouts](https://nordicfunder.com/how-to-withdraw-profits-prop-firm/), [Terms](https://nordicfunder.com/terms/), [How it works](https://nordicfunder.com/how-it-works/).
- Secondary sources:
  - Title "Nordic Funder Rules 2026 – 30 Days Payouts Available". — [TradingFinder Nordic Funder rules](https://tradingfinder.com/props/nordic-funder/rules/)
  - Title "Get Up to $1 Million Funding", which conflicts with the homepage's "up to $500K". — [TradingFinder Nordic Funder](https://tradingfinder.com/props/nordic-funder/)
  - "no monthly fees and full support for scalping". — search summary over the same results.

  All [secondary, unverified].

### Inferences
- Model classification:
  - **Standard 1-Step and 2-Step** (forex/CFD): no consistency rule to pass, and not among the listed funded caps. Most likely no consistency rule at all, but this needs confirmation.
  - **Lite:** none in evaluation, 50% when funded.
  - **Instant funding:** 20%.
  - **Equities / crypto:** 20% / 25% (not relevant).
- The EA policy (own EAs on every account, no approval, no surcharge) is the most EA-friendly wording in this group.

### Gaps
- **Platforms (is MT5 offered?), VPS policy, XAUUSD/NAS100, profit targets, daily loss (% and basis), max loss type, news and weekend rules, payout timing/split/minimum, and the 10k price: all unknown** because the domain and aggregators were blocked and the search budget ran out.
- Whether the "Lite" line and the 20% Instant cap are current as of September 2026: undated.

---

## 5. PipFarm (pipfarm.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
PipFarm runs three challenge "modes": Classic, Endurance and Consistency, plus Instant Funding, and its help center also documents a "Pay with Profits" model.
- **Classic Mode**, as announced, requires **no consistency score and no profitable days** to pass or to qualify for a payout, only a trading-day requirement.
- **Consistency Mode** uses a 50% score, tightened to 40%, 30% and 20% for 100k, 200k and 300k accounts.
- **Instant Funding** uses 25%.
- A secondary source claims PipFarm "recently added a funded-side rule to every one of its modes". If true, Classic now has a consistency rule on the funded side. This is **unresolved**.
- Platform, EA and VPS policy were not retrieved.

### Cited Findings
- Three modes were announced:
  - **Consistency Mode** "introduces a consistency score as a passing and payout requirement". The most profitable day may not exceed 50% of total profit "for each stage and between payouts". 100k accounts need a 40% score, 200k need 30%, 300k need 20%.
  - **Endurance Mode** is "our most popular challenge, designed for traders who think long-term and seek an incredible scaling opportunity".
  - **Classic Mode** is "a step back to our original rules with a simple Trading Day requirement (no consistency score or profitable days required) to pass a challenge or qualify for a payout."

  [official, snippet] — [We're launching three new modes: Classic, Endurance and Consistency](https://pipfarm.com/were-launching-three-new-modes-classic-endurance-and-consistency/)
- Instant Funding: "If your most profitable day accounts for more than 25% of your total profits, you must keep trading before you qualify for a payout. Once your balance increases by 3% and your consistency score is 25% or less, your payout will be processed automatically next Friday." [official, snippet] — [Meet the PipFarm Instant Funding Program](https://pipfarm.com/instant-funding-launch/)
- Other official pages found, content not seen:
  - [Pay with Profits — Overview](https://help.pipfarm.com/articles/4035678-pay-with-profits-overview) and [Pay with Profits — Risk Tiers](https://help.pipfarm.com/articles/6346904-pay-with-profits-risk-tiers);
  - [Redefining PipFarm and rewarding consistency](https://pipfarm.com/blog/redefining-pipfarm-and-rewarding-consistency);
  - [July 2025 Updates](https://pipfarm.com/july-2025-updates/);
  - [Making your payouts simpler and smoother](https://pipfarm.com/making-your-payouts-simpler-and-smoother/);
  - [PipFarm rule guide](https://pipfarm.com/pipfarm-rule-guide);
  - [FAQ](https://pipfarm.com/faq/).
- "PipFarm recently added a funded-side rule to every one of its modes." [secondary, unverified] — [TradeTanto: Prop Firm Consistency Rules Compared](https://tradetanto.com/learn/prop-firm-consistency)
- "Consistency rules vary by account size (≤20% for $300k), and profits from gaps (caused by news) larger than 0.2% are deducted"; also "PipFarm requires a Consistency Score of 50% for challenges and 25% for instant funding". [secondary, unverified] — [TradeTanto PipFarm rules](https://tradetanto.com/learn/pipfarm-rules)
- Title "PipFarm Rules 2026 – Hedging Only for 1 Account". [secondary, unverified] — [TradingFinder PipFarm rules](https://tradingfinder.com/props/pipfarm/rules/)

### Inferences
- **Classic Mode** is the only PipFarm candidate without a consistency rule, and only if the secondary claim that a funded-side rule now applies to every mode is wrong or does not cover Classic.
- The rule that deducts profits from news gaps larger than 0.2%, if still current, is a profit-distribution rule that matters for NAS100 and gold around news and session gaps.

### Gaps
- The dates of the modes launch and of the funded-side rule change; whether Classic and Endurance are still sold in September 2026: unknown.
- **Platform (MT5 or not), EA and VPS policy, XAUUSD/NAS100, targets, daily and max loss, payouts, prices, and the Pay with Profits rules: all unknown** (blocked, and search budget exhausted).

---

## 6. Ment Funding (mentfunding.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
Ment Funding's own site says its **Forex accounts from $25K to $1M have no consistency rule**. **Funded accounts with a starting balance above $1M** must meet a **35% consistency requirement** before withdrawal. EAs, trade copiers, scripts and indicators are allowed, with a **$1M total funding cap per strategy/EA**, aimed at off-the-shelf market EAs. Platform, VPS policy and the risk rules were not retrieved.

### Cited Findings
- "No consistency rule" on Forex accounts "from $25K to $1M – traders can trade freely". "Funded Accounts with a starting balance greater than $1 million are subject to a 35% Consistency Requirement, which must be met before a withdrawal can be requested." [official, snippet] — [Ment Funding Forex](https://mentfunding.com/mentfunding-fx/); [Terms and Conditions](https://mentfunding.com/terms-and-conditions/)
- EAs, Copy Traders, Scripts and Indicators are allowed. "$1 million max per strategy/EA (can be made up of multiple assessments, provided none are the same size at the same time)". This applies to "'off-shelf' EAs purchased from the market and used by many, as they seek to fund independent and unique strategies". [official, snippet] — [Terms and Conditions](https://mentfunding.com/terms-and-conditions/); [Ment Funding](https://mentfunding.com/)
- Homepage tagline: "Ment Funding – Funded. No time limits." [official, snippet] — [Ment Funding](https://mentfunding.com/)
- Secondary claims:
  - "No single trading day can be more than 33% of your total profit" as another consistency-related metric across Ment Funding accounts. This **conflicts** with the official "no consistency rule" and may refer to futures or to a specific product.
  - The >$1M rule was described as "no single trade can be accountable for more than 35% of the total account balance", wording that looks garbled.

  [secondary, unverified] — [TradingFinder Ment Funding (Aug 2026)](https://tradingfinder.com/props/ment-funding/); [TheTrustedProp Ment Funding](https://thetrustedprop.com/prop-firms/ment-funding)
- Futures: 3 months to complete, with a 25% consistency requirement. Out of scope. [secondary, unverified] — [H2T Funding Ment review](https://h2tfunding.com/reviews/ment-funding/)
- Titles: "Ment Funding Review August 2026 – Scaling Up to $5M" and "Fast 1-Step Funding Up To $5M". [secondary, unverified] — [TradingFinder](https://tradingfinder.com/props/ment-funding/); [H2T Funding](https://h2tfunding.com/reviews/ment-funding/)

### Inferences
- The Forex challenge at $25K–$1M is a no-consistency candidate. The smallest Forex size seen is $25K, so a 10k account may not exist.
- The $1M-per-EA cap only matters when scaling, and seems aimed at commercial EAs. A self-developed EA probably falls outside the "off-shelf" concern, but this is not confirmed.

### Gaps
- **Platform (MT5?), VPS policy, XAUUSD/NAS100, profit target(s), daily and max loss (type), minimum days, news and weekend rules, payout timing/split/minimum, and the price of the smallest ($25K) account: unknown.**
- The number of phases in the Forex challenge (secondary sources say "1-Step"): unverified.
- The conflict between "no consistency rule" (official) and "no day > 33%" (secondary): unresolved.

---

## 7. Funding Traders (fundingtraders.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
Funding Traders' own blog says **2-Step PRO6 and 2-Step PRO10 have no consistency score requirement**. **1-Step PRO** applies a **50%** best-day rule on funded accounts, and **Instant** applies **15%**; an optional 30% consistency add-on also exists. Funding Traders treats consistency as a payout-eligibility test, never a breach. 2-Step Next-Gen is "no longer available". Platform, EA and VPS policy and the 2-Step PRO risk parameters were not retrieved.

### Cited Findings
- A consistency rule "limits the share of your total profits that may come from your best single day. It is a payout eligibility test, not a pass condition for an evaluation, and it does not fail your account."
  - Thresholds: "15% on Instant Accounts and 50% on 1-Step PRO funded accounts."
  - "2-Step PRO6 and 2-Step PRO10 accounts do not have a consistency score requirement."
  - Formula: Consistency Score = (Highest Trading Day Profit / Total Trading Days PNL) × 100.

  [official, snippet] — [Your Best Day vs Your Total Profits (Funding Traders blog)](https://fundingtraders.com/blog/prop-firm-consistency-rules)
- Instant Account: "immediate access to capital with no challenge and a higher default Reward Share (90%), but tighter rules — including no news trading, a 15% consistency score, a 3% non-withdrawable safety cushion, and payouts every 14 days." [official, snippet] — [Funding Traders blog](https://fundingtraders.com/blog/prop-firm-consistency-rules)
- Help-center pages:
  - "2-Step Pro" — [link](https://fundingtraders.com/help/en/articles/13399206-2-step-pro)
  - "1-Step Pro" — [link](https://fundingtraders.com/help/en/articles/13615032-1-step-pro); older copy [link](https://help.fundingtraders.com/en/articles/11967220-1-step-pro)
  - "30% Consistency Score Add-On" — [link](https://help.fundingtraders.com/en/articles/11514818-30-consistency-score-add-on)
  - "2-Step Next-Gen (No longer available)" — [link](https://help.fundingtraders.com/en/articles/12130845-2-step-next-gen-no-longer-available)

  [official, titles/snippets]
- Blog post "What's New With FundingTraders: Challenge Convert, FT Points, and Four Countries Reopened" (content not seen). — [link](https://fundingtraders.com/blog/whats-new-with-fundingtraders-challenge-convert-ft-points-and-four-countries-reopened)
- Withdrawal policy page exists (content not seen). — [Withdrawal Policy](https://fundingtraders.com/withdrawal)

### Inferences
- **2-Step PRO6 and 2-Step PRO10** are this firm's no-consistency models. "6" and "10" probably refer to max-drawdown or target variants, but that is not confirmed.
- Instant (15%, no news trading) and 1-Step PRO (50% on the funded side) are excluded under the "no consistency" criterion.

### Gaps
- **Platforms (MT5?), EA and VPS policy, XAUUSD/NAS100, 2-Step PRO6/PRO10 targets, daily and max loss (type), minimum days, news and weekend rules, payout timing/split/minimum, and the 10k price: unknown** (fundingtraders.com blocked, search budget exhausted).

---

## 8. QT Funded (qtfunded.com): models, consistency rules, EA/VPS/MT5 facts

### Takeaway
QT Funded's help center lists several products:
- **QT Instant Funded:** 25% consistency at withdrawal.
- **QT 2 Step Elite:** payout needs 4 minimum days and at least 2 days of +0.5% per cycle. No % consistency rule was found; this profitable-day rule is not a percentage cap.
- **QT 1 Step (BNPL)** and **QT Prime:** QT Prime has exposure caps; reportedly its "on-demand" payouts need a 35% consistency score.
- **QT Power:** no details found.
- **Discontinued:** QT 2 Step and QT Instant (Old).

No QT model could be confirmed as having no consistency rule, and platform, EA and VPS policy were not retrieved.

### Cited Findings
- QT Instant Funded: "no single trading day's profit can exceed 25% of total profits at withdrawal time". The same help-article ID also appears under the title "QT Instant Funded (Old) – Discontinued", so it is **unclear whether the 25% rule belongs to the old or the current Instant product**. [official, snippet] — [QT Instant Funded](https://support.qtfunded.com/hc/en-gb/articles/5613494245663-QT-Instant-Funded); [QT Instant Funded (Old) – Discontinued](https://support.qtfunded.com/support/articles/5613494245663-qt-instant-funded-old-discontinued)
- Exposure Rule: "For Prime Evaluation, traders should not exceed 75% of daily drawdown in total exposure; for Prime Funded, the maximum is 2.5% of initial balance exposed at once." [official, snippet] — [Exposure Rule](https://support.qtfunded.com/hc/en-gb/articles/5613590674847-Exposure-Rule)
- QT 2 Step / QT 2 Step Elite: "Traders must complete 4 minimum days and at least 2 days of +0.5% per cycle to be eligible to request a payout." One URL titles the QT 2 Step article "QT 2 Step – Discontinued". [official, snippet] — [QT 2 Step](https://support.qtfunded.com/support/articles/5613390200863-qt-2-step); [QT 2 Step – Discontinued](https://support.qtfunded.com/hc/en-gb/articles/5613390200863-QT-2-Step); [QT 2 Step Elite](https://support.qtfunded.com/support/articles/5613474746783-qt-2-step-elite)
- "QT 1 Step (BNPL)" article exists (content not seen). — [QT 1 Step (BNPL)](https://support.qtfunded.com/support/articles/5632217156767-qt-1-step-bnpl)
- Secondary claims, which contradict each other on the split (80% vs 100%):
  - "QT Funded applies a 35% consistency rule for payouts on demand at 80% split";
  - "QT Prime On-Demand pays 100% profit split to traders who meet a 35% consistency score and a 3% minimum profit threshold";
  - QT Instant also needs "a minimum of 5 separate trading days".

  [secondary, unverified] — [FundedTrading QT Prime rules](https://fundedtrading.com/qt-prime-trading-challenge-rules/); [MyForexFirms QT Funded review 2026](https://www.myforexfirms.com/blogs/qt-funded-review-2026); [Lune QT Funded](https://lunefi.com/blog/qt-funded-an-in-depth-guide-rules-review-and-discount)
- A news item, "QT Funded Announces Key Updates to Trading Rules and Payout Requirements", exists (content and date not seen). [secondary] — [TheGodFunded news](https://thegodfunded.com/en/news/qt-funded-announces-key-updates-to-trading-rules-and-payout-requirements/)

### Inferences
- QT 2 Step Elite may be the closest QT model to "no consistency rule", since only a profitable-days rule was found, if it is still sold.
- QT Prime's funded exposure cap (at most 2.5% of initial balance open at once) acts as a hard max-risk rule. It would constrain an EA that stacks positions on gold and NAS100 at the same time.
- The 35% rule seems tied to the on-demand payout option rather than the whole Prime model. A standard-cycle Prime payout might carry no consistency rule, but this is unconfirmed.

### Gaps
- The current product list as of September 2026 (is QT Power still sold? which Instant version is current?): unknown.
- **Platforms (MT5?), EA and VPS policy, XAUUSD/NAS100, targets, daily and max loss (type), payouts, and prices: unknown** (support.qtfunded.com not openable, search budget exhausted).
