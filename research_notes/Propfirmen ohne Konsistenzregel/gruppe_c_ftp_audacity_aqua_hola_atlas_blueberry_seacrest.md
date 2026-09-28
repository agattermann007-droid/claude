# Group C: consistency rules and MT5-EA facts for Funded Trading Plus, Audacity Capital, AquaFunded, Hola Prime, Atlas Funded, Blueberry Funded and Seacrest Funded (as of September 2026)

Research date: 25 Sep 2026. **Source legend (important):**
- The egress proxy blocked every page fetch attempted. That covers all seven firm domains (fundedtradingplus.com, help.fundedtradingplus.com, audacity.capital, help.audacity.capital, aquafunded.com, help.aquafunded.com, holaprime.com, atlasfunded.com, blueberryfunded.com, help.blueberryfunded.com) and every review or news site tried (propvator, lunefi, thetrustedprop, propfirmbridge, forexpropreviews, tradelocker, bestpropfirm, ofpfunding, fundedfuturesfamily, prnewswire). So **no page was opened**. Every fact below comes from search-engine result summaries.
- The session-wide WebSearch budget (200 calls, shared with the parallel researchers) ran out partway through this task. By then Funded Trading Plus and Audacity Capital were researched in depth. **AquaFunded, Hola Prime, Atlas Funded, Blueberry Funded and Seacrest got only one consistency-focused search each.** Their sections therefore have large gaps. I have left those gaps as "unknown" and not guessed.
- **[OFF-S]** means the statement comes from the firm's own website or help center, seen only as a search snippet or summary. It is official but was not opened.
- **[SEC-S]** means the statement comes from a third-party review or news site, seen only as a search snippet. Treat it as **unverified (secondary source)**.
- The search tool returns a summary built from several result snippets. When a summary did not tie a statement to one URL, I cite the most likely URL(s) from that result list and write "attribution approximate".

## Q0. Across the seven firms, which currently offered models have NO consistency rule? (overview)

### Takeaway
These models are currently sold and reportedly have no consistency rule in any phase:
- **Funded Trading Plus:** 1-Step Express and Instant Funding.
- **Audacity Capital:** all three programs. These are Ability Challenge (2-step), Ability One (1-step) and the Funded Trader Programme (instant). The rule was removed firm-wide.
- **Blueberry Funded:** all plans (1-step, 2-step, Instant), per its help center. A funded "1.5% risk per trade idea" rule and an unclear note dated 17 Aug 2026 still need checking.
- **Atlas Funded:** Instant Zero only, per secondary sources.

These firms have no model that is fully free of a consistency rule:
- **Hola Prime:** there is no consistency rule to pass the challenge, but a 20% rule gates payouts on every funded account, including Direct/instant.
- **AquaFunded:** the instant models carry 15–20% rules. The evaluation models could not be verified.
- **Seacrest Funded:** the prop division reportedly closed with effect from 6 Feb 2026.

### Cited Findings
Overview table. Details and sources are in the firm sections below. MT5, EA and VPS are only listed where known.

| Firm | Model (Sept 2026) | Consistency: evaluation / funded | MT5? | EAs? | VPS? | Evidence |
|---|---|---|---|---|---|---|
| Funded Trading Plus | 1-Step Express | none / none | yes (firm-wide) | yes, no grid/HFT/copy trading | unknown (not confirmed officially) | [OFF-S]+[SEC-S] |
| Funded Trading Plus | Instant Funding | n/a / none | yes (firm-wide) | same | unknown | [OFF-S]+[SEC-S] |
| Funded Trading Plus | 2-Step Classic | 35% per step / 50% per payout period, plus 3% Symbol Loss Limit | yes | same | unknown | [OFF-S] |
| Audacity Capital | Ability Challenge (2-step) | none / none (removed) | yes (MT5 + DXtrade) | yes, own EA, no HFT/arb/DCA | yes, "no server abuse" | [OFF-S] |
| Audacity Capital | Ability One (1-step) | none / none (removed) | yes | same | yes | [OFF-S] |
| Audacity Capital | Funded Trader Programme (instant) | n/a / none | yes | same | yes | [OFF-S] |
| AquaFunded | Instant Funding Standard (old and new) | n/a / 20% (payout gate) | unknown | unknown | unknown | [OFF-S] |
| AquaFunded | Instant Funding Pro | n/a / 15% (bought before 8 Sep 2026); 20% (bought on or after 8 Sep 2026, limited time) | unknown | unknown | unknown | [OFF-S] |
| AquaFunded | Evaluation models, Pay After Pass | unknown | unknown | unknown | unknown | gap |
| Hola Prime | Challenge models (1-Step/2-Step, Prime/Pro) | none / 20% (payout gate) | unknown | unknown | unknown | [SEC-S] |
| Hola Prime | Direct (instant) | n/a / 20% | unknown | unknown | unknown | [SEC-S] |
| Atlas Funded | Instant Zero | none | unknown | unknown | unknown | [SEC-S] |
| Atlas Funded | 2-Step Access / 1-Step / other variants | 25% / 40% / "30% funded on some accounts" | unknown | unknown | unknown | [SEC-S] |
| Blueberry Funded | 1-step, 2-step, Instant | none on any plan (see caveats) | unknown | unknown | unknown | [OFF-S]+[SEC-S] |
| Seacrest Funded | — | firm's prop division closed with effect from 6 Feb 2026 | — | — | — | [SEC-S] |

- Seacrest Markets reportedly closed its prop trading division with effect from 6 February 2026 and moved to CFD brokerage only — [Funded Futures Family](https://www.fundedfuturesfamily.com/seacrest-markets/); [OFP Funding](https://ofpfunding.com/seacrest-funding-is-closing-what-it-means-for-traders-in-2026) [SEC-S]

### Inferences
- For an MT5 EA on XAUUSD and NAS100 with VPS permission confirmed, **Audacity Capital** is currently the best-documented consistency-free option in this group. Its official guidelines explicitly allow EAs and VPS. However, several of its rules act on individual trades, and an EA must code for them:
  - a minimum holding time of 2 minutes;
  - no opening, closing (including TP/SL fills) or adding within ±3 minutes of high-impact news;
  - a cap of 10 lots per position;
  - no averaging into losers.
- **Funded Trading Plus** 1-Step Express and Instant Funding are consistency-free and offer MT5 with EAs allowed. However, VPS permission and the scope of the per-instrument Symbol Loss Limit were not confirmed from official text.
- The Blueberry, Atlas Instant Zero, Hola Prime and AquaFunded entries rest on single snippets. Treat them as leads to verify, not conclusions.

### Gaps
- Not one page could be opened, so no fact here was read directly from a live page. Official content was seen only as snippets.
- The search budget ran out before AquaFunded, Hola Prime, Atlas Funded and Blueberry Funded could be researched for platforms, EA/VPS policy, instruments, risk rules, payouts and prices. All of those remain unknown.

## Q1. Funded Trading Plus (FTP): models, consistency rules and MT5-EA facts

### Takeaway
In 2026 FTP sells three programs: Instant Funding, 1-Step Express and 2-Step Classic. **Only 2-Step Classic has a consistency rule**: 35% of profit per evaluation step and 50% per payout period once funded. **1-Step Express and Instant Funding have none.** MT5 is offered, EAs are allowed (no grid, HFT/latency arbitrage or copy trading), and gold and NAS100 are tradable. A VPS policy could not be confirmed from an official page. Instant Funding (a UK prop firm) acquired FTP on 26 May 2026, and the rules were stated to be unchanged.

### Cited Findings
**Corporate status and line-up**
- Instant Funding announced its acquisition of FTP on 26 May 2026 for a "seven-figure" price. Both brands "will continue to operate independently", with "no immediate changes to accounts, dashboards, trading challenges, payouts, or rules" — [PR Newswire](https://www.prnewswire.com/news-releases/instant-funding-acquires-funded-trading-plus-increasing-group-revenue-by-70-302782025.html); [Morningstar/PRN](https://www.morningstar.com/news/pr-newswire/20260526ln67697/instant-funding-acquires-funded-trading-plus-increasing-group-revenue-by-70); [Finance Magnates](https://www.financemagnates.com/forex/prop-trading-instant-funding-acquires-funded-trading-plus/) [press-release snippets]
- Current programs are Instant Funding, 1-Step Express Challenge and 2-Step Classic Challenge. "In 2026, Funded Trading Plus dropped its older, overlapping program names (Experienced, Prestige, Premium, Advanced, Master) and consolidated everything into three products." — search summary of Sept-2026 reviews, e.g. [PropFirm Terminal](https://www.propfirmterminal.com/firms/funded-trading-plus), [Fortunly](https://fortunly.com/reviews/funded-trading-plus-review/) [SEC-S, attribution approximate]
- The official site lists these program pages: 1-Step ([/prop-trading-challenges/one-step](https://www.fundedtradingplus.com/prop-trading-challenges/one-step), [/1-step](https://www.fundedtradingplus.com/prop-trading-challenges/1-step)), 2-Step ([/two-step](https://www.fundedtradingplus.com/prop-trading-challenges/two-step)), Instant ([/instant-funding](https://www.fundedtradingplus.com/prop-trading-challenges/instant-funding)) and a [compare page](https://www.fundedtradingplus.com/prop-trading-challenges/compare-challenges) [OFF-S, titles/URLs]
- TradingFunder states it rechecked FTP's program pages and help-center rules on 24 May 2026, covering Instant Funding, 1-Step Express, 2-Step Classic, platforms, drawdown, payouts, resets and prohibited strategies — [TradingFunder](https://tradingfunder.com/firms/funded-trading-plus/) [SEC-S]

**Consistency rule (official help center)**
- **2-Step Classic evaluation:** "no single trading day's net profit can represent more than 35% of the total net profit achieved in that step". **Funded stage:** the limit is 50% of total profit in the payout period. Score = highest trading-day profit ÷ total trading-day PnL × 100. The help center showed "last updated 07.02.2026" (the date format is ambiguous: 7 Feb or 2 Jul 2026) — [FTP Help Center: Consistency Rule](https://help.fundedtradingplus.com/consistency-rule/) [OFF-S]
- Funded-stage detail: no single trading day's net simulated profit ("from closed positions only") may exceed 50% of total net profit in the current payout period, counted from funding or the last payout. Example: $100k account with $14k profit gives a maximum best day of $7k. The rule is monitored automatically, and the only effect is that a payout cannot be requested until it is met. The dashboard shows a "Minimum Required Profit" — [FTP Help Center: Consistency Rule](https://help.fundedtradingplus.com/consistency-rule/); [FTP blog](https://www.fundedtradingplus.com/why-consistency-rules-are-a-good-sign-prop-firm/) [OFF-S]
- "Consistency rules appear only on 2-step plans (35% in evaluation, 50% once funded). Instant and 1-step plans skip this requirement entirely." — [TradingFunder](https://tradingfunder.com/firms/funded-trading-plus/); [Lune](https://lunefi.com/blog/funded-trading-plus-complete-guide-to-rules-and-payouts); [TradeLens](https://tradelensapp.com/blog/funded-trading-plus-rules) [SEC-S]
- Official 1-Step page: "the FT+ 1-Step Express, feature[s] no consistency rules … You can pass your profit target and request your first payout immediately" — [FTP 1-Step page](https://www.fundedtradingplus.com/prop-trading-challenges/one-step) / [FTP blog: One Step vs Two Step 2026](https://www.fundedtradingplus.com/one-step-vs-two-step-trading-challenges-which-is-better-for-you-in-2026/) [OFF-S, attribution approximate]. A second official page says: "no consistency rules holding you back, no minimum time limits … request your first performance reward from day one" — [FTP: FTMO 1-Step vs FT+ 1-Step Express](https://www.fundedtradingplus.com/ftmo-1-step-challenge-vs-funded-trading-plus/) [OFF-S, attribution approximate]
- Breaking the consistency rule does not breach or reset the account; the trader keeps trading until the score complies — [Propvator](https://propvator.com/blog/does-funded-trading-plus-have-a-consistency-rule/) [SEC-S]

**Model: 1-Step Express (no consistency rule)**
- Profit target 10%. Daily loss 4%, balance-based, measured from the previous day's closing balance at 4:59 PM EST. Maximum drawdown 6% trailing, which locks once the account is 6% above the starting balance; after that the floor is effectively static. Sizes $10,000–$200,000 — [FundedTrading.com](https://fundedtrading.com/propfirm/funded-trading-plus/); [Myfxbook](https://www.myfxbook.com/prop-firms/funded-trading-plus); [PropFirmsFinder](https://propfirmsfinder.com/prop-firm/funded-trading-plus/); [TradingFunder](https://tradingfunder.com/firms/funded-trading-plus/) [SEC-S]
- Price: "$100,000 1-Step Express challenge at $549 base fee" (live official pricing as reported) — [FundedTrading.com](https://fundedtrading.com/propfirm/funded-trading-plus/) [SEC-S]. Price of the 10k account: **unknown or conflicting**. One summary gives "approximately $99 for $10,000 to $999 for $200,000" without naming the program ([Myfxbook](https://www.myfxbook.com/prop-firms/funded-trading-plus) / [TradingFinder](https://tradingfinder.com/props/funded-trading-plus/), attribution approximate). Another gives an "average price per $10,000 … $199 for 1-step options as of June 2026", which contradicts $549 per $100k — [PropFirmMap](https://propfirmmap.com/firms/fundedtradingplus) [SEC-S]
- Payouts are available from day 0, then every 7 days. Minimum payout $50. Profit split 80%, rising to 90% at 20% total profit and 100% at 30% total profit — [FundedTrading.com](https://fundedtrading.com/propfirm/funded-trading-plus/); [PickMyTrade FAQ](https://pickmytrade.io/prop-firm-faq/funded-trading-plus-faq) [SEC-S, attribution approximate]
- Weekend holding is permitted and news trading is fully permitted on 1-Step Express — [TradingFunder](https://tradingfunder.com/firms/funded-trading-plus/); [Propvator rules](https://propvator.com/funded-trading-plus/rules/) [SEC-S]

**Model: Instant Funding (no consistency rule)**
- No evaluation, "no profit targets or time limits … no hidden restrictions" — [FTP Instant Funding page](https://www.fundedtradingplus.com/prop-trading-challenges/instant-funding) [OFF-S]
- Daily loss cap 6%, calculated from the prior trading day's closed balance (resets at 23:59 server time). Maximum drawdown 6% trailing. No profit target. Profit split starts at 80% and can reach 90–100% — [PropFirmMap](https://propfirmmap.com/firms/fundedtradingplus); [Lune](https://lunefi.com/blog/funded-trading-plus-complete-guide-to-rules-and-payouts); [BestPropFirms](https://www.bestpropfirms.com/reviews/funded-trading-plus/) [SEC-S, attribution approximate]
- Sizes: "Instant Funding is available from $5,000 to $100,000 and has the highest entry costs" — [TradingFinder FTP review (Sept 2026)](https://tradingfinder.com/props/funded-trading-plus/) [SEC-S]. This conflicts with another summary that says "Account sizes run from $10,000 to $200,000 across all three" ([PropFirm Terminal](https://www.propfirmterminal.com/firms/funded-trading-plus), attribution approximate)
- Payouts: "The Instant and 1-Step routes unlock rewards from day one" — [PropFirmMap](https://propfirmmap.com/firms/fundedtradingplus) [SEC-S]

**Model: 2-Step Classic (has a consistency rule; listed for completeness)**
- Official page: "two phases, a consistent 7% simulated target, no time constraints, and a permanent static drawdown". The same page's snippet also mentions a "structured path with trailing drawdown", which is internally inconsistent — [FTP 2-Step page](https://www.fundedtradingplus.com/prop-trading-challenges/two-step) [OFF-S]
- The 2-Step Classic has a 3% **Symbol Loss Limit**: "any single instrument (such as XAU/USD) may not incur more than a 3% simulated equity loss, calculated based on the Balance at 16:59 EST the prior day". Multiple simultaneous trades on the same instrument count as one. Triggering it in any evaluation phase or in the FT+ Trader (funded) phase is a hard breach, and the account is terminated — [FTP Help: 2-Step Classic Program Information](https://help.fundedtradingplus.com/2-step-classic-program-information/); [FTP Help: Symbol Loss Limit](https://help.fundedtradingplus.com/symbol-loss-limit/) [OFF-S]
- **Conflict:** one search summary described a "Symbol Loss Limit at 3% per instrument per day … Breach that and the account is terminated" in the context of 1-Step Express, and said it "applies to both 1-Step and 2-Step challenge programs" — [TradingFunder](https://tradingfunder.com/firms/funded-trading-plus/) / [FTP Help: Symbol Loss Limit](https://help.fundedtradingplus.com/symbol-loss-limit/) (attribution approximate). The official snippets seen name only 2-Step Classic (3%) and the legacy Prestige Lite (2%). Whether it applies to 1-Step Express or Instant Funding is **unverified**.

**Firm-wide: platforms, EAs, VPS, instruments, other rules**
- Platforms: MetaTrader 5, cTrader, DXtrade and Match-Trader — [FTP Help: Which platforms do you offer?](https://help.fundedtradingplus.com/which-platforms-do-you-offer/) [OFF-S]; [DailyForex](https://www.dailyforex.com/forex-brokers/funded-trading-plus-review) [SEC-S]. EAs can be installed on MT4/MT5 — [FTP MetaTrader guides](https://www.fundedtradingplus.com/installing-and-using-metatrader-guides/) [OFF-S]. The snippets did not say whether MT5 is selectable for every program.
- EA policy: EAs and automated strategies are allowed. Grid EAs are explicitly prohibited, and HFT and latency arbitrage are banned. Trend-following, breakout, swing and scalping EAs are permitted without pre-approval. Copy trading "in any form" is prohibited, including EA-based copying between one's own accounts. News trading is allowed without restriction — [EAFunded](https://www.eafunded.com/firms/funded-trading-plus); [Myfxbook](https://www.myfxbook.com/prop-firms/funded-trading-plus) [SEC-S]. The official help article [Does your simulated-live environment support the use of EAs, Algos or Bots?](https://help.fundedtradingplus.com/does-your-simulated-live-environment-support-the-use-of-eas-algos-or-bots/) exists, but its text was not seen.
- VPS: one search summary said "VPS usage is allowed and must have a static IP and be used responsibly". It was not clearly tied to an FTP page and may be generic ([EAFunded](https://www.eafunded.com/firms/funded-trading-plus), attribution uncertain). **Unverified.**
- Instruments: forex majors and exotics, gold, silver, oil, and global indices including NAS100, SPX500 and US30 — [FTP Available Markets](https://www.fundedtradingplus.com/available-markets) [OFF-S]
- Hard rules vs soft rules: breaking a hard rule closes the account; breaking a soft rule closes only the offending position. Inactivity rule: at least one trade (open and close) in any 30-day period — [FTP Help: program information pages](https://help.fundedtradingplus.com/experienced-trader-program-information/) [OFF-S, from legacy-program pages; applicability to current programs assumed but unverified]
- Payout rails are Rise, Deel and crypto, every 7–10 days. Maximum capital $2.5M. Trustpilot 4.4/5 from 2,650+ reviews — [PropFirm Terminal](https://www.propfirmterminal.com/firms/funded-trading-plus) / [Fortunly](https://fortunly.com/reviews/funded-trading-plus-review/) [SEC-S, attribution approximate]

**Legacy programs (reportedly discontinued in 2026; still documented in the help center)**
- Experienced (1-phase): 10% target, 6% relative max DD, 4% daily; overnight and weekend holding allowed. Advanced (2-phase): 10%/5% targets, 10% relative trailing max DD, 5% daily, no weekend holding (close by 4:30 pm EST Friday). Premium (2-phase): 8%/5% targets, 8% relative max DD, 4% daily. Master (instant): 6% relative trailing max DD, 6% daily, no weekend holding — [FTP Help: Experienced](https://help.fundedtradingplus.com/experienced-trader-program-information/), [Advanced](https://help.fundedtradingplus.com/advanced-trader-program-information/), [Premium](https://help.fundedtradingplus.com/premium-trader-program-information/), [Master](https://help.fundedtradingplus.com/master-trader-program-information/) [OFF-S]
- Prestige Lite: 6% target per phase, 6% static max, 3% daily, 2% Symbol Loss Limit, minimum 3 days with ≥0.5% profit per phase. Prestige Pro: 10% target, 10% static max, 5% daily, minimum profitable days — [FTP Help: Prestige Lite](https://help.fundedtradingplus.com/prestige-lite-trader-program-information/); [FTP Help: Prestige Pro](https://help.fundedtradingplus.com/prestige-pro-trader-program-information/) [OFF-S]

### Inferences
- For a gold/NAS100 EA, the 1-Step Express 6% trailing drawdown is tight. It trails until +6% is reached and then locks at the starting balance. Its basis is not confirmed (balance vs equity, intraday vs end-of-day).
- On Instant Funding the 6% daily limit equals the 6% trailing max, so in practice the trailing max is the binding constraint.
- If the 3% Symbol Loss Limit applies beyond 2-Step Classic, an XAUUSD EA would need a hard per-symbol daily equity-loss stop below 3%, because a breach terminates the account. Treat this as a must-verify item.
- The acquisition by Instant Funding (May 2026) has not changed the rules so far. It is still a watch item for future rule changes.

### Gaps
- Official VPS policy text: not confirmed.
- Whether MT5 is available for every program and every size: not confirmed.
- Official 10k price for 1-Step Express, and the price of the smallest Instant Funding account ($5k?): conflicting or unknown.
- Instant Funding weekend-holding and news rules, minimum trading days and first-payout timing: unknown beyond "rewards from day one".
- Whether a max-risk-per-trade, gambling or lot-consistency rule exists on 1-Step Express or Instant Funding: unknown. None was mentioned in the snippets.
- Drawdown basis for 1-Step Express (equity vs balance) and the exact lock level: only a secondary description exists.

## Q2. Audacity Capital: models, consistency rules and MT5-EA facts

### Takeaway
Audacity Capital (London, founded 2012) runs three programs: **Ability Challenge** (2-step), **Ability One** (1-step) and the **Funded Trader Programme (FTP, instant)**. Its official trading guidelines state that **no consistency rule is in place**. Secondary sources say the rule was removed across all three programs. MT5 is offered (with DXtrade). EAs and VPS are officially allowed, but trade-level rules matter for an EA:
- a minimum trade duration of 2 minutes;
- no opening, closing or adding (including TP/SL fills) within ±3 minutes of high-impact news;
- a maximum of 10 lots per open position;
- no HFT, arbitrage, DCA or averaging against the trade;
- no third-party signal EAs.

### Cited Findings
**Consistency rule status**
- Official guidelines: "There is no consistency rule in place. As long as you manage your risk properly and adhere to our risk management guidelines, you can trade according to your strategy without restrictions on profit distribution across trading days." — [Audacity Knowledge Center: Trading Guidelines](https://audacity.capital/knowledge-center/trading-guidelines/) [OFF-S, wording as rendered in snippet]
- Audacity says it removed the consistency rule. Its old help-center article still describes the former rule, which search engines still show, but it "describes a rule Audacity Capital no longer enforces" — [Audacity: Prop Firms With No Consistency Rule in 2026](https://audacity.capital/trading-guides/prop-firms-with-no-consistency-rule/) [OFF-S]; legacy article: [help.audacity.capital Consistency Rule](https://help.audacity.capital/hc/en-gb/articles/21204562218258-Consistency-Rule) [not opened]
- "The consistency rule has been waived across all program tiers (Ability One, Ability Challenge, and Funded Trader Program)" — [TradingFunder](https://tradingfunder.com/firms/audacity-capital/); [PropFirmScope](https://propfirmscope.com/prop-firms/audacity-capital) [SEC-S, attribution approximate]
- FTP: "There is no consistency rule for the FTP" — [Audacity: Instant Funding Prop Firm Rules Explained](https://audacity.capital/trading-guides/instant-funding-prop-firm-rules/) / [Audacity Knowledge Center: FTP](https://audacity.capital/knowledge-center/ftp/) [OFF-S]
- The exact date of removal was not found. Audacity has a 2026 webinar page titled "New Trading Rules & Funding Program Updates 2026" — [Audacity webinar](https://audacity.capital/webinars/new-rules-better-trading/) [OFF-S, title only]

**Firm-wide trading rules relevant to an EA (these act on trades, not on profit distribution)**
- News and weekend: "You may hold trades over the weekend and trade during news events. Simply avoid opening, closing (TP, SL or manual) or adding to positions within 3 minutes before or after any high impact news release or speech." — [Audacity Knowledge Center: Trading Guidelines](https://audacity.capital/knowledge-center/trading-guidelines/) [OFF-S]
- Minimum hold: "Each individual trade must remain open for a minimum of two (2) minutes" — [Audacity: Prohibited Trading Practices](https://audacity.capital/prohibited-trading-practices/); [Trading Guidelines](https://audacity.capital/knowledge-center/trading-guidelines/) [OFF-S]
- EAs "are allowed if they follow prohibited-strategy rules and are not sourced from third-party signals". A VPS "is permitted, provided it is utilized for Expert Advisors (EAs) in a manner that does not result in server abuse". A stop loss is not mandatory. There are no overall lot restrictions, but there is a "maximum limit of 10 lots per open position". Arbitrage, HFT, DCA and other prohibited strategies lead to immediate permanent deactivation. "Continuously increasing position sizes when trades move against the initial market bias — regardless of lot size — is … strictly forbidden" — [Audacity: Prohibited Trading Practices](https://audacity.capital/prohibited-trading-practices/); [Trading Guidelines](https://audacity.capital/knowledge-center/trading-guidelines/); [General Trading Rules](https://audacity.capital/knowledge-center/general/) [OFF-S, attribution approximate across these pages]
- Platforms: MT5 and DXtrade only; no cTrader, Match-Trader, TradingView or MT4 — [TradingFunder](https://tradingfunder.com/firms/audacity-capital/); [PropFirmScope](https://propfirmscope.com/prop-firms/audacity-capital) [SEC-S]. Another review says Audacity "runs MetaTrader 5 and DXtrade" and "allows news trading, weekend holding, EA use, and copy trading". The copy-trading claim is unverified and sits uneasily with the official ban on EAs "sourced from third-party signals" — [TradingFinder](https://tradingfinder.com/props/audacity-capital/) [SEC-S]
- Leverage up to 1:100; funded accounts $7,500–$240,000 (older phrasing) — [TradingFinder](https://tradingfinder.com/props/audacity-capital/) [SEC-S]

**Model: Ability Challenge (2-step), no consistency rule**
- There are two demo challenge stages (Challenge, Verification) and then a live funded stage ("Ability Live"). Time is unlimited. The minimum is 4 trading days in phase 1 and in phase 2, with no minimum on the funded stage. Targets are 10% (Challenge) and 5% (Verification). Sizes: 5K, 10K, 15K, 30K, 60K, 120K, 240K — [Audacity Knowledge Center: Ability Challenge](https://audacity.capital/knowledge-center/ability-challenge/) [OFF-S]
- Challenge phase: "daily drawdown limit is 7.5% of your balance or equity at rollover, whichever is higher"; overall drawdown 15% of starting balance — [Audacity: Ability Challenge page](https://audacity.capital/two-step-prop-firm-ability-challenge/) / [Knowledge Center](https://audacity.capital/knowledge-center/ability-challenge/) [OFF-S]
- Verification and Live: 5% daily drawdown and 10% maximum ("equity must not fall below 90% of the initial account balance … including commissions and swaps") — [Audacity Zendesk: Drawdown](https://audacitycapital.zendesk.com/hc/en-gb/articles/21204575708818-Drawdown); [Audacity Zendesk: daily drawdown by stage](https://audacitycapital.zendesk.com/hc/en-gb/articles/14711458519954-What-is-the-daily-drawdown-on-the-Challenge-Verification-and-Live-account-stage-of-the-Ability-Challenge-and-is-it-based-on-balance-or-equity-) [OFF-S, older help-center domain, may be legacy]. Consistent with the secondary summary "Phase 1 … 7.5% daily and 15% maximum … Phase 2 … 5% daily and 10% maximum" — [TradingFinder](https://tradingfinder.com/props/audacity-capital/) [SEC-S]
- Price: "$10K account is available for $68 with a 14% discount (regular price $79)". The official site says the Ability Challenge "starts from just $17" — [Audacity Ability Challenge page](https://audacity.capital/two-step-prop-firm-ability-challenge/); [Audacity home](https://audacity.capital/) [OFF-S, promo-dependent]
- First payout: "30 days after placing your first trade on the Ability Live phase account". The fee is refunded up to 100% with the first payout — [Audacity Help: payout process and profit split for the Ability Challenge](https://help.audacity.capital/hc/en-gb/articles/11092871596946-What-is-the-payout-process-and-profit-split-for-the-Ability-Challenge) [OFF-S]
- Profit split up to 90%, paid bi-weekly once withdrawal conditions are met. The scaling plan doubles the account at every 10% profit milestone, up to $2,000,000 — [Audacity home](https://audacity.capital/) [OFF-S]

**Model: Ability One (1-step), no consistency rule**
- Single phase with a 10% target. Daily drawdown 3% ("static") and maximum drawdown 6%, "fixed" from the initial balance, in both the Challenge and Funded phases. Time is unlimited, with a minimum of 3 trading days in the challenge and none when funded. A breach of the daily or overall drawdown terminates the account — [Audacity Knowledge Center: Ability One](https://audacity.capital/knowledge-center/ability-one/) [OFF-S]. Older secondary data said 5% daily and 10% overall (superseded) — [TradingFunder review](https://tradingfunder.com/audacity-capital-review/) [SEC-S]
- Profit share starts at 75% and rises to 85% if profits are ≥10%, and up to 90% through scaling. Withdrawals are processed every two weeks. A "Reward Bonus" equal to the registration fee is added to the first withdrawal from Ability Live — [Audacity Knowledge Center: Ability One](https://audacity.capital/knowledge-center/ability-one/) [OFF-S]
- Price: **unknown**

**Model: Funded Trader Programme (FTP, instant funding), no consistency rule**
- "Traders with a verifiable live trading history apply through a brief knowledge and strategy interview and receive immediate live funded capital — from $3,000 to $60,000" — [Audacity home](https://audacity.capital/); [Audacity FTP page](https://audacity.capital/funded-trader-program/) [OFF-S]. There is also an "Instant Funding" landing page — [Audacity Instant Funding](https://audacity.capital/instant-funding/) [OFF-S, title only]
- Rules: 10% profit milestone with unlimited trading days, 5% daily drawdown and 10% maximum drawdown — [Audacity Knowledge Center: FTP](https://audacity.capital/knowledge-center/ftp/) [OFF-S]. The daily 5% is "trailing from the peak intraday equity and is reset at the beginning of a new server day". The 10% maximum is fixed from the original balance — [Audacity: Instant Funding Prop Firm Rules Explained](https://audacity.capital/trading-guides/instant-funding-prop-firm-rules/) [OFF-S]
- Payout mechanics: payout at the 10% profit milestone. The account then goes to a risk-team review (1–3 working days, no trading), the profit is credited to the dashboard wallet, and a new account at double the size is issued. A minimum of 5 trading days applies before requesting payouts — [Audacity Knowledge Center: FTP](https://audacity.capital/knowledge-center/ftp/) [OFF-S]. Another snippet says "Payouts are processed bi-weekly, with the first payout available 14 days after your first live trade", without saying which program — [Audacity FTP page](https://audacity.capital/funded-trader-program/) [OFF-S, ambiguous]
- Profit split is "between 50% and 80% depending on the account size, account stage and the speed of reaching the 10% profit mark" — [Audacity: Instant Funding Prop Firm Rules Explained](https://audacity.capital/trading-guides/instant-funding-prop-firm-rules/) [OFF-S]
- FTP accounts are swap-free and commission-free. Scaling offers "quarterly doubling opportunities (conditions: minimum 2.5% profit monthly and at least one withdrawal)" — [Audacity Knowledge Center: FTP](https://audacity.capital/knowledge-center/ftp/); [Audacity home](https://audacity.capital/) [OFF-S; the doubling mechanism is described differently across snippets]
- Price of the smallest FTP account: **unknown**

**Other**
- Audacity reports more than $250M in trader payouts after 14 years — [Audacity](https://audacity.capital/trading-guides/audacity-capital-250-million-payouts/) [OFF-S, title]. It also runs a free competition, the "Audacity Traders Cup", that awards funded accounts. This is not a paid model — [Audacity Traders Cup](https://audacity.capital/trading-guides/audacity-traders-cup/) [OFF-S, title]

### Inferences
- All three Audacity programs appear consistency-free. It is the only firm in this group where both EA and VPS permission were confirmed in official text, albeit via snippets.
- The ±3-minute high-impact-news window covers TP and SL fills as well as manual closes. An always-on EA on NAS100 and XAUUSD therefore needs a news filter that avoids having pending TP/SL levels likely to fill inside that window. This is the most operationally important Audacity constraint for automation.
- The 2-minute minimum hold rules out fast scalping EAs. The ban on "increasing position sizes when trades move against the initial market bias" rules out grid, martingale and DCA logic.
- Ability One's 3% daily / 6% overall is tight for gold volatility. The Ability Challenge funded stage (5% daily / 10% max, static from initial balance) gives more room.
- The FTP daily drawdown trails from peak intraday equity. For an EA that lets winners run intraday, this is stricter than a balance-based daily limit.

### Gaps
- Exact date the consistency rule was removed: not found.
- Whether XAUUSD and NAS100 are available: not confirmed in any snippet. It is likely for a multi-asset MT5 firm, but **unknown**.
- Ability One price, FTP price or application fee, and whether FTP is purchasable or interview-only: unclear.
- Whether the "Ability Live" funded accounts are real-money or simulated: snippets say "live", but this was not verified.
- The Zendesk drawdown articles may be legacy. Current Verification/Live drawdown values were confirmed only by combining an older help center with a secondary review.

## Q3. AquaFunded: models and consistency rules (partially researched)

### Takeaway
AquaFunded's help center documents a consistency rule on its instant models:
- **20%** on instant funded accounts, as a payout gate rather than a breach.
- **15%** on Instant Funding Pro accounts bought before 8 Sep 2026, and **20%** on those bought on or after 8 Sep 2026 (limited-time promotion).

Whether its evaluation models (1-/2-/3-step) or the "Pay After Pass" model are free of a consistency rule could not be verified before the search budget ran out.

### Cited Findings
- "On instant funded challenges, a consistency rule of 20% applies": one trading day cannot equal or exceed 20% of total profits. If it does, no payout can be requested until the best day falls below 20% of that payout period's profits. The account is not terminated, and the trader continues trading — [AquaFunded Help: Consistency Rule](https://help.aquafunded.com/en/articles/11875903-consistency-rule) [OFF-S]
- "Instant Funding Pro accounts purchased on or after 8 September 2026 will receive a 20% Consistency Rule instead of the standard 15% … for a limited time". Accounts purchased before 8 Sep 2026 remain at 15% — [AquaFunded Help: Instant Funding Pro](https://help.aquafunded.com/en/articles/15281078-instant-funding-pro) [OFF-S]
- The help center has separate articles for "New Instant Funding Standard", "Old Instant Funding Standard" and "Pay After Pass Model", which shows these models exist or existed — [New Instant Funding Standard](https://help.aquafunded.com/en/articles/10476448-instant-funding-models); [Old Instant Funding Standard](https://help.aquafunded.com/en/articles/15281077-old-instant-funding-standard); [Pay After Pass Model](https://help.aquafunded.com/en/articles/13322298-pay-after-pass-model) [OFF-S, titles only]
- A third-party rules page is titled "AquaFunded Rules 2026 – Martingale & Hedging Allowed" — [TradingFinder](https://tradingfinder.com/props/aquafunded/rules/) [SEC-S, title only]

### Inferences
- The help-center wording frames the 20% rule as applying to "instant funded challenges". The evaluation-based models may therefore have no consistency rule, or a different one. This is an unverified inference.

### Gaps
- Full model list for Sept 2026: unknown (1-Step / 2-Step / 3-Step? Pay After Pass details?).
- Consistency status of the evaluation and Pay After Pass models: unknown.
- Platforms (MT5?), EA policy, VPS policy, XAUUSD/NAS100 availability, drawdown rules, payouts and prices: all unknown. The search budget was exhausted, and aquafunded.com and help.aquafunded.com are blocked by the proxy.

## Q4. Hola Prime: models and consistency rules (partially researched)

### Takeaway
According to secondary sources, Hola Prime has **no consistency rule for passing its challenges**. However, it applies **one 20% consistency rule to every funded account, including Direct (instant) accounts**. The rule is checked at payout as a payout gate and does not breach the account. By the task's definition, no Hola Prime model is fully free of a consistency rule. A September 2026 update reportedly removed three limits, including a "60% profit concentration trigger".

### Cited Findings
- "Hola Prime maintains a single 20% consistency rule across its funded accounts, checked at payout, while challenge accounts have no consistency rule to pass". The biggest winning day cannot exceed 20% of total profits, and the same 20% applies to the Direct (Instant) account. A breach holds the payout without cancelling it, and the account stays active — [Propvator: Does Hola Prime have a consistency rule?](https://propvator.com/blog/does-hola-prime-have-a-consistency-rule/) [SEC-S]
- "On-demand payouts require a stricter 40% consistency score instead of the standard 20%". As rendered, this is internally unclear, since 40% would be numerically looser for a best-day cap. It may be a differently defined "score" — [Propvator](https://propvator.com/blog/does-hola-prime-have-a-consistency-rule/) / [Lune](https://lunefi.com/blog/hola-prime-complete-guide-to-rules-and-payouts) [SEC-S, attribution approximate]
- A September 2026 update "focuses on flexibility rather than removing risk controls altogether", and "the first change eliminates the maximum 60% profit concentration trigger" — [Forex Prop Reviews: Hola Prime Major Rule Update Removes 3 Key Limits](https://forexpropreviews.com/hola-prime-major-rule-update-removes-3-key-limits/) [SEC-S]
- A separate article reports that Hola Prime "Updates 1-Step Pro Account with New Consistency Rule" (date and content not seen) — [Forex Prop Reviews](https://forexpropreviews.com/hola-prime-updates-1-step-pro-account-with-new-consistency-rule/) [SEC-S, title only]
- Program names seen in third-party URLs include "1-Step Prime" — [El Trader Financiado](https://www.eltraderfinanciado.com/en/review/hola-prime?program=1-Step+Prime) [SEC-S, title/URL only]

### Inferences
- If the 20% funded payout gate is accurate, an EA with a lumpy profit profile (for example gold breakouts) would see payouts delayed rather than accounts lost. Hola Prime is still outside the "no consistency rule" set.

### Gaps
- Official Hola Prime pages were not surfaced or opened. The current model list, the other two removed limits (Sept 2026) and the new 1-Step Pro rule are unknown.
- MT5 availability, EA/VPS policy, XAUUSD/NAS100, drawdowns, payouts and prices: unknown.

## Q5. Atlas Funded: models and consistency rules (partially researched)

### Takeaway
Secondary sources say Atlas Funded runs several variants: Standard and Pro evaluations, Instant Funded, Instant Zero and Access. Consistency rules differ by model: **none on Instant Zero**, 25% on 2-Step Access and 40% on 1-Step, with a "30% funded consistency rule on some accounts". Instant Zero is the only candidate here, and nothing else about it could be verified.

### Cited Findings
- "The consistency rule differs by model – none on Instant Zero, 25% on 2-Step Access, and 40% on 1-Step". Product variants are "Standard and Pro evaluations, Instant Funded, Instant Zero, and Access", with "a 30% funded consistency rule on some accounts". On Instant Zero, "the trade-off is tighter drawdown and payout-buffer mechanics" — search summary over [Propvator: Atlas Funded Review](https://propvator.com/blog/atlas-funded-review/), [PropFirmBridge](https://propfirmbridge.com/education/atlas-funded-review-2026-is-it-legit-rules-payouts-and-50-off-code), [Top10EX](https://top10ex.com/atlasfunded-prop-firm/) and [TradeLocker Hub](https://tradelocker.com/hub/prop-firms/atlas-funded) [SEC-S, attribution approximate]
- "Atlas Funded has received complaints about its consistency rule as of August 2026" — same search summary [SEC-S, source unclear]
- Atlas Funded publishes its own blog posts on the topic, for example "Prop Firms With No Consistency Rule: 2026 Guide" and "Prop Firms that Allow EA" — [Atlas Funded blog](https://www.atlasfunded.com/post/prop-firms-with-no-consistency-rules); [Atlas Funded blog: EA](https://www.atlasfunded.com/post/prop-firms-that-allow-ea) [OFF-S, titles only; content about Atlas's own models not seen]

### Inferences
- Atlas Funded has a TradeLocker hub listing, so TradeLocker is probably one of its platforms. Whether MT5 is offered is unknown.

### Gaps
- Instant Zero rules (drawdown size and type, "payout buffer", daily loss, split, price), platforms (MT5?), EA/VPS policy and instruments: all unknown.
- Which accounts carry the "30% funded" rule, and what the August 2026 complaints were about: unknown.

## Q6. Blueberry Funded: models and consistency rules (partially researched)

### Takeaway
Blueberry Funded's help center reportedly states that **no consistency rule applies on any plan**: the traditional rule was removed across 1-step, 2-step and Instant. On 12 Mar 2026 it also removed lot-size limits and the all-in and martingale restrictions. Two caveats remain:
- funded accounts reportedly have a **1.5% "risk per trade idea" rule**, which matters for EA position sizing;
- an ambiguous note says accounts bought before 17 Aug 2026 "continue on their existing terms".

### Cited Findings
- "Blueberry Funded does not apply a consistency rule on any of its plans". Traditional consistency rules were removed "across 1-step, 2-step, and Instant Challenges": there is "no payout restriction based on 'best trading day' and no fixed daily profit percentage cap" — [Blueberry Help: Does Blueberry Funded enforce a consistency rule?](https://help.blueberryfunded.com/en/articles/9812246-does-blueberry-funded-enforce-a-consistency-rule-in-trading) [OFF-S]; [Lune: Blueberry Funded Rules](https://lunefi.com/blog/blueberry-funded-rules) [SEC-S]
- "Accounts purchased before 17 August 2026 continue on their existing terms, and no consistency requirement has been applied retrospectively to any account" — same search summary, attributed to the [Blueberry help article](https://help.blueberryfunded.com/en/articles/9812246-does-blueberry-funded-enforce-a-consistency-rule-in-trading) or [Lune](https://lunefi.com/blog/blueberry-funded-rules) [attribution approximate]. **Ambiguous.** It suggests a terms change on 17 Aug 2026 but does not say what changed for new accounts.
- "Starting March 12, 2026, Blueberry Funded removed restrictions like lot size limits, all-in trading, and Martingale strategies" — [Best Prop Firm: Blueberry Funded Simplifies Rules](https://bestpropfirm.com/blueberry-funded-simplifies-rules-boosts-trading-flexibility/) [SEC-S]
- "Funded accounts follow a 1.5% risk per trade idea rule, with an optional 2% add-on for extra drawdown room" — search summary over [Lune](https://lunefi.com/blog/blueberry-funded-an-in-depth-guide-rules-review-and-discount) and [BrokerAnalysis](https://brokeranalysis.com/prop-trading-firms/blueberry-funded/rules/) [SEC-S, attribution approximate; meaning of the "2% add-on" unclear]

### Inferences
- The 1.5% risk-per-trade-idea rule works like a max-risk-per-trade rule. An EA would need a stop loss on every position, with total risk per trade idea (including stacked entries) sized at or below 1.5% of the account. It is not a consistency rule, but it limits how profits can be made.

### Gaps
- Current model names, profit targets, drawdowns, payouts and prices: unknown.
- Platforms (MT5?), EA and VPS policy, XAUUSD/NAS100: unknown.
- What changed on 17 Aug 2026: unknown. This must be checked before relying on "no consistency rule" for new accounts.

## Q7. Seacrest Funded: status

### Takeaway
Seacrest Markets reportedly **closed its prop trading division with effect from 6 February 2026** and is now a CFD broker only. No Seacrest Funded model is currently offered. When it was operating, it had a 35% consistency rule in the challenge phase.

### Cited Findings
- "Seacrest Markets announced the complete closure of its prop trading division effective February 6, 2026, shifting all focus to CFD brokerage operations" — [Funded Futures Family: Seacrest Markets Closes Prop Trading in 2026](https://www.fundedfuturesfamily.com/seacrest-markets/); [OFP Funding: Seacrest Funding closing](https://ofpfunding.com/seacrest-funding-is-closing-what-it-means-for-traders-in-2026) [SEC-S]
- Historical rules (pre-closure): 35% consistency rule during the challenge phase; ban on "bracketing" (simultaneous buy-stop and sell-stop orders placed before an announcement); 1-step and 2-step evaluations required at least 3 profitable days, each with net profit of ≥0.5% of the initial balance — [PropTrusted](https://proptrusted.com/prop-firms/seacrest-funded/); [TradingFinder](https://tradingfinder.com/props/my-funded-fx/rules/) [SEC-S, historical]

### Inferences
- Exclude Seacrest from the September 2026 shortlist.

### Gaps
- The closure was not verified on Seacrest's own site. Both sources are third-party.
- A third-party page titled "Seacrest Funded Review May 2026" exists ([ManuallyReviewed](https://manuallyreviewed.com/seacrest-funded-review/), title only). It is probably a stale or re-dated review, but the conflict with the February 2026 closure could not be resolved.
