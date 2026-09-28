# Group A: which FTMO, The5ers, FundedNext, Funding Pips, E8 Markets and FXIFY models have no consistency rule (target date: September 2026), and what an MT5 EA trader (XAUUSD + NAS100, 24/7 VPS) needs to know about them

> **Source-access note (read first).** The egress proxy blocked WebFetch/curl for every official domain (ftmo.com, the5ers.com, fundednext.com / help.fundednext.com, fundingpips.com, e8markets.com, fxify.com). It also blocked every review site tried (propvator, proptradingvibes, tradetanto, fxempire, newyorkcityservers, …) and search/archive mirrors (bing, duckduckgo, web.archive.org, reddit). **No official page could be opened.** The session-wide WebSearch budget (200 calls) ran out partway through this research. The remaining facts come from GitHub code search of a public third-party repository, `vedkanani123/rules`. Every citation carries one of these labels:
> - **[OFF-SNIP]**: official firm page, seen only as a web-search snippet or summary. The page was not opened and the wording is unverified.
> - **[OFF-MIRROR]**: text of an official firm page as mirrored in a third-party GitHub crawl (`vedkanani123/rules`). The crawl date is unknown; the latest file date in the repo is 2026-09-08, and some pages carry a "© 2026" footer. Status: unverified (secondary copy).
> - **[DOSSIER]**: firm dossier in the same repo, compiled by an AI agent. The batch README says "Generated: 2026-09-08". The dossiers cite official pages plus aggregators such as PropDataLab, PropFirmMatch, Lune and QuantVPS. Status: **unverified (secondary source)**.
> - **[SEC-SNIP]**: third-party review or aggregator page, seen only via a search snippet or summary. Status: **unverified (secondary source)**.
>
> Search summaries sometimes merge several result pages. Where a claim could not be tied to a single page, all candidate pages are cited.
>
> Repo permalink base: `https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/`. Batch date: [README_STATUS](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/README_STATUS.txt).

---

## 1. Which account models are offered (Sept 2026), and which carry a consistency, best-day or similar profit-distribution rule?

### Takeaway
These models have **no consistency or best-day rule in either the evaluation or the funded phase**, in their standard configuration:
- **FTMO:** 2-Step Challenge, both Standard and Swing.
- **The5ers:** High Stakes, Hyper Growth, Pro Growth and Bootcamp. No rule was found, but some programs require a minimum number of profitable days.
- **FundedNext:** Stellar 2-Step, Stellar 1-Step and Stellar Lite (only **without** the On-Demand Rewards add-on), plus Stellar Instant. Two related rules apply to all four: a "Max Risk 3%" rule, and only 40% of news profits counting.
- **Funding Pips:** evaluations are consistency-free on every model. The funded Master is consistency-free only on the **Weekly or Bi-weekly** reward cycles. That covers 2-Step Standard (Weekly or Bi-weekly), 2-Step Flex (85% or 95% Bi-weekly), 2-Step Pro (Weekly) and, apparently, 1-Step Flex. It excludes the On-Demand cycle, the Monthly cycle for Masters bought on/after 2026-08-15, and Zero.
- **E8 Markets:** only E8 Pro and the new E8 Zero Forex (launched Jul 2026) have no funded best-day rule listed, and this is not explicitly confirmed. All other E8 forex models have a 35–40% funded best-day rule.
- **FXIFY:** Two-Phase Standard (trailing) and Three-Phase. Instant Funding Standard is also consistency-free but bans EAs. One-Phase is **disputed** between sources.

### Cited Findings

#### FTMO
- The CFD line-up is FTMO Challenge 1-Step and 2-Step, both one-time fee. FTMO Futures Beta (Growth/Pro, monthly subscription) is a separate futures product and out of scope. US clients are served through the affiliated site ftmo.oanda.com. — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)
- FTMO FAQ, "Do you have any consistency rules?": "Provided you maintain sustainable risk management practices, there are no additional consistency requirements for your trading." It adds that consistency is judged through the Trading Objectives (Minimum Trading Days, Best Day Rule). — [OFF-SNIP FTMO FAQ](https://ftmo.com/en/faq/do-you-have-any-consistency-rules/)
- In the dossier's model table, both "FTMO Challenge 2-Step … Consistency: none" and the "2-Step Swing variant … none" appear. — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt); consistent with "The FTMO 2-Step Challenge has no consistency rule at all" in a search summary of [SEC-SNIP Propvator](https://propvator.com/blog/does-ftmo-have-a-consistency-rule/) and [SEC-SNIP FreeTraderHub](https://freetraderhub.com/blog/ftmo-consistency-rule-explained/)
- **1-Step Best Day Rule (50%):** "no single trading day should reach more than 50% of your Positive Days' Profit". Exceeding it "is not considered a rule breach": the trader keeps trading until the ratio drops below 50%. — [OFF-SNIP FTMO FAQ (AU)](https://ftmo.com/au/faq/how-does-the-best-day-rule-50-work-in-ftmo-challenge-1-step/); [OFF-SNIP Trading Objectives](https://ftmo.com/en/trading-objectives/)
- The 1-Step Best Day Rule applies in **both the Challenge and the funded FTMO Account**. Dossier wording: "Best-Day Rule (Challenge + FTMO Account) … NOT a breach … Shown in Account MetriX". — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt); a search summary also says "it applies in both the evaluation and funded phases" ([SEC-SNIP FreeTraderHub](https://freetraderhub.com/blog/ftmo-consistency-rule-explained/), [SEC-SNIP MyForexFirms](https://myforexfirms.com/blogs/ftmo-review-2026-drawdown-rules-consistency-rule-honest-verdict))
- **Soft, lot-size-consistency-like rule (all FTMO accounts):** the trading style must be replicable on live accounts. "Market standard risk management rules include avoiding opening substantially larger position sizes or a substantially smaller/larger number of positions compared to your other simulated trades." — [OFF-SNIP FTMO FAQ "Trading according to a real market"](https://ftmo.com/en/faq/what-is-trading-according-to-a-real-market/). Gambling and account-rolling are also forbidden. — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)
- **1-Step launch date is disputed:** one search summary says "launched in February 2026", another source says late 2025. — [SEC-SNIP TheTrustedProp](https://thetrustedprop.com/blogs/ftmo-1-step-challenge-simply-explained), [SEC-SNIP Tradetanto](https://tradetanto.com/learn/ftmo-rules-evaluation-process), [SEC-SNIP PropFirmPaid](https://propfirmpaid.com/blog/ftmo-review-2026-updated-rules-pricing)

#### The5ers (The 5%ers)
- The line-up is "FOUR CFD programs (Hyper Growth 1-step, Pro Growth 1-step, High Stakes 2-step, Bootcamp 3-step) + Summer Plan promo + Futures arm". — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt). One secondary source additionally mentions "an Instant Funding option that skips evaluation entirely" ([SEC-SNIP Tradetanto](https://tradetanto.com/learn/the-5-ers-rules-explained-a-complete-guide)). However, The5ers' own /instant-funding/ page is titled "Pass the One Step Program Challenge and Get Instant Funding", which suggests Hyper Growth is being marketed as "instant funding". — [OFF-SNIP the5ers.com/instant-funding](https://the5ers.com/instant-funding/)
- **High Stakes has two target variants:** "New" (10% then 5%) and "Classic" (8% then 5%). Both require at least three profitable days per phase. — search summary of [SEC-SNIP TradingFinder](https://tradingfinder.com/props/the-5ers/rules/) / [SEC-SNIP ProptradingVibes](https://proptradingvibes.com/blog/the5ers-rules-overview)
- **No best-day or consistency rule was found for the four core CFD programs.** A secondary source says the Futures track has a per-position consistency rule "that the CFD programs do not enforce". — [SEC-SNIP ProptradingVibes](https://proptradingvibes.com/blog/the5ers-rules-overview)
- **The only CFD consistency rule found is in the 2026 Summer Plan (1-Step and 2-Step):** "Once you pass both Phase 1 and Phase 2 and receive your live $100,000 funded account, a 50% consistency requirement will apply … there is no consistency rule during the evaluation phases for the 2-Step plan." The best trading day may be at most 50% of total profits for a withdrawal or scale-up. — [OFF-SNIP 2-Step Plan FAQ](https://the5ers.com/faqs/2-step-plan-rules-specifications/); [OFF-SNIP Summer Plan](https://the5ers.com/summer-plan/)
- **Summer Plan details (limited-time 2026 promo):**
  - $100K account. 1-Step Plan $249 with a 10% target; 2-Step Plan from $149.
  - 3% daily loss on the higher of end-of-day equity or balance; hitting it terminates the account.
  - 50% daily consistency checked at payout.
  - Minimum withdrawal $250; payout cap up to $3,000 per cycle.
  - No orders from 2 minutes before to 2 minutes after high-impact news.
  - — [OFF-SNIP Summer Plan](https://the5ers.com/summer-plan/), [OFF-SNIP Summer Plan 2026 article](https://the5ers.com/prop-firm-summer-plan-2026/)
  - The dossier's reading of the homepage 1-Step table says "$2,000 payout cap", which conflicts with $3,000. — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)
- **Profitable-day minimums** (a distribution requirement, not a percentage cap):
  - High Stakes: at least 3 profitable days per step. A profitable day is one where "closed positions made a positive profit of at least 0.5% of the initial balance". — [OFF-SNIP help.the5ers.com](https://help.the5ers.com/how-do-you-define-a-profitable-day-in-the-high-stakes-program/)
  - Pro Growth: an official-domain snippet says "three minimum profitable days" (≥0.5%), but the same summary also says "no minimum trades or days requirements for completing level 1". These conflict. — [OFF-SNIP help.the5ers.com Pro Growth](https://help.the5ers.com/new-programprogrowth/)
  - Hyper Growth: "No minimum trades or days requirements for completing level 1". — [OFF-SNIP help.the5ers.com Hyper Growth](https://help.the5ers.com/how-does-the-hyper-growth-program-work/)
- The5ers Futures (out of scope) has a 40% best-trade consistency rule. — [OFF-SNIP Futures FAQ](https://the5ers.com/futures-faqs/what-is-the-consistency-rule/); a secondary source says 30% ([SEC-SNIP ProptradingVibes](https://proptradingvibes.com/blog/the5ers-rules-overview)); these conflict.

#### FundedNext
- The CFD families are Stellar 2-Step, Stellar 1-Step, Stellar Lite and Stellar Instant. Futures (Flex, Legacy, Rapid, Bolt) are separate. "Labs" sells experimental offers. Add-ons include "Lifetime 95%, no min days, 150% reward, Double Up, EA/VPS". — [DOSSIER FundedNext (short)](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/FundedNext.txt); [DOSSIER FundedNext (full)](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **Stellar Instant:** "no consistency rules … no restrictions on lot sizes or trade frequency, and no requirement to maintain performance patterns across different days". — [OFF-SNIP help article](https://help.fundednext.com/en/articles/11641328-are-there-any-consistency-rules-for-the-stellar-instant-account). Official page mirrors show "Consistency Rule None" and "Stellar Instant: No Daily Loss Limit | No Consistency Rule". — [OFF-MIRROR stellar-instant page](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfds-stellar-instant.md); [OFF-MIRROR /cfds page](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfds.md)
- **As of April 2026**, the 40% consistency rule applies only to futures products (Bolt challenge and funded, Legacy challenge, Rapid funded). It "does not apply to any of the four FundedNext CFD accounts". — [SEC-SNIP ProptradingVibes](https://proptradingvibes.com/blog/fundednext-consistency-rule)
- Stellar Lite has no consistency rule on the standard reward cycle. — [SEC-SNIP CryptoSlate](https://cryptoslate.com/prop-firms/fundednext-review/), [SEC-SNIP ForTraders](https://fortraders.com/blog/fundednext-rules)
- **Optional On-Demand Rewards add-on** (Stellar Lite, 2-Step, 1-Step; base price +5%):
  - A payout can be requested on any qualifying day "once your account is up 2% and the 40% consistency rule is maintained".
  - The rule: "Your best single trading day must stay within 40% of your total performance on FundedNext Accounts only".
  - Reward share is 95% from day one.
  - Buying this add-on therefore **introduces** a funded consistency rule. — [OFF-SNIP FundedNext blog](https://fundednext.com/blog/fundednext-stellar-on-demand-rewards)
- **Related rules on every Stellar account:** "CFD 'Max Risk 3% at any time' applies on every Stellar account (challenge + funded); only 40% of news-trading profit counts". — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **Forbidden:** "Change in trading behavior — Executing trades with Lot sizes or frequency that significantly deviate from your typical trading behavior." This works as a soft lot-size consistency rule. — [OFF-MIRROR general-rules/cfds/what-is-forbidden](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-en-general-rules-cfds-what-is-forbidden.md)
- **Legacy models:** the CFD Challenge Terms still mention "Evaluation Model" and "Express Model". An Express Model "purchased with a 'Consistency' designation" must follow consistency requirements; with a "Non-Consistency" designation they do not apply. — [OFF-MIRROR CFD Challenge Terms](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfd-challenge-terms.md). Whether these are still sold is unknown; they are absent from the current CFD line-up.

#### Funding Pips
- **Five live models:** 1-Step Flex (1 phase); 2-Step Standard, 2-Step Flex and 2-Step Pro (2 phases each); Zero (instant Master, no evaluation). The dossier's prices are from a live-checkout read on 2026-07-14 and a checkout table cross-checked 2026-08-26. FundingTicks (futures) "CLOSED 2026-01-18". — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- Earlier 2026 secondary sources list "1-Step, 2-Step, 2-Step Pro and Zero". — [SEC-SNIP ProptradingVibes](https://proptradingvibes.com/blog/fundingpips-rules-overview), [SEC-SNIP Tradetanto](https://tradetanto.com/learn/fundingpips-rules). The Sept-2026 dossier no longer lists a classic "1-Step", so it appears to have been replaced by 1-Step Flex (unverified).
- **No consistency rule in any evaluation** ("No consistency rule on eval"). — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt). The rule is checked only on the funded Master before a withdrawal, and "Breaking the consistency rule at Funding Pips does not breach or reset your account". — [SEC-SNIP summary of Propvator/ProptradingVibes/MarketsXplora](https://marketsxplora.com/review/fundingpips-trading-rules/)
- **2-Step Standard Master** (cycle locked at purchase):
  - Weekly 60%, Bi-weekly 80%, Monthly 100%, On-Demand 90%.
  - "On-Demand requires 35% Consistency Score + 2% min request."
  - "For Masters purchased on/after 2026-08-15, Monthly adds: 35% Consistency Score or lower + 7 profitable days of >=0.5% of starting Master size + 1% Striking System trigger."
  - — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
  - **Rule change:** before that date, secondary sources said the 35% rule applied "only on the On Demand reward cycle; Weekly, Bi-Weekly and Monthly cycles are not subject to it". This is now outdated for Monthly. — [SEC-SNIP Propvator](https://propvator.com/blog/does-funding-pips-have-a-consistency-rule/), [SEC-SNIP ProptradingVibes](https://proptradingvibes.com/blog/fundingpips-rules-overview)
- **2-Step Flex:**
  - Rewards are "85% bi-weekly (min 1%) OR 95% bi-weekly (request every 14 days after 3 profitable days, min 1%); Monthly 100% option (every 30 days, 35% consistency + 1% Striking System + 7 days of >=0.5%)".
  - Worked example for "$100K Flex 95%": "Risk-per-idea cap $2,000 — a correlated EURUSD+GBPUSD basket risking $2,500 combined = breach".
  - However, the dossier also quotes the 2-Step Flex page as "1.2% risk guideline: explicitly 'No Restrictions … on this model'". These conflict.
  - — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **2-Step Pro:** Master is "80% Weekly". "No Risk-Per-Trade-Idea cap ('removed' wording on Pro page)". — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **1-Step Flex:** Master "85% bi-weekly (locked)". A "Striking System 1% trigger applies on 1-Step Flex and post-2026-08-15 Standard Monthly". The definition of the Striking System was not retrieved. — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **Zero (instant):**
  - 15% consistency (largest day ≤15% of total profit).
  - At least 7 profitable days (≥0.25%) in each 30-day cycle.
  - "Your biggest loss cannot exceed your biggest win."
  - — [SEC-SNIP summary incl. NYC Servers/ProptradingVibes](https://newyorkcityservers.com/blog/fundingpips-review)
  - The help centre is quoted as: "Master Account from day one … 7 days with net profit of 0.25% or more … within each rolling 30-day period to be eligible for rewards". Zero also carries "5% TRAILING + max 1% open-risk rule". — [DOSSIER FundingPips citing help.fundingpips.com Zero article](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)

#### E8 Markets
- **Product lines:** "Forex/Crypto products (E8 One / Pro / Zero / Classic / Track / Signature Forex) and Futures products (E8 Signature Futures / E8 Zero Starter / E8 Zero MAX) are SEPARATE product lines". There is also a crypto arm (E8 One/Pro/Signature Crypto) and a 24/7 Perpetuals arm. — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **No consistency rule in any evaluation.** Funded best-day rules are payout conditions: the payout is denied until the rule is met, and the account stays active. — [SEC-SNIP ProptradingVibes](https://www.proptradingvibes.com/blog/e8-markets-consistency-rule), [SEC-SNIP Tradetanto](https://tradetanto.com/learn/e8-markets-rules), [SEC-SNIP Propvator](https://propvator.com/blog/does-e8-markets-have-a-consistency-rule/)
- **Funded best-day rules per model:**
  - E8 One: "Consistency: NONE during evaluation. 40% BEST-DAY RULE on funded (SimFi Performance): no single day > 40% of total generated profits".
  - E8 Signature Forex: "35% BEST-DAY RULE on funded".
  - E8 Classic, E8 Track and E8 Track 1:1: "40% best-day funded".
  - — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **E8 Pro Forex and E8 Zero Forex:** the dossier table lists no best-day rule (Pro: "daily payouts, min 1%"; Zero: "none eval"). The official On-Demand article is summarised as "40% best-day One, 35% Signature … Pro/Zero daily payouts with 1% / $100 minimums". E8 Zero Forex was "LAUNCHED JUL 2026". — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)

#### FXIFY
- **Line-up:** "SIX CFD paths":
  - One-Phase.
  - Two-Phase: Standard (trailing), Classic (static) and Pro (static; "new Apr 2026").
  - Three-Phase.
  - Lightning (7-day).
  - Instant Funding, plus Instant Lite.
  - A crypto arm; FXIFY Futures is separate.
  - — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)
- **Instant Funding Lite** was introduced in February 2026, from $19 for a $2,500 account, with 3% daily, 4% trailing and a 20% consistency rule. — [SEC-SNIP summary of FXEmpire/TradingFinder/BestPropFirms](https://www.fxempire.com/prop-firms/fxify)
- **Consistency per the dossier:** "30% on 1-Phase + Lightning (best day ≤30% of total); 25% on funded 2-Phase Classic; 20% on Instant Lite; none on Standard/3-Phase/Instant". For Three-Phase: "No consistency rule. EAs allowed." One-Phase worked example: a $100K account with "total +$10,000 with best day +$3,500 (35%) = FAIL consistency → keep trading till best ≤$3,000". — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)
- **Conflict on One-Phase:** a search summary states "There is no consistency rule on the One Phase challenge or Instant Funding Standard". It lists 30% on Lightning (both stages), 25% on the 2-Phase Static funded account and 20% on Instant Funding Lite. — [SEC-SNIP FXEmpire](https://www.fxempire.com/prop-firms/fxify), [SEC-SNIP TradingFinder "FXIFY Rules 2026 – 30% Consistency Rule"](https://tradingfinder.com/props/fxify/rules/), [SEC-SNIP Propvator](https://propvator.com/blog/does-fxify-have-a-consistency-rule/)
- The crypto Instant Funded account has its own consistency rule (official FAQ title). — [OFF-SNIP FXIFY FAQ](https://fxify.com/faqs/all-faqs/crypto-accounts/crypto-account-how-does-the-consistency-rule-work-on-the-crypto-instant-funded/)

### Inferences
- For a trader who wants **zero consistency exposure in both phases**, the cleanest candidates are:
  - FTMO 2-Step (Swing variant for 24/7 holding).
  - The5ers High Stakes, Hyper Growth, Pro Growth and Bootcamp.
  - FundedNext Stellar 2-Step, 1-Step and Lite without On-Demand.
  - Funding Pips 2-Step Standard Weekly or Bi-weekly, 2-Step Flex Bi-weekly, 2-Step Pro Weekly and 1-Step Flex.
  - FXIFY Two-Phase Standard and Three-Phase.
  - E8 Pro and E8 Zero Forex, provided their "no best-day" status is confirmed on the official site.
- A clear 2026 pattern: consistency rules are increasingly **tied to the payout option picked at checkout** (Funding Pips On-Demand/Monthly, FundedNext On-Demand add-on, FXIFY Classic 100% line, E8 funded best-day). The "no consistency" status often depends on choosing the **slower/lower-split** payout cycle.
- FTMO's "no substantially larger position sizes" and FundedNext's "lot size/frequency deviation" rules are not percentage consistency rules. They can still bite an EA that scales lots aggressively (e.g., martingale or pyramiding). This is an inference from the rule wording.

### Gaps
- The Funding Pips "Striking System (1% trigger)" definition could not be retrieved. Whether it restricts payouts or trading on 1-Step Flex is unknown.
- The FXIFY One-Phase consistency status is disputed (30% vs none) and needs checking on https://fxify.com/programs/one-phase/. The FXIFY Two-Phase Pro consistency status is unknown.
- E8 Pro and E8 Zero Forex are not **explicitly** stated anywhere as having "no best-day rule". This was inferred from the dossier table and the payout-article summary.
- The5ers: no official statement was found that explicitly says "no consistency rule" for High Stakes, Hyper Growth, Pro Growth or Bootcamp. The absence is inferred.
- It is unknown whether the FundedNext legacy Express "Non-Consistency" model is still purchasable.
- An unverified 2026 claim that FTMO "now use[s] real-time equity" for the max-loss calculation appeared only in a secondary search summary ([SEC-SNIP PropFirmPaid](https://propfirmpaid.com/blog/ftmo-review-2026-updated-rules-pricing)) and could not be checked.

---

## 2. Platforms: is MetaTrader 5 available for these models?

### Takeaway
MT5 is offered by all six firms, but the details matter:
- **FundedNext** allows automated trading only on MT4/MT5, and Stellar Instant is MT5-only.
- **E8** runs MT5 through a separate entity (E8 Markets Ltd, Saint Lucia).
- **FXIFY** runs MT5 through its broker FXPIG, and US traders must use DXtrade.
- **FTMO, The5ers, FundedNext and FXIFY** do not provide MetaTrader to US-located clients.

### Cited Findings
- **FTMO:**
  - Platforms: MetaTrader 4, MetaTrader 5, cTrader and TradingView, for both the Challenge and the FTMO Account. DXtrade is also referenced. — [OFF-SNIP FTMO FAQ platforms](https://ftmo.com/en/faq/which-platforms-can-i-use-for-trading/), [OFF-SNIP FTMO Trading Platforms](https://ftmo.com/en/trading-platforms/)
  - Traders should not log in to MetaTrader or cTrader from the United States. A VPN/VPS must not give a US geolocation when using MetaTrader, cTrader or TradingView. — [OFF-SNIP FTMO FAQ VPN/VPS](https://ftmo.com/en/faq/can-i-travel-or-use-vpn-vps/)
- **The5ers:** non-US clients can use MetaTrader 5, cTrader and TradingView; US clients can use TradingView only. cTrader costs an extra $10. — [OFF-SNIP The5ers FAQ platforms](https://the5ers.com/faqs/which-trading-platform-do-you-use/)
- **FundedNext:**
  - Four CFD platforms: MT5 ("Automated trading via Expert Advisors (MQL5)"), MT4, cTrader (all marked "Not available for USA clients") and Match-Trader ("Available to Regular and USA clients"). "Run an EA or automated strategy: MT4 or MT5." — [OFF-MIRROR fundednext.com trading-platforms page, © 2026](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/firms_rules/fundednext.com-a249e2c8/0014-trading-platforms.txt)
  - "MT5-exclusive items: Free Trial Accounts, Free Monthly Competition Accounts, Stellar Instant". — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **Funding Pips:**
  - The homepage lists platforms "MT5/cTrader/Match-Trader". "MetaTrader 5 (MT5) — flagship, EA support, deep symbol set." TradeLocker is available "on select models" per PropFirmMatch reviewer reports. — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
  - Funding Pips' own blog has an MT5 article. — [DOSSIER-cited FundingPips blog](https://fundingpips.com/ar/blog/metatrader-5-mt5-the-ultimate-trading-platform-for-forex-and-cfds) (URL as listed in a GitHub research doc: [MrPichii prop_firm_market_2026.md](https://github.com/MrPichii/NAS100-mean-reversion-system-with-a-meta-labeling-ML-filter-walk-forward-validated-Monte-Carlo-ri/blob/21ab916a0de0995b78bf2e59729943372af2d549/docs/research/prop_firm_market_2026.md))
- **E8 Markets:**
  - "MetaTrader 5 (MT5) — via E8 Markets Ltd (Saint Lucia entity)". E8 Funding LLC "solely operates … Tradelocker, cTrader, and Match Trade". There is also a proprietary "E8 Terminal". The futures platform is Tradovate only.
  - The dossier warns against E8 for "MT5-only US traders (verify MT5 restriction first)".
  - — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **FXIFY:** "MetaTrader 4 (Platform 4), MetaTrader 5 (Platform 5, via FXPIG), DXTrade (US traders MUST use DXtrade — MT4/5 restricted in US), TradingView." — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)

### Inferences
- For a non-US trader running an MT5 EA, MT5 should be selectable on every candidate model. At FundedNext, choosing MT5 (not cTrader or Match-Trader) is mandatory for EA use.

### Gaps
- Per-model MT5 availability was not confirmed. Examples: whether E8 Pro and E8 Zero Forex can be bought on MT5 (the E8 MT5 entity is separate); whether FXIFY Three-Phase is offered on MT5; whether Funding Pips 1-Step Flex and 2-Step Flex are offered on MT5.
- The trader's residence is not stated. If the trader is US-based, MetaTrader is not available at FTMO, The5ers, FundedNext or FXIFY per the sources above.

---

## 3. Are Expert Advisors / automated trading allowed, and with what restrictions?

### Takeaway
- **Allowed without extra fees:** FTMO, The5ers, Funding Pips, E8 (forex) and FXIFY (on the 1/2/3-Phase models).
- **Restrictions to note:**
  - **The5ers** requires the trader to **own the EA source code**.
  - **FTMO and E8** allow third-party EAs but penalise the same EA or strategy being used by many traders: FTMO applies a $400k allocation cap per client or strategy; E8 enforces "one strategy per user".
  - **FXIFY bans EAs on Lightning and Instant Funding.**
- **FundedNext (2026)** permits automation only on MT4/MT5 **with a paid "VPS & EA" add-on**. Using EAs or a VPS without that add-on is listed as forbidden.

### Cited Findings
- **FTMO:**
  - "As long as your trading is legitimate and conforms to real market conditions, FTMO allows discretionary trading, algorithmic trading, and EAs."
  - With third-party software, "make sure that the strategy or the same EA is not being used by other traders as there is a maximum capital allocation of $400,000 per client or per strategy".
  - — [OFF-SNIP FTMO FAQ strategies](https://ftmo.com/en/faq/which-instruments-can-i-trade-and-what-strategies-am-i-allowed-to-use/)
  - Forbidden: "EAs that cause the trading account to become hyperactive with an excessive number of more than 2,000 server requests per day". — [OFF-SNIP FTMO Forbidden Trading Practices](https://ftmo.com/en/forbidden-trading-practices/)
  - Dossier: "EAs allowed incl. third-party, BUT duplicate third-party EA strategies across traders risk max-capital-allocation denial". — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)
- **The5ers:**
  - EAs are permitted, but EAs must not copy other persons' signals, "do tick scalping, perform latency arbitrage trading, perform reverse arbitrage trading, perform hedge arbitrage trading, perform high-frequency trading, or use emulators". Such accounts "will be canceled, banned, and will not be refunded".
  - "The trader must own the source code of the EA." Using an EA "from a provider where the trader does not own the source code" is prohibited.
  - The stop loss must be visible on the platform; no "stealth mode" stop loss.
  - — [OFF-SNIP The5ers EA FAQ](https://the5ers.com/faqs/can-i-use-an-ea-expert-advisor-can-i-set-a-stealth-mode-stop-loss/), [OFF-SNIP help centre copy](https://help.the5ers.com/can-i-use-an-ea-expert-advisor-can-i-set-a-stealth-mode-stop-loss/)
  - The dossier also lists "EA hyperactivity degrading servers" as banned and "EAs/algos (self-built)" as allowed. — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)
- **FundedNext:**
  - Official platform page: "Run an EA or automated strategy — MT4 or MT5. **Automated trading is only permitted on MetaTrader at FundedNext (EA usage fee applies).**" — [OFF-MIRROR trading-platforms page, © 2026](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/firms_rules/fundednext.com-a249e2c8/0014-trading-platforms.txt)
  - Official "What is forbidden" page: "Unauthorized VPS / EAs Usage — Using a VPS or Expert Advisor (EAs) without prior approval through official FundedNext add-ons." It links to the help article https://help.fundednext.com/en/articles/8020351-what-are-the-restricted-prohibited-trading-strategies. — [OFF-MIRROR what-is-forbidden](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-en-general-rules-cfds-what-is-forbidden.md)
  - Model pages (Stellar Instant, Lite, 1-Step): "EAs/VPS — Available with add-ons". The Stellar Instant checkout shows "Add-Ons Available: VPS & EA". — [OFF-MIRROR Stellar Instant](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfds-stellar-instant.md), [OFF-MIRROR Stellar Lite](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfds-stellar-lite.md), [OFF-MIRROR Stellar 1-Step](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfds-stellar-1-step.md)
  - **Conflicting (likely older) wording in the dossier:** EAs/indicators "allowed if used responsibly" (MT4/MT5 per the Lite help article). On Match-Trader "automated/algorithmic trading is NOT allowed". Also banned: "Unauthorised automation/HFT/mass-order behaviour/platform overload". — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **Funding Pips:**
  - "ALLOWED: EAs, algos, discretionary; overnight + weekend holding; news trading in evaluation (non-exploitative)". The banned list includes intentionally exploiting news or violating the red-folder blackout, and "Hedging across connected accounts / firms to game targets". — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
  - A GitHub research doc of unknown date claims: "Funding Pips enforces a rule where profits from trades held under 2 minutes on funded accounts are completely disqualified". — [unverified, GitHub research doc (MrPichii)](https://github.com/MrPichii/NAS100-mean-reversion-system-with-a-meta-labeling-ML-filter-walk-forward-validated-Monte-Carlo-ri/blob/21ab916a0de0995b78bf2e59729943372af2d549/docs/research/prop_firm_market_2026.md)
- **E8 Markets:**
  - E8 help-centre text dated **May 14, 2026**: "you can use any EA (Expert Advisor) as long as we don't see multiple users executing the same trades/strategy. We limit one strategy per user, so if we see multiple users utilize the same EA, it may lead to the termination of your account. So even though the use of third-party EA is allowed, we recommend that each user use their own programmed EA." — [OFF-MIRROR E8 rules text](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/firms_rules/e8Market/rules.txt)
  - "EAs/bots: ALLOWED on Forex/Crypto … PROHIBITED on Futures — manual trading only". — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
  - Copy trading "is not allowed between E8 evaluation accounts", but copying between your own personal account, E8 Trader accounts, or a funded and an evaluation account is allowed. — [OFF-MIRROR via PropFirmMatch copy](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/firms_rules/e8Market/propfirmmatch.txt)
  - Unverified claim: E8 "restricts systems where more than 50% of the total trade allocation is held for under 60 seconds" as HFT. — [GitHub research doc (MrPichii)](https://github.com/MrPichii/NAS100-mean-reversion-system-with-a-meta-labeling-ML-filter-walk-forward-validated-Monte-Carlo-ri/blob/21ab916a0de0995b78bf2e59729943372af2d549/docs/research/prop_firm_market_2026.md)
- **FXIFY:**
  - "EAs/grid/martingale/copy: ALLOWED on 1/2/3-Phase (even advertised 'Martingale & Grid Allowed'); **PROHIBITED on Lightning + Instant**."
  - Copy trading: "may copy between OWN FXIFY accounts or FXIFY→external; copying others' signals onto FXIFY as decision-maker is banned".
  - — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)

### Inferences
- A **self-coded** EA that is not sold or shared fits every firm. A **purchased/third-party** EA is excluded at The5ers (unless the trader owns the source), risky at FTMO and E8 (duplicate-strategy checks), and needs a paid add-on at FundedNext.
- FXIFY Instant Funding Standard is consistency-free but **unusable for an EA** (EAs prohibited). The same applies to Lightning.

### Gaps
- The price and terms of FundedNext's "VPS & EA" add-on, and the date this requirement was introduced, are unknown.
- Funding Pips' and FXIFY's exact HFT or minimum-hold-time definitions for forex are unknown. The Funding Pips "2-minute" funded-profit rule is unverified.
- It is unknown whether FXIFY or Funding Pips restrict third-party EAs.

---

## 4. Is a VPS / remote server allowed?

### Takeaway
- **Explicitly allowed:** FTMO ("generally allowed"; avoid a US geolocation).
- **Apparently allowed:** The5ers (official blog content says EAs on VPS are allowed).
- **Allowed only via a paid add-on:** FundedNext. Using a VPS without its "VPS & EA" add-on is listed as forbidden.
- **Not explicitly addressed:** Funding Pips (VPN/travel "not explicitly banned", but it runs device/IP matching). E8 and FXIFY status is **unknown**.

### Cited Findings
- **FTMO:** "The use of VPN/VPS is generally allowed." Clients should avoid changing their geolocation to the United States when using MetaTrader, cTrader or TradingView. — [OFF-SNIP FTMO FAQ](https://ftmo.com/en/faq/can-i-travel-or-use-vpn-vps/)
- **The5ers:**
  - A The5ers article on algorithmic trading (2026) states: "While The5ers allows EAs on VPS, prohibited approaches include arbitrage trading, high-frequency strategies with trade durations measured in seconds, EAs that scalp during rollover periods, and copy trading from external accounts." — [OFF-SNIP The5ers blog "AI trading bots & Algos"](https://the5ers.com/ai-trading-bots-and-algos/)
  - "Trading from Forbidden Territories via VPN (compliance breach)" is banned. — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)
- **FundedNext:**
  - Forbidden: "Using a VPS or Expert Advisor (EAs) without prior approval through official FundedNext add-ons." — [OFF-MIRROR what-is-forbidden](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-en-general-rules-cfds-what-is-forbidden.md)
  - The dossier recommends "Single-IP discipline: one consistent device/IP recommended; dedicated VPN/VPS IP recommended when roaming". — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **Funding Pips:** "VPN/travel: not explicitly banned; Device-ID/IP-match system means shared networks/devices risk false flags — use a personal device + connection." — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **E8 Markets and FXIFY:** no VPS statement was found in any accessible source. For FXIFY, the only VPS-related item is a QuantVPS article on FXIFY payout rules, dated 2026-07-04, listed as a source in the dossier. — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)

### Inferences
- A 24/7 Windows VPS is safest at FTMO (explicit permission) and probably fine at The5ers. At FundedNext it is only compliant with the paid add-on. At Funding Pips, a **dedicated** VPS with a stable IP (not shared with other traders) would reduce device/IP-match flags. This is an inference from the device-ID wording.

### Gaps
- Official VPS policies for **E8 Markets, FXIFY and Funding Pips** could not be found. They should be checked in each help centre before buying.

---

## 5. Are XAUUSD (gold) and NAS100 (US100/USTEC) tradable?

### Takeaway
- **Explicitly confirmed:** FTMO (US100.cash, XAUUSD) and The5ers (NAS100, XAUUSD).
- **Indicated but symbol names not confirmed:** Funding Pips, E8 and FXIFY list metals/commodities and indices. For FundedNext, no symbol list was retrieved; only indices and commodities leverage tiers are known.
- Leverage on indices and metals is often much lower than on FX, which matters for gold and NAS100 lot sizing.

### Cited Findings
- **FTMO:** FTMO trading updates reference the symbols "US100.cash" and "XAUUSD". — [OFF-SNIP FTMO Symbols](https://ftmo.com/en/symbols/), [OFF-SNIP FTMO Trading Update 3 Jul 2025](https://ftmo.com/en/trading-updates/trading-update-3-jul-2025/)
- **The5ers:**
  - NAS100 and XAUUSD are both available. — [OFF-SNIP The5ers asset specifications](https://the5ers.com/asset-specifications/)
  - An official-domain snippet says that on "the instant funding program … Index positions should be closed before the weekend". Its scope and date are unclear. — [OFF-SNIP The5ers asset specifications / indices page](https://the5ers.com/indices/)
  - Leverage: "High Stakes 1:100; Hyper Growth / Pro Growth / Bootcamp 1:30". — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)
- **FundedNext:**
  - Leverage per the dossier:
    - Challenge: 1-Step "Forex 1:30, Indices 1:10, Commodities 1:15"; 2-Step and Lite "Forex 1:100, Indices and Commodities 1:25".
    - Funded: 1-Step "Indices and Commodities 1:10"; 2-Step and Lite "Indices and Commodities 1:15".
    - Instant: "Forex 1:30, Indices 1:5, Commodities 1:7.5".
    - — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
  - Conflict: the official model-page mirrors show "Forex 1:30, Indices 1:10, Commodities 1:10" (Instant, Lite) and "Commodities 1:15" (1-Step). — [OFF-MIRROR Stellar Instant](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfds-stellar-instant.md)
- **Funding Pips:**
  - "INSTRUMENTS: FX (forex pairs), Metals, Energies, Indices, Crypto."
  - Homepage leverage 1:100. Swap-free leverage: "Metals 1:10 … Indices 1:5".
  - Commission "$5 per lot FX/metals on standard models" (third-party confirmed).
  - The Master account has a "dynamic leverage tier system for Metals, Energies, and Indices" that does not apply to Zero (from a rules-changelog fragment).
  - — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt); [OFF-MIRROR changelog fragment](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/firms_rules/alphaCapitol/rules.txt)
- **E8 Markets:** "CLASSIC INSTRUMENTS: 250+ markets — Forex pairs, Indices, Commodities/Metals, Energies (WTI, Brent), Stocks, Crypto". The full symbol list is live at https://e8x.e8markets.com/trading-symbols. The Perpetuals arm lists "BTC, Gold, Oil, Nasdaq, EUR". — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **FXIFY:** "INSTRUMENTS: 150–330+ symbols: Forex, Indices, Crypto, Commodities, Stocks". — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)

### Inferences
- Gold and a Nasdaq-100 CFD are standard at all six firms (metals/commodities and indices categories are listed everywhere). The exact MT5 symbol names (e.g., "NAS100" vs "US100.cash" vs "NDX100"), contract sizes and index/metal leverage caps should be checked per firm before configuring the EA.

### Gaps
- The exact XAUUSD and NAS100 symbol names, trading hours and commissions for FundedNext, Funding Pips, E8 and FXIFY are unknown. The FundedNext symbols page exists in the crawl (`0016-symbols.txt`) but its content was not retrieved.

---

## 6. Core risk rules of the no-consistency models (targets, daily loss, max loss type, max-risk rules, minimum days, news, weekend)

### Takeaway
The no-consistency models vary widely:
- **Static max-loss models:** FTMO 2-Step (10%), The5ers High Stakes (10%), FundedNext 2-Step (10%) and Lite (8%), Funding Pips Standard (10%), 2-Step Flex (12%) and Pro (6%), E8 Pro (8%) and E8 Zero Forex (3%), FXIFY Three-Phase.
- **Trailing max-loss models:** FXIFY Two-Phase Standard (10% trailing) and FundedNext Stellar Instant (6% trailing).
- For a 24/7 EA the key restrictions are:
  - FTMO Standard accounts: no weekend holding and news blackouts. Use FTMO **Swing** for 24/7 holding.
  - Funding Pips Master: 5-minute red-folder news blackout.
  - FundedNext: Max Risk 3% rule and 40% news-profit counting.
  - The5ers Hyper Growth: daily pause and a possibly mandatory stop loss.

### Cited Findings

#### FTMO 2-Step (no consistency; Standard and Swing)
- **Targets and time:** 10% (Challenge) then 5% (Verification). The dossier table: "10% Ch + 5% Ver | 5% | 10% STATIC | none". Unlimited time. — [OFF-SNIP FTMO How it works / 2-Step](https://ftmo.com/en/2-step-challenge/); [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)
- **Daily loss:** Maximum Daily Loss is 5% of the initial simulated capital, recalculated every midnight CE(S)T. — [OFF-SNIP Trading Objectives](https://ftmo.com/en/trading-objectives/)
- **Max loss:** 10% of the initial capital. It does not trail like the 1-Step's end-of-day trailing loss. — [OFF-SNIP Trading Objectives](https://ftmo.com/en/trading-objectives/); described as a "10% static maximum loss" by [SEC-SNIP MarketsCoupons](https://www.marketscoupons.com/guides/ftmo-review)
- **Minimum days:** 4 minimum trading days in the Evaluation Process (Challenge and Verification), with at least one position opened each day. — [OFF-SNIP How it works](https://ftmo.com/en/how-it-works/)
- **Standard vs Swing:**
  - Standard FTMO Account: "NO opening/closing within 2 minutes around restricted high-impact news on affected symbols"; must "close before weekend/overnight windows". — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)
  - The Swing account type has no restrictions on news trading, overnight holding ("longer than 2 hours after market close") or weekend holding. It has the same price as Standard. — [OFF-SNIP FTMO FAQ Swing](https://ftmo.com/en/faq/ftmo-swing-account-type/), [OFF-SNIP FTMO FAQ news](https://ftmo.com/en/faq/can-i-trade-news/); price note in [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)
- **For comparison, FTMO 1-Step (has a Best Day Rule):**
  - 10% target, unlimited time; MDL 3% of the initial balance, recalculated daily. — [OFF-SNIP](https://ftmo.com/en/1-step-challenge/)
  - Max loss 10% **end-of-day trailing**: the limit is recalculated at 00:00 CE(S)T from the highest EOD balance and "can only increase". — [OFF-SNIP FTMO FAQ ML 1-Step](https://ftmo.com/au/faq/what-is-the-max-loss-ml-rule-in-ftmo-challenge-1-step/)
  - Minimum trading days: "NONE" per the dossier. FTMO says the 1-Step can be completed "in as few as 2 trading days" because of the Best Day Rule ([OFF-SNIP FTMO x OANDA FAQ](https://ftmo.oanda.com/faq/what-is-the-minimum-time-required-to-pass-ftmo-challenge-1-step/)). One secondary source claims "three trading days" (conflict).
  - "Swing n/a (no Swing on 1-Step)". — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)

#### The5ers (no consistency found)
- **High Stakes:**
  - Targets 8% then 5% (Classic) or 10% then 5% (New); see §1.
  - Daily loss 5%, "taken from the closing equity or balance of your previous day (the highest between them)". Max loss 10% from the initial balance ("absolute drawdown"). — [OFF-SNIP help.the5ers High Stakes drawdown](https://help.the5ers.com/what-is-the-drawdown-rule-for-high-stakes/)
  - At least 3 profitable days (≥0.5%) per step. — [OFF-SNIP help centre](https://help.the5ers.com/how-do-you-define-a-profitable-day-in-the-high-stakes-program/)
  - Dossier table: "$2.5K–$100K | 10% then 5% | 5% | 10% STATIC | 1:100 | 80/20 | $500,000". — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)
- **Hyper Growth:**
  - 10% target against a 6% stop-out; "3% daily pause". When the pause level is hit, "all open trades get closed, and the account remains disabled until the next trading day". — [OFF-SNIP help centre daily pause](https://help.the5ers.com/how-does-the-daily-pause-work/), [OFF-SNIP The5ers programs explained](https://the5ers.com/challenge-programs-bootcamp-high-stakes-hyper-growth-explained/)
  - No minimum days. — [OFF-SNIP help centre Hyper Growth](https://help.the5ers.com/how-does-the-hyper-growth-program-work/)
  - "Holding open trades over the weekend is allowed, and news trading is allowed in the Hyper Growth Program." — [OFF-SNIP help centre Hyper Growth](https://help.the5ers.com/how-does-the-hyper-growth-program-work/)
  - **Stop-loss conflict:** an official-domain summary says "A mandatory stop-loss is required on every position throughout the program" ([OFF-SNIP](https://the5ers.com/challenge-programs-bootcamp-high-stakes-hyper-growth-explained/)). A secondary source says "stop loss NOT required" ([SEC-SNIP ProptradingVibes](https://proptradingvibes.com/blog/the5ers-rules-overview)).
- **Pro Growth:** 10% target; 3% daily loss that **terminates** (no pause); 6% max loss; profitable-day requirement disputed (§1). — [OFF-SNIP help centre Pro Growth](https://help.the5ers.com/new-programprogrowth/); dossier: "$5K/$10K/$20K/$50K | 10% | 3% TERMINATES | 6% stop-out | 1:30 | 75/25" ([DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt))
- **Bootcamp:** 3 steps with a 6% target each; 5% max loss per step. Funded stage: "3% daily pause", "4% funded" max loss, leverage 1:30, split 50/50, scaling to $4,000,000. — [OFF-SNIP The5ers programs explained](https://the5ers.com/challenge-programs-bootcamp-high-stakes-hyper-growth-explained/); [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)
- **News (core programs):** "news trading within normal risk (no 5-min blackout published …)"; overnight and weekend holding are allowed. The Summer Plan, by contrast, has a 2-minute news ban (§1). — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)

#### FundedNext Stellar models (no consistency without the On-Demand add-on)
- **Official CFD Challenge Terms:** minimum trading days "Stellar 1-Step Model — 2 days; Stellar 2-Step Model — 5 days; Stellar Lite Model — 5 days". Profit targets "Stellar 1-Step — 10%; Stellar 2-Step — Phase 1: 8%, Phase 2: 5%; Stellar Lite — Phase 1: 8%, Phase 2: 4%". — [OFF-MIRROR CFD Challenge Terms](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfd-challenge-terms.md)
- **Dossier model table:**

  | Model | Sizes | Daily loss | Max loss | Split | Fee refund |
  |---|---|---|---|---|---|
  | Stellar 2-Step | 6K/15K/25K/50K/100K/200K | 5% | 10% STATIC | 80%→90%→95% | with 1st reward |
  | Stellar 1-Step | 6K–200K | 3% | 6% STATIC | 80%→90%→95% | with 3rd reward |
  | Stellar Lite | 5K/10K/25K/50K/100K/200K | 4% | 8% STATIC | 80%→90%→95% | with 3rd reward |
  | Stellar Instant | 2K/5K/10K/20K | none | 6% TRAILING | 70%→80% | never |

  Stellar Instant also has no target and no minimum days. — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **2-Step daily loss detail:** "Daily Loss Limit: 5% of INITIAL balance per day". The profit target counts "Closed trades only". — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **Lite max-loss add-on:** an "MLL 10% Add-On (Lite-only)" lifts the max loss from 8% to 10%. — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
- **All Stellar accounts:**
  - "Max Risk 3% at any time" (challenge and funded). This is a max-open-risk rule.
  - News trading and overnight/weekend holding are allowed on challenge and funded, but "only 40% of news-trading profit counts".
  - No time limit.
  - — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)

#### Funding Pips (consistency-free cycles only)
- **Dossier model table:**

  | Model | Targets | Daily loss | Max loss | Minimum days | Sizes |
  |---|---|---|---|---|---|
  | 1-Step Flex | 12% (eval only) | 3% | 12% STATIC | 1 day | 5K–100K |
  | 2-Step Standard | 8% + 5% | 5% (higher of opening balance/equity) | 10% STATIC floor | 3 per phase (eval only) | 5K–100K (+2.5K in select regions) |
  | 2-Step Flex | 10% + 6% | 4% | 12% STATIC | 1 day (85% option) / 3 profitable days (95% option) | 5K–100K |
  | 2-Step Pro | 6% + 6% | 3% | 6% STATIC | 1 per phase | 5K–200K |
  | Zero | none | 3% | 5% TRAILING + max 1% open risk | (reward eligibility: 7 profitable days per 30) | 5K–200K |

  "No time limit on ANY evaluation". Inactivity rule: at least 1 trade every 30 days, on evaluation and Master. "Funded (Master) has NO profit target on any model." — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **Rule change:** the 2-Step Standard "10% variant withdrawn 2026-07-24 06:00 Server Time UTC+3". — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **News:**
  - Evaluation: "No scheduled-news window restriction during evaluation; intentionally exploiting news is prohibited".
  - Master: "5-min blackout around red-folder news on affected currencies; news profits deducted". Trades opened 5h before high-impact news or speeches are excluded from the rule, per a truncated fragment. Standard, Pro and Zero follow the same red-folder logic.
  - Weekend and overnight holding are allowed on evaluation and Master.
  - — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)

#### E8 Pro and E8 Zero Forex (no best-day rule listed)
- **E8 Pro:** "Standard Pro track: 8% Phase 1 / 5% Phase 2 targets, 4% daily loss, 8% static max drawdown, 80% split (100% payout tier selectable). DAILY payouts with 1% minimum … No activation fee." Sizes 5K–500K; the table marks the steps as "1-2*". — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **E8 Zero Forex (launched Jul 2026):** "3% STATIC max drawdown from INITIAL balance … 6% closed-trade target, 80% split. Simplicity product: no checkout customization. Daily payouts, $100 minimum." $50K is the flagship size. — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **Other E8 models, for comparison (all with a funded best-day rule):**
  - E8 One: 6% default target (customisable 6–21%). Max drawdown is "INTRADAY DYNAMIC (TRAILING), 4% default (custom 4-14%)" and "moves against you IN REAL TIME as equity rises — including unrealized gains". Base prices use a "default 6%/4%/3% rule set".
  - Classic: 8%/4%, 4% daily, 8% static.
  - Track: 8%/4%/third step, 4% daily, 8% static.
  - Track 1:1: 5%/5%, 5% daily, 5% static.
  - Signature Forex: 6% target, 4%/3% end-of-day dynamic trailing, no separate daily loss.
  - — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **News and weekend:** "News trading: ALLOWED on all Classic products with NO restrictions (Signature page: 'Trade the economic calendar with no restrictions')". Weekend holding is allowed. — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)

#### FXIFY Two-Phase Standard and Three-Phase (no consistency)
- **Two-Phase:**
  - "Targets 10% Ph1 + 5% Ph2 … Daily 4% all variants … Max 10%: TRAILING (Standard) vs STATIC (Classic + Pro Apr-2026)". Minimum 5 trading days per phase.
  - The table row for Two-Phase Standard reads "5K→400K | 10% / 5% | 4% | 10% TRAIL | 5/phase | 80% (90% add-on)".
  - — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)
- **Three-Phase:** "Targets 5%/5%/5% in order … Daily 5%; Max static band (table 5–10%); min 5 days/phase; unlimited time. No consistency rule. EAs allowed. Refund 100% with first payout." — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)
- **One-Phase (disputed consistency):** "Target 10% once … Daily 3%; Max 6% TRAILING equity high-water-mark, LOCKS once +6% reached"; minimum 5 trading days. — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)
- **Instant Funding Standard (EAs banned):**
  - The dossier gives "4%" daily loss and an 8% trailing max loss. — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)
  - Conflict: a secondary summary says Instant Standard "runs on an 8% trailing drawdown. There is no daily loss limit, no consistency rule, and no minimum trading days". — [SEC-SNIP FXEmpire/TradingFinder summary](https://www.fxempire.com/prop-firms/fxify)
- **News, weekend and stop loss:** "Weekend holding: permitted ALL account types incl. funded. News: Two-Phase unrestricted; Instant/Lightning 5-min either side. No SL required on any program." — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)

### Inferences
- For a 24/7 gold/NAS100 EA that may hold over weekends and through news, the models with the fewest operational frictions are:
  - FTMO 2-Step **Swing**.
  - FXIFY Two-Phase **Standard** (but a 10% trailing loss).
  - E8 Pro.
  - The5ers High Stakes (1:100 leverage).
- Funding Pips Masters impose a 5-minute news blackout with profit deduction, which an unattended EA must respect.
- FundedNext's "Max Risk 3% at any time" limits combined open exposure. A gold plus NAS100 EA with simultaneous positions must cap total open risk below 3%.
- Trailing structures penalise open-profit give-backs. FXIFY Two-Phase Standard trails at 10%; E8 One trails intraday including unrealized gains, but E8 One has a best-day rule anyway. Static models are friendlier to EAs that let winners run.

### Gaps
- The exact daily-loss calculation basis (balance vs equity, reset time) is unknown for FundedNext, E8 Pro/Zero and FXIFY.
- It is unknown whether FXIFY One-Phase/Three-Phase or E8 Pro/Zero have news restrictions on funded accounts. FXIFY's statement covers Two-Phase, Instant and Lightning only.
- Whether E8 Pro is 1-step or 2-step (the table says "1-2*") and E8 Zero's funded daily loss are unclear.
- For FTMO 2-Step, the "Maximum Loss" wording in one official snippet ("recalculated daily … highest account balance") appears to belong to the 1-Step. Official pages should be checked to confirm the 2-Step max loss is static.

---

## 7. Payouts: first payout timing, frequency, profit split, minimum payout

### Takeaway
- **FTMO 2-Step:** on demand after day 14 (a bi-weekly rhythm in practice); 80% split, rising to 90% via scaling or the Premium programme; fee refunded with the first reward.
- **The5ers High Stakes:** every 14 days at 80%. Hyper Growth and Bootcamp start at 50%; Pro Growth starts at 75%.
- **FundedNext 2-Step:** first reward after 21 days, then every 14 days. 1-Step pays every 5 business days. Instant pays on demand at +5% (or bi-weekly at ≥1%).
- **Funding Pips:** depends on the cycle locked at purchase. Weekly 60% or Bi-weekly 80% (Standard), bi-weekly 85%/95% (2-Step Flex), weekly 80% (Pro). Minimum reward is 1% of Master size.
- **E8 Pro and Zero:** daily payouts with a 1% or $100 minimum.
- **FXIFY:** first payout on demand from the first funded day (minimum $50); 80% base split, 90% with an add-on.

### Cited Findings
- **FTMO:**
  - "Frequency: on-demand after day 14 (bi-weekly rhythm in practice)". Bank wire needs a minimum of $20 closed profit.
  - 2-Step split "80% (90% via Scale/Premium)"; the fee is refunded with the first reward. 1-Step split is 90% with "NO refund".
  - — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt)
  - A secondary summary: "Rewards can be requested after a minimum of 14 days from your first day of trading … bank transfers require at least $20 in closed profit and crypto withdrawals require $50". — [SEC-SNIP Tradetanto / TradersSecondBrain](https://traderssecondbrain.com/guides/ftmo-review)
  - 1-Step: "you start with 90% simulated profit on your first and all subsequent rewards". — [OFF-SNIP FTMO blog 1-Step](https://ftmo.com/en/blog/introducing-the-1-step-ftmo-challenge/)
  - Conflict: one official-domain snippet says "Your reward on your FTMO Account is 90% of your simulated profits" without specifying the model. — [OFF-SNIP FTMO How it works](https://ftmo.com/en/how-it-works/)
- **The5ers:**
  - High Stakes: "the ability to withdraw funds from your dashboard every 14 days". — [OFF-SNIP the5ers.com/high-stakes](https://the5ers.com/high-stakes/)
  - High Stakes pays on a bi-weekly cycle "at an 80% rate from the first payout". — [OFF-SNIP The5ers article](https://the5ers.com/pass-the-funded-trader-evaluation-rules-risk-mindset/)
  - "Pro Growth starts at 75/25, Hyper Growth and Bootcamp start at 50/50 … up to 100%". "The first payout is 14 days after receiving a funded account, then every two weeks." — [SEC-SNIP Tradetanto](https://tradetanto.com/learn/the-5-ers-rules-explained-a-complete-guide)
  - Hyper Growth: "Once passing level 1, your fully funded trading account will bring you a 50% profit share payout". — [OFF-SNIP The5ers article](https://the5ers.com/your-guide-to-passing-the-5ers-evaluation-program/)
  - Pro Growth: bi-weekly payouts, minimum $150. — [OFF-SNIP help centre Pro Growth](https://help.the5ers.com/new-programprogrowth/)
- **FundedNext:**
  - Stellar 2-Step: "You can request your first Performance Reward 21 days after starting trading, with subsequent Performance Rewards occurring every 14 days". Reward share becomes 80% on the FundedNext Account. — [OFF-SNIP FundedNext help](https://help.fundednext.com/en/articles/10701585-how-often-will-i-receive-my-performance-reward)
  - Stellar 1-Step: "Starting from the first trading cycle, you will receive Performance Rewards every 5 business days". Reward share quoted as 80% in the snippet. — [OFF-SNIP FundedNext help](https://help.fundednext.com/en/articles/10701585-how-often-will-i-receive-my-performance-reward)
  - Split ladder: "Standard 80% -> Scale-Up 90% -> 95% Add-On (1-Step/2-Step/Lite). Instant: 70% Day 1 -> 80% Tier 3+". — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
  - Stellar Lite: "First reward: 21 days, then bi-weekly (Bi-Weekly Add-On shortens to 14-day rhythm). Fee refund with 3RD reward." — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
  - Stellar Instant: "on-demand once at 5% growth, OR bi-weekly cycle at >=1% growth … 70% share Day 1 -> 80% Tier 3+". — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)
  - The optional On-Demand add-on (+5%) gives 95% from day one but brings a 40% consistency rule (§1). — [OFF-SNIP FundedNext blog](https://fundednext.com/blog/fundednext-stellar-on-demand-rewards)
- **Funding Pips:**
  - Cycles "LOCKED at purchase": Standard Weekly 60%, Bi-weekly 80%, Monthly 100%, On-Demand 90%; 2-Step Flex 85% or 95% bi-weekly; 2-Step Pro 80% weekly; 1-Step Flex 85% bi-weekly; Zero 95% bi-weekly.
  - "Min reward: 1% of Master size (2% for On-Demand)." Advertised average first rewards: "$389 ($5K) / $743 ($10K)".
  - — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **E8 Markets:**
  - E8 Pro: "DAILY payouts with 1% minimum (official On-Demand article: 'With E8 Pro, the minimum is 1%'). No on-demand schedule — request daily after rollover."
  - E8 Zero Forex: "Daily payouts, $100 minimum".
  - Split: Pro 80% (100% tier selectable); Zero 80%.
  - E8 Signature has payout caps and mandatory buffers; "unused profit above cap does not carry over".
  - — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **FXIFY:** "Base split 80%, 90% via add-on (+20% fee); Two-Phase Classic lists 100% variant lines. First payout ON DEMAND from first funded day (min $50). Refund 100% on 1/2/3-Phase with first payout." — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)

### Inferences
- The fastest payout access among consistency-free models is at E8 Pro (daily, 1% minimum) and FXIFY Two-Phase Standard and Three-Phase (on demand from day one, $50 minimum). FundedNext 1-Step pays every 5 business days.
- At Funding Pips the consistency-free route costs split: 60–80% on Standard Weekly/Bi-weekly versus 90–100% with consistency. 2-Step Flex at 85% or 95% bi-weekly is the exception.

### Gaps
- Minimum payout amounts for The5ers High Stakes and Hyper Growth, FXIFY Three-Phase and FundedNext 2-Step are unknown.
- The FundedNext 1-Step split conflicts: 80% in the help-centre snippet vs a possibly higher figure elsewhere.
- The FTMO 2-Step default split conflicts: 80% (dossier and secondary) vs a "90%" official snippet whose model is unspecified.

---

## 8. Price of the smallest account (ideally 10k)

### Takeaway
10k-class prices (USD, one-time):
- **FTMO:** 2-Step $89 (EUR89 promo display), 1-Step $79.
- **Funding Pips (10K):** 2-Step Standard $59 ($66 at checkout), 2-Step Pro $55, 2-Step Flex $59, 1-Step Flex $99, Zero $88.
- **E8 One (10K):** $72, but E8 One has a consistency rule. E8 Pro and Zero Forex prices are unknown.
- **FXIFY (10K):** 2-Phase $75–$89, 3-Phase $59, 1-Phase $89–$99.
- **The5ers:** only rough bands; Bootcamp $6K is about $39.
- **FundedNext:** unknown.
- All figures come from secondary compilations. Promotions rotate frequently.

### Cited Findings
- **FTMO:** "1-STEP (USD checkout): 10K $79 | 25K $199 | 50K $319 | 100K $499 | 200K $999". "2-STEP (USD checkout): 10K $89 | 25K $250 | 50K $345 | 100K $540 | 200K $1,080". EUR display for 2-Step 10K: "EUR155 (older EU display) / EUR89 (current promo display)". Swing and Standard 2-Step are the same price. — [DOSSIER FTMO](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FTMO.txt); "fees start from €89 for the $10K 2-Step" and 1-Step "from EUR 79" — [SEC-SNIP MarketsCoupons/TheTrustedProp summary](https://www.marketscoupons.com/guides/ftmo-review)
- **Funding Pips** (live checkout read 2026-07-14, pricing page read 2026-07-30):

  | Size | 1-Step Flex | 2-Step Standard | 2-Step Pro | 2-Step Flex | Zero |
  |---|---|---|---|---|---|
  | $5K | $59 | $32 ($36 at checkout) | $29 | $32 | $60 ($69 via Lune) |
  | $10K | $99 | $59 ($66 at checkout) | $55 | $59 | $88 ($99 via Lune) |

  A $2.5K size exists on Standard and Pro in select countries (~$29 band). Swap-free is a +10% add-on. — [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **E8 One** (aggregator base price, default rule set): "5K $40 | 10K $72 | 25K $154 | 50K $235 | 100K $398 | 200K $650 | 400K $1,301 | 500K $1,627". Checkout choices (drawdown, daily-loss and target bands) re-price the fee. — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **FXIFY** (base fees in USD; promos ONESTEP35 = 35% off 1-Phase until 2026-12-31, CHART30 = 30% off all except Lite until 2026-10-01):

  | Size | 1-Phase | 2-Phase | 3-Phase | Lightning | Instant |
  |---|---|---|---|---|---|
  | $5K | $59 | $39–$59 | $39 | — | — ($5K Lite $44) |
  | $10K | $99 ($89 P201) | $75–$89 | $59 | $99 ($59 P201) | $69–$449 ($89 Lite) |

  "P201" is the dossier's own citation label (probably a PropFirm201 review). — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt)
  - Instant Standard "starts at $69 for a $1,000 account". — [SEC-SNIP FXEmpire summary](https://www.fxempire.com/prop-firms/fxify)
- **The5ers:**
  - Dossier: "Bootcamp: $6K ~$39 (cheapest on-ramp)". High Stakes "$2.5K band | $5K–$25K … $100K ~$275–$875 band". Hyper Growth "~$260–$1,225 band across $5K–$20K+ tiers". Pro Growth "$5K–$50K band". The dossier itself says to "Confirm exact size at checkout". — [DOSSIER The5ers](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/The5ers.txt)
  - Summer Plan: $100K from $149 (2-Step) or $249 (1-Step). — [OFF-SNIP](https://the5ers.com/summer-plan/)
- **FundedNext:** smallest sizes are 6K (2-Step, 1-Step), 5K (Lite) and 2K (Instant). Prices were not retrieved. — [DOSSIER FundedNext](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundedNext.txt)

### Inferences
- Among consistency-free, EA-friendly models, the cheapest 10k-class entries appear to be Funding Pips 2-Step Pro ($55), FXIFY Three-Phase ($59) and Funding Pips 2-Step Standard ($59). FTMO 2-Step is $89 but refundable with the first reward.

### Gaps
- The5ers 10K prices per program (the dossier's "$25K ~$19" High Stakes figure looks implausible) are unknown.
- FundedNext prices for every Stellar model are unknown.
- E8 Pro and E8 Zero Forex prices are unknown.
- The FundedNext EA/VPS add-on price is unknown.

---

## 9. Official URLs of model and rules pages (for the trader to open)

### Takeaway
These are the official pages to verify each model. None could be opened from this environment. URLs marked "(from dossier source list)" were taken from the dossiers' cited-source lists and were not opened.

### Cited Findings
- **FTMO:**
  - 2-Step: https://ftmo.com/en/2-step-challenge/
  - 1-Step: https://ftmo.com/en/1-step-challenge/
  - Trading Objectives: https://ftmo.com/en/trading-objectives/
  - Consistency FAQ: https://ftmo.com/en/faq/do-you-have-any-consistency-rules/
  - Swing: https://ftmo.com/en/faq/ftmo-swing-account-type/
  - Forbidden practices: https://ftmo.com/en/forbidden-trading-practices/
  - VPN/VPS: https://ftmo.com/en/faq/can-i-travel-or-use-vpn-vps/
  - Symbols: https://ftmo.com/en/symbols/
  - Scaling: https://ftmo.com/en/reward-growth-and-scaling-plan/
  - US: https://ftmo.oanda.com
  - — [OFF-SNIP result lists](https://ftmo.com/en/trading-objectives/)
- **The5ers:**
  - High Stakes: https://the5ers.com/high-stakes/
  - Hyper Growth: https://the5ers.com/hyper-growth/
  - Programs overview: https://the5ers.com/challenge-programs-bootcamp-high-stakes-hyper-growth-explained/
  - High Stakes drawdown: https://help.the5ers.com/what-is-the-drawdown-rule-for-high-stakes/
  - Pro Growth: https://help.the5ers.com/new-programprogrowth/
  - Bootcamp: https://help.the5ers.com/how-does-the-bootcamp-program-work/
  - EA FAQ: https://the5ers.com/faqs/can-i-use-an-ea-expert-advisor-can-i-set-a-stealth-mode-stop-loss/
  - Prohibited practices: https://the5ers.com/faqs/prohibited-trading-practices/
  - Assets: https://the5ers.com/asset-specifications/
  - Summer Plan: https://the5ers.com/summer-plan/
  - — [OFF-SNIP result lists](https://the5ers.com/high-stakes/)
- **FundedNext:**
  - Comparison: https://fundednext.com/package-comparison
  - Instant consistency FAQ: https://help.fundednext.com/en/articles/11641328-are-there-any-consistency-rules-for-the-stellar-instant-account
  - Lite rules: https://help.fundednext.com/en/articles/12673505-what-rules-do-i-need-to-follow-in-the-stellar-lite-challenge-at-fundednext-cfd
  - Prohibited strategies: https://help.fundednext.com/en/articles/8020351-what-are-the-restricted-prohibited-trading-strategies
  - On-Demand add-on: https://fundednext.com/blog/fundednext-stellar-on-demand-rewards
  - Model pages, inferred from mirror filenames (not opened): https://fundednext.com/cfds/stellar-instant, https://fundednext.com/cfds/stellar-lite, https://fundednext.com/cfds/stellar-1-step
  - — [OFF-SNIP result lists](https://help.fundednext.com/en/articles/11641328-are-there-any-consistency-rules-for-the-stellar-instant-account); [OFF-MIRROR](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_dossiers/_raw/FundedNext/fundednext.com-cfds-stellar-instant.md)
- **Funding Pips:**
  - 2-Step Standard: https://help.fundingpips.com/hc/en-us/articles/34501809112081-2-Step-Standard
  - 2-Step Pro: https://help.fundingpips.com/hc/en-us/articles/34502027344017-2-Step-Pro-Model
  - Zero: https://help.fundingpips.com/hc/en-us/articles/34502157694865-FundingPips-Zero
  - From dossier source list: https://fundingpips.com/trading-objectives (2-Step Flex rules), https://fundingpips.com/2-step-pro, https://fundingpips.com/1-step-flex, https://fundingpips.com/zero, https://fundingpips.com/rewards
  - — [OFF-SNIP](https://help.fundingpips.com/hc/en-us/articles/34501809112081-2-Step-Standard); [DOSSIER FundingPips](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FundingPips.txt)
- **E8 Markets** (from dossier source list):
  - https://e8markets.com
  - Signature payout caps: https://help.e8markets.com/en/articles/11940573-payout-caps-and-buffers-for-e8-signature-explained
  - Symbols: https://e8x.e8markets.com/trading-symbols
  - A compare page mirrored as "e8markets.com-compare-simfi-funded-accounts". The URL is not confirmed.
  - — [DOSSIER E8Markets](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/E8Markets.txt)
- **FXIFY** (from dossier source list):
  - https://fxify.com/programs/
  - https://fxify.com/programs/one-phase/
  - https://fxify.com/programs/two-phase/
  - https://fxify.com/programs/three-phase-challenge/
  - https://fxify.com/programs/instant-funding/
  - Rules FAQ: https://fxify.com/faqs/rules/
  - — [DOSSIER FXIFY](https://github.com/vedkanani123/rules/blob/f30590c2ca3a30d384f080710f020763c9c5bc62/propfirm_full_dossiers/FXIFY.txt); [OFF-SNIP FXIFY FAQ](https://fxify.com/faqs/rules/)

### Inferences
- Before purchase the trader should open, at minimum:
  - FTMO: the 2-Step and Swing FAQs.
  - FundedNext: the prohibited-strategies article (EA/VPS add-on).
  - Funding Pips: /rewards (cycle-dependent consistency).
  - FXIFY: /programs/one-phase/ (disputed consistency).
  - E8: the On-Demand/payout article (to confirm that Pro and Zero have no best-day rule).

### Gaps
- Exact official URLs for the E8 Pro and E8 Zero Forex model pages, the The5ers Pro Growth and Bootcamp product pages, and the FundedNext model pages could not be confirmed.
