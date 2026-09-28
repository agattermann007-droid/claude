# Group B: Goat Funded Trader, Blue Guardian, Maven Trading, Alpha Capital Group, BrightFunded, Instant Funding: account models without a consistency rule (as of 25 Sep 2026)

**Method and verification status (read first).**
- Research date: 25 Sep 2026. The network egress proxy blocked every firm domain and every review site tried. WebFetch returned `EGRESS_BLOCKED` for help.goatfundedtrader.com, www.goatfundedtrader.com, blueguardian.com, alphacapitalgroup.uk, help.brightfunded.com, maventrading.com, instantfunding.com, propvator.com, cryptoslate.com, lunefi.com, fxempire.com and propfirmmatch.com. curl got HTTP 403 on CONNECT for about 70 more prop-firm and review hosts, including help.blueguardian.com, help.maventrading.com, intercom.help and trustpilot.com. **No page could be opened in full.** Every finding below comes from WebSearch result snippets or summaries.
- Tags:
  - **[OFF-SNIP]**: wording from the firm's own help centre or blog, found with a search limited to that domain. It is the firm's own text, but the page itself could not be opened, so it is **unverified**.
  - **[SEC-SNIP]**: a third-party review or aggregator seen only as a search snippet. **Unverified (secondary source).**
  - **[MIXED-SNIP]**: an open search whose summary mixes official and third-party pages. The page behind each sentence cannot be identified, so it is cited to the whole result set. **Unverified.**
- The session-wide WebSearch budget (200 calls, shared with parallel researchers) ran out after the GFT and Blue Guardian deep-dives. Maven, Alpha Capital, BrightFunded and Instant Funding each got only one search, covering the consistency rule. Their MT5, EA, VPS, risk, payout and price facts are **unknown** and need a follow-up pass.
- Out of scope and excluded:
  - Blue Guardian's **futures** line (Standard/Reserve/Express/Direct). Reviews often mix its consistency rules into the CFD rules.
  - **Funded Trader Markets**, a different firm. Its help centre has articles titled "Instant Funding Standard/Pro", which are easily confused with instantfunding.com.

## 1. Which account models are offered (Sep 2026), and which of them have a consistency rule?

### Takeaway
- **Goat Funded Trader (GFT):** only **1-Step** and **Instant Premium** are documented without a consistency rule.
  - These models have a consistency rule: Instant GOAT 15%, Instant HERO 15%, Instant PRO 20%, Instant Blitz 25%, GOAT Blitz 15% and Goat 1$ 15%.
  - Pay Later: funded stage only, 20%, or 30% for accounts purchased from 5 Sep 2026.
  - 2-Step Standard: funded stage only, 15% (secondary source).
  - 3-Step and 2 Step GOAT: unknown.
  - Discontinued: 2-Step PRO (13 Jun 2026) and Instant Standard (22 Sep 2025).
- **Blue Guardian (CFD):** **1 Step Standard** and **2 Step Standard** have no consistency rule. So do the legacy models 1 Step Pro, 2 Step Classic and 3 Step (funded).
  - Instant Standard 20%, Instant Starter 15%.
  - 2 Step Pro: 25% on funded accounts.
  - 1 Step Nano and 2 Step Nano: 50% on funded accounts.
  - BNPL and 1 Step Crypto: unknown.
- **Maven** (secondary sources only): 1-, 2- and 3-Step have no rule during evaluation. After funding, a 50% rule applies only once funded profit passes $5,000. Instant and Mini accounts: 20%.
- **Alpha Capital:** no consistency rule during evaluation. When funded, a 40% best-day rule applies only to **On-Demand** payouts; **Bi-Weekly** payouts have none.
  - Alpha One and Alpha Swing are On-Demand-only, so they carry the rule.
  - Direct/Instant: unknown.
- **BrightFunded** (secondary sources only): no consistency rule on any plan (1-Step, 2-Step Bright, 2-Step Classic), in evaluation or funded ("as of April 2026").
- **Instant Funding:** unresolved. Only generic secondary claims of "no consistency rules" were found.

### Cited Findings

**Goat Funded Trader (GFT)**
- How the rule is defined: "no single trading day can account for X% or more of your total profits during the payout period". The percentage varies by model. Failing the rule is not a breach; it only blocks the payout request until the best day falls below X%. [OFF-SNIP] ([GFT: What Is the Consistency Rule?](https://help.goatfundedtrader.com/en/articles/15290379-what-is-the-consistency-rule))
- **1-Step: no consistency rule.** The help-centre snippet says the 1 STEP model "does not have a consistency rule". [OFF-SNIP] ([GFT 1 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model)) A secondary source agrees: "The 1-Step and Instant Premium accounts have no consistency rule". [SEC-SNIP] ([CryptoSlate GFT Review 2026](https://cryptoslate.com/prop-firms/goat-funded-trader-review/))
  - **Conflict:** another summary of a help-centre search listed a 15% rule under 1-Step. It probably blended in text from the Goat 1$ or Instant GOAT articles. ([GFT 1 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model)) The weight of evidence says none.
- **Instant Premium: no consistency rule.** "Instant Premium accounts do not have a consistency rule. There is no requirement for profits to be spread evenly across trading days." [OFF-SNIP] ([GFT Instant Premium Model](https://help.goatfundedtrader.com/en/articles/16013484-instant-premium-model))
- **Instant GOAT: 15%.** The rule blocks payouts but does not breach the account. [OFF-SNIP] ([GFT Instant Funding GOAT Model](https://help.goatfundedtrader.com/en/articles/13574117-instant-funding-goat-model))
- **Instant HERO: 15%.** [OFF-SNIP] ([GFT Instant HERO Model](https://help.goatfundedtrader.com/en/articles/16097387-instant-hero-model)) A launch report exists: [Forex Prop Reviews: GFT launches Instant HERO](https://forexpropreviews.com/goat-funded-trader-launches-instant-hero-accounts/).
- **Instant PRO ("Instant Funding PRO"): 20%.** [OFF-SNIP] ([GFT Instant Funding PRO Model](https://help.goatfundedtrader.com/en/articles/13574328-instant-funding-pro-model))
- **Instant Blitz: 25%.** [OFF-SNIP] ([GFT Instant Blitz Model](https://help.goatfundedtrader.com/en/articles/13484273-instant-blitz-model))
- **GOAT BLITZ: 15% in each payout period.** It is a 1-step evaluation sold only on "2 random weekends every month", with a 3% target. [OFF-SNIP / SEC-SNIP] ([GFT GOAT BLITZ MODEL](https://help.goatfundedtrader.com/en/articles/11111955-goat-blitz-model); [TheTrustedProp: GOAT BLITZ explained (2026)](https://thetrustedprop.com/blogs/goat-funded-trader-goat-blitz-challenge-explained))
- **Goat 1$: 15%.** It is a $1,000 account for $1. [OFF-SNIP] ([GFT Goat 1$ MODEL](https://help.goatfundedtrader.com/en/articles/11769239-goat-1-model))
- **Pay Later: funded stage only.** It is a 1-phase evaluation with a $5 entry fee. Once funded, the best day must not exceed **20%** of total profit in the payout period, or **30% for accounts purchased from 5 Sep 2026**. [OFF-SNIP] ([GFT PAY LATER MODEL](https://help.goatfundedtrader.com/en/articles/12822025-pay-later-model))
- **2-Step Standard** (targets 10% then 5%): "15% standard, and this applies only once the account is funded". [SEC-SNIP] ([CryptoSlate](https://cryptoslate.com/prop-firms/goat-funded-trader-review/)) The official snippet did not state the percentage. ([GFT 2-Step Standard](https://help.goatfundedtrader.com/en/articles/13575169-2-step-standard))
- **Conflict:** the same CryptoSlate summary also claimed "there is no consistency rule on funded accounts across any evaluation model". The official Pay Later article contradicts this with its 20%/30% funded rule. ([CryptoSlate](https://cryptoslate.com/prop-firms/goat-funded-trader-review/); [GFT PAY LATER MODEL](https://help.goatfundedtrader.com/en/articles/12822025-pay-later-model))
- **2 Step GOAT** (6% target in both steps): consistency rule unknown. ([GFT 2 Step GOAT Model](https://help.goatfundedtrader.com/en/articles/13575348-2-step-goat-model))
- **3-Step** (6% target in each step): consistency rule unknown. The article carries rule changes for accounts bought from 27 Jul 2026, so the model appears to still be sold. [OFF-SNIP] ([GFT 3 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630343-3-step-model))
- **Discontinued:**
  - 2-Step PRO "is no longer available for sale as of June 13, 2026"; existing accounts stay active. [OFF-SNIP] ([GFT 2-Step PRO Model](https://help.goatfundedtrader.com/en/articles/13778401-2-step-pro-model))
  - Instant Standard "is no longer available for sale as of September 22, 2025". [OFF-SNIP] ([GFT Instant Funding Standard Model](https://help.goatfundedtrader.com/en/articles/13574475-instant-funding-standard-model))
- Model index: [GFT Models collection](https://help.goatfundedtrader.com/en/collections/11811982-models) (not opened).

**Blue Guardian (CFD/forex line)**
- **Official consistency article** [OFF-SNIP] ([Blue Guardian: Consistency Rule](https://help.blueguardian.com/en/articles/10690013-consistency-rule)):
  - "On Instant Standard account, a consistency rule of 20% applies."
  - "On Instant Starter account a consistency rule of 15% applies."
  - "The consistency rule does not apply to 1 step Standard, 1 step pro, 2 step standard, 2 step classic and 3 step funded accounts."
  - "On 2 Step Pro funded accounts a consistency rule of 25% applies."
  - A violation does not breach the account; the payout-request button stays unavailable until the rule is met.
- **1 Step Nano:** "For Funded Accounts, the Payout Request button will remain unavailable until the 50% consistency requirement is met." [OFF-SNIP] ([Blue Guardian 1 Step Nano Rules](https://help.blueguardian.com/en/articles/16444654-1-step-nano-rules))
- **2 Step Nano:** "A 50% consistency rule applies to Funded Accounts only." [OFF-SNIP] ([Blue Guardian 2 Step Nano Rules](https://help.blueguardian.com/en/articles/16445450-2-step-nano-rules))
- **Legacy models** labelled as such in the help centre [OFF-SNIP]:
  - [1 Step Pro Rules (Legacy Model)](https://help.blueguardian.com/en/articles/14062228-1-step-pro-rules-legacy-model)
  - [3 Step Rules (Legacy Model)](https://help.blueguardian.com/en/articles/14062468-3-step-rules)
  - [2 Step Pro Rules (Legacy Model)](https://help.blueguardian.com/en/articles/14062433-2-step-pro-rules-legacy-model)
  - A non-legacy [2 Step Pro Rules](https://help.blueguardian.com/en/articles/14062433-2-step-pro-rules) article also exists.
- **Other CFD model articles found:**
  - [Instant Standard](https://help.blueguardian.com/en/articles/14061082-instant-standard-account-rules)
  - [Instant Starter](https://help.blueguardian.com/en/articles/14061939-instant-starter)
  - [1 Step Standard](https://help.blueguardian.com/en/articles/14062186-1-step-standard-rules)
  - [1 Step Crypto](https://help.blueguardian.com/en/articles/14061705-1-step-crypto)
  - [2 Step Standard](https://help.blueguardian.com/en/articles/14062291-2-step-standard-rules)
  - [Buy Now Pay Later (BNPL)](https://help.blueguardian.com/en/articles/15859899-buy-now-pay-later-bnpl-rules)
  - Index: [Account Models collection](https://help.blueguardian.com/en/collections/18967956-account-models)
  - Consistency rules for BNPL and 1 Step Crypto were not captured.
- **Conflicting secondary claims:**
  - "Instant accounts enforce a 20% consistency rule … Pro accounts tighten this to 35%" and "20% on the first payout, 25% on the second, and 30% from the third". [SEC-SNIP] ([LuxAlgo Blue Guardian](https://www.luxalgo.com/prop-firms/blue-guardian/); [Damn Prop Firms: Blue Guardian instant/Direct](https://damnpropfirms.com/prop-firms/blue-guardian-instant-funding-rules/))
  - Damn Prop Firms attributes the 20→25→30% step-up to the "Direct" account. It lists the models "Standard … 40% once funded; Reserve and Express … 40% (or optional 50%) in the evaluation; Direct steps from 20% to 25% to 30%". [SEC-SNIP] ([Damn Prop Firms: Blue Guardian consistency](https://damnpropfirms.com/prop-firms/blue-guardian-consistency-rule-and-drawdown/))
  - Standard/Reserve/Express/Direct is Blue Guardian's 2026 **futures** line-up: "In mid-2026, Blue Guardian rolled out its restructured futures product line … Standard, Reserve, Express, and Direct." [SEC-SNIP] ([Capital Critic: Blue Guardian Futures models](https://www.capitalcritic.ai/blog/blue-guardian-futures-models-explained))
  - These rules therefore do not belong to the CFD models above.

**Maven Trading** (secondary sources only; the official site was blocked and the search budget ran out)
- "Maven Trading's 1-Step, 2-Step, and 3-Step challenge accounts have no consistency score requirement. The rule is exclusive to Instant Funding and Mini accounts." [SEC-SNIP] ([Propvator: Does Maven Trading Have a Consistency Rule?](https://propvator.com/blog/does-maven-trading-have-a-consistency-rule/); [PropTradingVibes: Maven 20% score (2026)](https://www.proptradingvibes.com/blog/maven-trading-consistency-rule))
- **Instant accounts:** "your biggest winning day cannot exceed 20% of total profit". [SEC-SNIP] ([PropTradingVibes](https://www.proptradingvibes.com/blog/maven-trading-consistency-rule))
  - The same summary gives the formula as "(Largest winning trade ÷ Total profit) × 100", so it is unclear whether the rule is based on the day or the trade.
  - If the score is above 20%, the withdrawal is denied until it drops below.
- **1/2/3-Step once funded:** "the 50% best-day cap on the 1 Step, 2 Step and 3 Step accounts only kicks in once your funded profit passes $5,000". [SEC-SNIP]
- "As of April 2026, a separate threshold applies above $5,000 cumulative profit: no single trade can exceed 50% of total profit, and a risk interview is required." [SEC-SNIP]
- Result set for the two claims above: [TheTrustedProp Maven 2026](https://thetrustedprop.com/prop-firms/maven-trading); [MyForexFirms Maven 2026](https://myforexfirms.com/blogs/maven-trading-review-2026); [PropFirmMatch Maven](https://propfirmmatch.com/prop-firms/maven-trading); [Lune Maven rules 2026](https://lunefi.com/blog/maven-trading-complete-guide-to-rules-and-payouts); [TradingFinder Maven rules 2026](https://tradingfinder.com/props/maventrading/rules/)

**Alpha Capital Group**
- "The consistency rule in the funded stage applies only to On-Demand payout accounts, and Alpha Capital does not apply a consistency rule during the evaluation phase or for traders using the Bi-Weekly payout option." [MIXED-SNIP] (result set: [Alpha Capital: Rules Explained 2026](https://alphacapitalgroup.uk/posts/alpha-capital-rules-explained-drawdown-profit-targets-daily-loss-and-evaluation-rules-2026); [TradeTanto Alpha rules](https://tradetanto.com/learn/alpha-capital-group-rules-what-traders-need-to-know); [Lune Alpha rules 2026](https://lunefi.com/blog/alpha-capital-complete-guide-to-rules-and-payouts); [FXEmpire Alpha review 2026](https://www.fxempire.com/prop-firms/alphacapitalgroup))
- "For the Alpha One and Swing plans, the On-Demand payout is mandatory, so the consistency rule must be followed." [MIXED-SNIP] (same set)
- **The rule:** no single trading day may contribute more than **40%** of total profit. Example: with a $1,000 best day, total profit must reach $2,500 before a payout. [MIXED-SNIP] (same set)
- **Current products:**
  - The official product-page title reads "Prop Firm Evaluations | Alpha One, Pro, Swing & Direct". [OFF-SNIP] ([Alpha Capital product page](https://alphacapitalgroup.uk/product))
  - The 2026 update is titled "New Alpha One, Instant Funding, Lower Pro". [OFF-SNIP] ([Alpha Capital 2026 pricing update](https://alphacapitalgroup.uk/resources/alpha-capital-2026-plan-pricing-update))
  - A third-party page still lists "One, Pro, Swing & Three". [SEC-SNIP] ([TradeTanto](https://tradetanto.com/learn/alpha-capital-group-rules-what-traders-need-to-know))

**BrightFunded**
- "BrightFunded does not enforce any consistency rule on evaluation or funded accounts as of April 2026. There is no daily profit cap, no requirement that profits be distributed across multiple days, and no minimum number of profitable sessions." [MIXED-SNIP]
- This "applies to all three current evaluation plans: 1-Step, 2-Step Bright, and 2-Step Classic". [MIXED-SNIP]
- Result set for both claims: [BrightFunded Help: current evaluation rules](https://help.brightfunded.com/en/articles/9241611-what-are-the-current-rules-for-the-evaluation-process); [PropTradingVibes BrightFunded rules 2026](https://proptradingvibes.com/blog/brightfunded-rules-overview); [TradeTanto BrightFunded rules](https://tradetanto.com/learn/brightfunded-rules); [FXEmpire BrightFunded](https://www.fxempire.com/prop-firms/brightfunded); [Lune BrightFunded rules 2026](https://lunefi.com/blog/brightfunded-rules)

**Instant Funding (instantfunding.com)**
- Summaries state that "Instant Funding eliminates the evaluation phase and traders receive funded accounts immediately with no profit targets, no time limits, and no consistency rules". They also mention "simulated accounts ranging from $1,250 to $80,000 with no profit targets or consistency rules required". [SEC-SNIP] (result set: [Lune Instant Funding rules 2026](https://lunefi.com/blog/instant-funding-rules); [Lune Instant Funding review 2026](https://lunefi.com/blog/instant-funding-an-in-depth-guide-rules-review-and-discount); [TTT Markets list](https://tttmarkets.com/articles/10-prop-firms-with-instant-funding-and-no-consistency-rules/); [GFT blog list](https://www.goatfundedtrader.com/blog/prop-firm-instant-funding-no-consistency-rule))
  - These sentences may describe instant funding in general rather than the firm Instant Funding.
- The only official Instant Funding page found is a general explainer, "Consistency Rule Explained | Best-Day Rule in Prop Trading". Its content could not be seen. ([instantfunding.com explainer](https://instantfunding.com/trading-rules-explained-what-is-a-consistency-rule-in-prop-trading/))
- **Do not confuse** with the "Instant Funding Standard/Pro" consistency articles. They belong to **Funded Trader Markets**, a different firm. ([FTM: Instant Funding Standard](https://intercom.help/fundedtradermarkets/en/articles/10020459-what-is-the-consistency-requirement-on-instant-funding-standard-account); [FTM: Instant Funding Pro](https://intercom.help/fundedtradermarkets/en/articles/10152126-is-there-any-consistency-requirement-on-instant-funding-pro-account))

### Inferences
- **Models with no consistency rule at any stage, on the best evidence available:**
  - GFT: 1-Step and Instant Premium.
  - Blue Guardian: 1 Step Standard and 2 Step Standard.
  - BrightFunded: 1-Step, 2-Step Bright and 2-Step Classic (secondary sources only).
  - Alpha Capital: funded accounts paid **Bi-Weekly**. Alpha One and Swing are On-Demand-only, so this is probably Alpha Pro; which plans allow Bi-Weekly needs confirming.
- **Maven 1/2/3-Step:** no rule in evaluation, but a conditional 50% rule once funded profit passes $5,000. On a 10k account that is +50% profit, so in practice it is far off, but it is formally a rule.
- **Match with the trader's needs, within this group.** The trader needs an MT5 EA on XAUUSD and NAS100, running on a VPS, with no consistency rule.
  - **Blue Guardian 1 Step Standard and 2 Step Standard** are the only models where "no consistency", "EAs allowed" and "VPS allowed" are all backed by official snippets. MT5 is probable but not officially confirmed (see §3).
  - GFT's two consistency-free models (1-Step, Instant Premium) are **VPS-banned for purchases from 12 Aug 2026** (see §5).
- **GFT tightens its rules often, keyed to the purchase date.** Examples:
  - 1-Step daily drawdown fell from 4% to 3% from 1 Aug 2026.
  - More valid days were required from 25/27 Jul 2026.
  - VPS ban from 12 Aug 2026.
  - Instant Premium floating-loss limit tightened to −1% from 2 Sep 2026.
  - Pay Later consistency loosened to 30% from 5 Sep 2026.
  - Any account bought later may carry different rules.
- **Blue Guardian's general consistency article does not list the newer Nano models** (50%). The model-specific articles should be treated as authoritative.

### Gaps
- **GFT:**
  - Consistency percentage for 3-Step and 2 Step GOAT.
  - The official percentage for 2-Step Standard (15% comes from a secondary source only).
  - Whether Instant PRO and Instant Blitz are still for sale in Sep 2026.
  - The models collection page could not be opened.
- **Blue Guardian:**
  - Consistency rules for BNPL and 1 Step Crypto.
  - Whether 2 Step Classic is still sold (no current rules article was found).
  - Which "2 Step Pro" article (current or legacy) carries the 25% rule.
- **Maven:** no official confirmation. The official model list for Sep 2026 is unknown, and it is unclear whether the $5,000 rule is based on the best day or the single trade.
- **Alpha Capital:**
  - Which plans can choose Bi-Weekly payouts.
  - Consistency rules for Direct/Instant.
  - Whether Alpha Three still exists.
- **BrightFunded:** no official confirmation; whether any instant or other new models exist is unknown.
- **Instant Funding:** the official model list and per-model consistency rules were not found. Status: unknown.

## 2. Related profit-distribution rules that act like a consistency rule

### Takeaway
Even the "no consistency" models carry distribution-type rules:
- **GFT:**
  - 1-Step funded accounts have a **$3,000 daily profit cap** (the excess is deducted).
  - All GFT news-window trades (±5 min around red-folder news) are **capped at 1% profit** of the initial balance.
  - Payouts need several **"valid" days**, each with at least 0.5% profit.
  - A >80%-margin trade idea is treated as gambling.
- **Blue Guardian:**
  - News-window profits on funded accounts are **removed**.
  - Trades must be held at least **2 minutes**.
  - The **Guardian Shield** acts as a floating-loss limit (see §7).
- **Maven** (secondary source): a **50% single-trade rule plus a risk interview** above $5,000 profit.
- **Alpha Capital** (secondary source): at least **5 trading days "using the same strategy"** before the first Bi-Weekly payout.

### Cited Findings
- **GFT 1-Step, daily profit cap:** funded accounts "have a $3,000 daily profit limit. Profits exceeding this are deducted but do NOT result in an account breach." [OFF-SNIP] ([GFT 1 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model))
- **GFT news profit cap:** "Any trade that is opened or closed within 5 minutes before or after a high-impact news release (marked with a red folder on ForexFactory.com or Myfxbook.com) can generate a maximum profit of 1% of the account's initial balance." This is a profit cap, not a violation. [OFF-SNIP] ([GFT: Is News Trading allowed?](https://help.goatfundedtrader.com/en/articles/10742084-is-news-trading-allowed))
- **GFT gambling rule:** "gambling-style trading" is defined as "any trade where more than 80% of available margin is used in a trading idea". [OFF-SNIP] ([GFT: All or Nothing strategies](https://help.goatfundedtrader.com/en/articles/10742096-does-goat-funded-trader-allow-all-or-nothing-trading-strategies))
- **GFT valid-day requirements:** a valid trading day is one with profit of at least 0.5% of the initial balance. [OFF-SNIP] ([GFT 1 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model)) Required counts:
  - 1-Step payout: at least 3 valid days. ([GFT 1 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model))
  - Instant Premium: at least 5, not necessarily consecutive. ([GFT Instant Premium](https://help.goatfundedtrader.com/en/articles/16013484-instant-premium-model))
  - Instant GOAT: at least 5. ([GFT Instant GOAT](https://help.goatfundedtrader.com/en/articles/13574117-instant-funding-goat-model))
  - Instant HERO: at least 6. ([GFT Instant HERO](https://help.goatfundedtrader.com/en/articles/16097387-instant-hero-model))
  - 2-Step Standard funded: 4 days for accounts bought on or after 25 Jul 2026. ([GFT 2-Step Standard](https://help.goatfundedtrader.com/en/articles/13575169-2-step-standard))
  - 3-Step funded: 4 days for accounts bought on or after 27 Jul 2026. ([GFT 3 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630343-3-step-model))
  - All [OFF-SNIP]. General article: [GFT minimum trading days](https://help.goatfundedtrader.com/en/articles/13860595-what-are-the-minimum-trading-days).
- **Goat 1$ lifetime cap:** withdrawable profit is capped at $100 for the life of the account. [OFF-SNIP] ([GFT Goat 1$ MODEL](https://help.goatfundedtrader.com/en/articles/11769239-goat-1-model))
- **GFT 2-minute rule:** a separate article exists ("What is the rule about trades lasting less than 2 minutes?"); its content was not captured. ([GFT 2-minute rule](https://help.goatfundedtrader.com/en/articles/12849041-what-is-the-rule-about-trades-lasting-less-than-2-minutes))
- **Blue Guardian news rule (funded):** "refrain from Opening/Closing trades 5 minutes before and 5 minutes after red folder (high-impact) news events. Any profits earned during this time or significantly influenced by news events will be subject to removal." News trading is allowed in the challenge. [OFF-SNIP] ([Blue Guardian Platform Rules](https://help.blueguardian.com/en/articles/9661525-platform-rules); [2 Step Nano Rules](https://help.blueguardian.com/en/articles/16445450-2-step-nano-rules))
- **Blue Guardian minimum hold:** "The minimum holding time is 2 minutes. If a trade is closed in under 2 minutes, it may be flagged for tick scalping." [OFF-SNIP] (Blue Guardian model rules articles, e.g. [1 Step Standard](https://help.blueguardian.com/en/articles/14062186-1-step-standard-rules) and [2 Step Standard](https://help.blueguardian.com/en/articles/14062291-2-step-standard-rules))
- **Maven:** above $5,000 cumulative profit, "no single trade can exceed 50% of total profit, and a risk interview is required" (as of April 2026). [SEC-SNIP] ([MyForexFirms Maven 2026](https://myforexfirms.com/blogs/maven-trading-review-2026); [TheTrustedProp Maven](https://thetrustedprop.com/prop-firms/maven-trading))
- **Alpha Capital:** [MIXED-SNIP] ([Alpha Capital: Rules Explained 2026](https://alphacapitalgroup.uk/posts/alpha-capital-rules-explained-drawdown-profit-targets-daily-loss-and-evaluation-rules-2026); [Lune Alpha](https://lunefi.com/blog/alpha-capital-complete-guide-to-rules-and-payouts))
  - On-Demand payouts need at least 2% gross profit.
  - The first Bi-Weekly payout needs "a minimum of 5 trading days using the same strategy".
- **BrightFunded:** "no daily profit cap … no minimum number of profitable sessions". [MIXED-SNIP] ([PropTradingVibes BrightFunded](https://proptradingvibes.com/blog/brightfunded-rules-overview); [BrightFunded Help](https://help.brightfunded.com/en/articles/9241611-what-are-the-current-rules-for-the-evaluation-process))

### Inferences
- **GFT 10k 1-Step:** the $3,000 daily cap is 30% of the account and practically irrelevant. The news cap (1% = $100 on 10k) matters for a NAS100/XAUUSD EA around US releases unless the EA filters out red-folder news.
- **Blue Guardian funded accounts:** news-window profits are removed, not merely capped. An EA needs a ±5-minute red-folder filter, and must hold every trade for at least 2 minutes.
- **Valid-day rules:** at GFT and Blue Guardian (3 trading days), payout timing depends on the number of qualifying days. This works like a distribution requirement even without a formal consistency rule. The user's own EA report (local file `DEADBAND/DEADBAND_LIVE4_660_Bericht.md`) identifies GFT's valid days as the bottleneck; this was not independently re-checked here.

### Gaps
- GFT: content of the "trades < 2 minutes" and [Risk limitation Policy](https://help.goatfundedtrader.com/en/articles/10742114-risk-limitation-policy) articles, and whether the $3,000 daily cap also applies to Instant Premium or other models.
- Maven, Alpha, BrightFunded and Instant Funding: news, gambling, lot-size and trade-consistency rules are unknown.

## 3. Platforms: is MetaTrader 5 available?

### Takeaway
GFT offers MT5, along with MatchTrader, cTrader and TradeLocker. Blue Guardian appears to offer MT5 to non-US clients; US clients are limited to Match-Trader and TradeLocker. Platforms for Maven, Alpha Capital, BrightFunded and Instant Funding are **unknown**, because the search budget ran out.

### Cited Findings
- **GFT:** "MT5, MatchTrader, and cTrader are among the available trading platforms." [OFF-SNIP] ([GFT: Which platforms can I trade on?](https://help.goatfundedtrader.com/en/articles/10741900-which-platforms-can-i-trade-on)) The commission article names MT5, MatchTrader and TradeLocker. [OFF-SNIP] ([GFT commissions](https://help.goatfundedtrader.com/en/articles/10742044-how-does-the-commission-work-for-different-trading-instruments))
- **Blue Guardian:**
  - "Blue Guardian restricts US clients to using Match Trader and TradeLocker only." [OFF-SNIP] ([Blue Guardian Platform Rules](https://help.blueguardian.com/en/articles/9661525-platform-rules))
  - Monthly competitions "are held exclusively on the Match-Trader and MT5 platform". [OFF-SNIP] ([Blue Guardian Competition](https://help.blueguardian.com/en/articles/10209820-blue-guardian-competition))
  - "Blue Guardian supports MT5 along with other trading platforms like Match Trader and TradeLocker" for the 1-Step Standard. [SEC-SNIP] ([PropFirmMatch Blue Guardian](https://propfirmmatch.com/prop-firms/blue-guardian))

### Inferences
- MT5 on Blue Guardian challenge accounts for non-US traders is probable, but no official snippet stated it directly.

### Gaps
- Per-model platform availability at GFT, for example whether Instant Premium is sold on MT5. (The user's own account runs on MT5, per the local project.)
- Maven, Alpha Capital, BrightFunded and Instant Funding: platform lists were not retrieved. Status: unknown.

## 4. Are Expert Advisors / automated trading allowed?

### Takeaway
- **GFT:** EAs are allowed but must be **the trader's own**. Third-party or off-the-shelf EAs lead to a breach, and GFT may ask to see the code. HFT, gold-arbitrage EAs and martingale/grid recovery are prohibited, and so is hedging.
- **Blue Guardian:** EAs are allowed ("that you setup to suit your own strategy"). Trades must be held at least 2 minutes. Trade copiers may only link accounts owned by the same person.
- **Maven, Alpha Capital, BrightFunded, Instant Funding:** unknown.

### Cited Findings
- **GFT: EAs allowed, with limits.** "Yes, you can use Expert Advisors as long as the EAs comply with the prohibited trading practices rule. However, you are not allowed to use high-frequency trading (HFT) strategies / systems and/or Gold Arbitrage EA." [OFF-SNIP] ([GFT: Can I use Expert Advisors (EAs)?](https://help.goatfundedtrader.com/en/articles/10749630-can-i-use-expert-advisors-eas))
- **GFT: own EA only.** "Utilizing any third-party strategy, Expert Advisor, off-the-shelf strategy or one marketed to pass assessment accounts will lead to a breach of your account or reward." GFT "may require you to prove that your Expert advisor is your own by presenting the code". [OFF-SNIP] ([GFT EAs](https://help.goatfundedtrader.com/en/articles/10749630-can-i-use-expert-advisors-eas); [GFT Prohibited Trading Practices](https://help.goatfundedtrader.com/en/articles/10742118-what-are-prohibited-trading-practices))
- **GFT: no martingale or grid.** Martingale or grid-based recovery systems "may result in account termination and forfeiture of any associated profits". [OFF-SNIP] ([GFT EAs](https://help.goatfundedtrader.com/en/articles/10749630-can-i-use-expert-advisors-eas))
- **GFT: hedging.** Hedging means "opening two opposite positions on the same asset, regardless of differences in lot size". Detected hedging, "especially between a GFT account and an external firm", leads to an immediate breach and a permanent ban. [OFF-SNIP] ([GFT: Is hedging allowed?](https://help.goatfundedtrader.com/en/articles/10742101-is-hedging-allowed))
- **GFT: owner only.** Accounts "must be operated solely by the account owner", and sharing logins is prohibited. [OFF-SNIP] ([GFT Prohibited Trading Practices](https://help.goatfundedtrader.com/en/articles/10742118-what-are-prohibited-trading-practices))
- **Blue Guardian: EAs allowed.** "EAs are allowed. You may use EAs (Expert Advisors) that you setup to suit your own strategy or trading style." [OFF-SNIP] (model rules articles, e.g. [1 Step Standard](https://help.blueguardian.com/en/articles/14062186-1-step-standard-rules), [2 Step Standard](https://help.blueguardian.com/en/articles/14062291-2-step-standard-rules))
- **Blue Guardian: copy trading.** Third-party trade-copier software is permitted "as long as it complies with our rules"; all copied trades must be "between accounts legally owned by the same account holder". [OFF-SNIP] (same articles)
- **Blue Guardian: minimum hold.** "The minimum holding time is 2 minutes", and shorter trades may be flagged as tick scalping. [OFF-SNIP] (same articles)

### Inferences
- A self-developed MT5 EA, like the user's DEADBAND EA, fits both firms' EA policies as far as the snippets show. The conditions are:
  - no grid/martingale and no opposite positions on the same symbol at GFT;
  - a hold time of at least 2 minutes at Blue Guardian;
  - being able to show the source code if GFT asks.

### Gaps
- Maven, Alpha Capital, BrightFunded and Instant Funding: EA and automation policies are unknown.
- GFT: whether the "trades < 2 minutes" rule also applies to EAs (content not captured).

## 5. Is a VPS / remote server allowed (with policy-change dates)?

### Takeaway
- **GFT:** for accounts **purchased from 12 Aug 2026**, VPS use is **strictly prohibited on One Step, Two Step, Instant Premium and Pay Later**.
  - It is **allowed on Instant GOAT and Instant HERO**, but both have a 15% consistency rule.
  - Accounts bought before 12 Aug 2026 are unaffected.
  - So **no GFT model bought today is both consistency-free and VPS-permitted.**
- **Blue Guardian:** **VPN and VPS are allowed**, but must not be used to get around copy-, group- or signal-trading rules.
- **Maven, Alpha Capital, BrightFunded, Instant Funding:** unknown.

### Cited Findings
- **GFT ban list:** "For all accounts purchased from August 12, 2026 onwards, the use of a VPS (Virtual Private Server) is strictly prohibited on the following account types: One Step, Two Step, Instant Premium, and Pay Later." [OFF-SNIP] ([GFT: IP Address and Account Access Policy](https://help.goatfundedtrader.com/en/articles/10742103-ip-address-and-account-access-policy))
- **GFT exceptions:** the ban applies "with the exception of Instant GOAT and Instant Hero accounts, which are allowed to use VPS. Accounts purchased before August 12, 2026 are not affected by this new VPS restriction." [OFF-SNIP] (same article)
- **GFT general stance:** "accessing any trading account through VPN or VPS is strongly discouraged". IP addresses are monitored, with the data "obtained directly from the trading platform". [OFF-SNIP] (same article)
- **Secondary reports:**
  - "Using a VPN, VPS, or sharing login credentials will lead to instant suspension of the account … IP tracking". [SEC-SNIP] ([PropfirmXL: GFT hidden rules](https://propfirmxl.com/goat-funded-trader-hidden-rules/))
  - Some traders report account bans for alleged VPS use. [SEC-SNIP] ([NYC Servers: GFT review 2026](https://newyorkcityservers.com/blog/goat-funded-trader-review); [Trustpilot GFT](https://www.trustpilot.com/review/goatfundedtrader.com))
- **Blue Guardian:** "While VPNs and VPS are allowed, using either service to bypass rules related to copy trading, group trading, or signal trading is strictly prohibited. If you are found misusing these services … your account will be failed and terminated." [OFF-SNIP] (model rules articles, e.g. [Instant Standard](https://help.blueguardian.com/en/articles/14061082-instant-standard-account-rules), [2 Step Standard](https://help.blueguardian.com/en/articles/14062291-2-step-standard-rules); policy index: [Prohibited Trading Practices & Account Policies](https://help.blueguardian.com/en/articles/9661512-prohibited-trading-practices-account-policies))

### Inferences
- **The user's own GFT Instant Premium 10k account** (dated 2 Sep 2026 in the local report) falls under the VPS ban, which is consistent with its plan to run the EA only on its own PC.
- **GFT models not named on the ban list** (3-Step, 2 Step GOAT, GOAT Blitz, Goat 1$, Instant PRO, Instant Blitz): their VPS status is unclear. One snippet summary read the rule as "prohibited … with the exception of Instant GOAT and Instant Hero", which would mean all other models are banned.
- **Blue Guardian 1 Step Standard and 2 Step Standard** are the only models in this group with official, snippet-level backing for all three: VPS allowed, EAs allowed, no consistency rule.

### Gaps
- GFT: the full wording for models not on the list, and whether a remote desktop into a home PC counts as a VPS.
- Blue Guardian: whether the VPS permission applies equally to all CFD models (the snippets came from model rules articles).
- Maven, Alpha Capital, BrightFunded and Instant Funding: VPS policies and any change dates are unknown.

## 6. Are XAUUSD (gold) and NAS100 (US100/USTEC) tradable?

### Takeaway
GFT and Blue Guardian both list metals/gold and indices. The exact symbol names (XAUUSD, NAS100/US100/USTEC) were not confirmed in any snippet. The other four firms: unknown.

### Cited Findings
- **GFT instruments:** "FX pairs, CFD indices, metals, commodities, stocks and cryptocurrencies". [OFF-SNIP] ([GFT: What instruments can I trade?](https://help.goatfundedtrader.com/en/articles/10741905-what-instruments-can-i-trade))
- **GFT commissions:** on MT5, MatchTrader and TradeLocker, $0 per lot on indices, commodities and stocks and "$5 for metals with raw spread on all assets". [OFF-SNIP] ([GFT commissions](https://help.goatfundedtrader.com/en/articles/10742044-how-does-the-commission-work-for-different-trading-instruments))
- **Blue Guardian instruments:** "FX, Indices, Gold & Commodities, and Cryptos". [OFF-SNIP] ([Blue Guardian: What instruments can I trade?](https://help.blueguardian.com/en/articles/9661542-what-instruments-can-i-trade))

### Inferences
- Gold is explicitly tradable at Blue Guardian, and metals at GFT. NAS100 is very likely among the "indices" at both firms; the user's local EA project already trades XAUUSD and NAS100 on GFT. It is still not confirmed for Blue Guardian by symbol name.

### Gaps
- Symbol lists and trading hours for NAS100 and XAUUSD at Blue Guardian.
- Maven, Alpha Capital, BrightFunded and Instant Funding: instrument lists are unknown.

## 7. Core risk rules of the models WITHOUT a consistency rule

### Takeaway
- **GFT 1-Step** (bought from 1 Aug 2026): 10% target (secondary source), 3% daily loss, 6% static maximum loss, at least 3 valid days before payout.
- **GFT Instant Premium:** no target, 3% daily loss, 6% trailing maximum loss (wording unclear on end-of-day vs. intraday). Floating loss is a hard breach at −1.5%, or **−1% for purchases from 2 Sep 2026**. At least 5 valid days before a payout.
- **Blue Guardian 1 Step Standard:** 10% target, 4% daily loss, 6% trailing maximum that locks at the starting balance after +6%, at least 3 trading days.
- **Blue Guardian 2 Step Standard:** 8% / 4% targets, 4% daily loss, 8% maximum loss.
- **Blue Guardian, both models:** the **Guardian Shield** closes all trades when floating loss reaches 2%. On a funded account, the first activation permanently cuts the profit split to 50% and the second closes the account.
- **Weekend holding:** allowed at both firms. GFT forbids trades opened purely to exploit the weekend gap.
- **Maven, Alpha Pro, BrightFunded:** unknown.

### Cited Findings

**GFT 1-Step**
- Profit target 10%. Secondary sources give "4% maximum daily drawdown and a 6% overall drawdown limit, paired with a 10% profit target"; the 4% is the rule from before Aug 2026. [SEC-SNIP] ([TradingFinder GFT rules 2026](https://tradingfinder.com/props/goat-funded-trader/rules/); [Forex Prop Reviews: GFT One-Step](https://forexpropreviews.com/goat-funded-traders-one-step-evaluation-rules-targets/))
- Daily loss: "For 1-Step accounts purchased from August 1st, 2026 onward, the Daily Drawdown Limit is 3% instead of 4%." It is measured from the higher of balance or equity at 5:00 PM EST. [OFF-SNIP] ([GFT 1 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model))
- Maximum loss: "Account equity or balance must never drop below 94% of starting capital", which is a static 6%. [OFF-SNIP] (same article)
- Payout eligibility: at least 3 trading days, each with at least 0.5% profit. [OFF-SNIP] (same article)
- Funded daily profit cap of $3,000 (see §2). [OFF-SNIP] (same article)

**GFT Instant Premium**
- Daily loss: "The maximum daily loss limit is 3% of your daily starting balance … calculated daily at 5 PM EST based on your account balance or equity". The article also says "Your equity must not drop by more than 3% of your initial account balance in a single trading day". [OFF-SNIP] ([GFT Instant Premium Model](https://help.goatfundedtrader.com/en/articles/16013484-instant-premium-model))
- Maximum loss: "a trailing drawdown set at 6% of the equity value". It rises when equity rises and does not fall when equity drops. The same article calls it a "6% Trailing End-of-Day Maximum Drawdown", so **intraday vs. end-of-day is ambiguous**. [OFF-SNIP] (same article)
- Floating loss: "if floating loss reaches -1.5% of account balance at any moment, the account will be permanently closed". "For all challenges purchased from September 2nd, 2026 onwards, the Floating Loss hard breach threshold is -1% instead of -1.5%." This applies independently of the daily and maximum limits. [OFF-SNIP] (same article)
- Payout eligibility: "at least 5 trading days before requesting a reward … minimum profit of 0.5% of initial balance", not necessarily consecutive. [OFF-SNIP] (same article)

**Related GFT Instant models, for comparison (all have a 15% consistency rule)**
- Instant GOAT: 3% daily loss (5 PM EST, balance or equity), 6% trailing on equity, at least 5 valid days. [OFF-SNIP] ([GFT Instant GOAT](https://help.goatfundedtrader.com/en/articles/13574117-instant-funding-goat-model))
- Instant HERO: 3% daily loss, 1% maximum floating loss (a breach closes the account), 5% trailing end-of-day maximum, at least 6 valid days. [OFF-SNIP] ([GFT Instant HERO](https://help.goatfundedtrader.com/en/articles/16097387-instant-hero-model))

**GFT general rules**
- Weekend: "Traders are allowed to hold trades over the weekend. However, opening trades solely to take advantage of the price gap … on Monday is not allowed." [OFF-SNIP] ([GFT weekend](https://help.goatfundedtrader.com/en/articles/10742082-can-i-hold-trades-over-the-weekend); [GFT weekend gap](https://help.goatfundedtrader.com/en/articles/14123389-do-you-allow-trading-the-weekend-gap))
- News: profit capped at 1% within ±5 minutes of red-folder news (see §2). [OFF-SNIP] ([GFT news](https://help.goatfundedtrader.com/en/articles/10742084-is-news-trading-allowed))

**Blue Guardian 1 Step Standard** [OFF-SNIP] ([Blue Guardian 1 Step Standard Rules](https://help.blueguardian.com/en/articles/14062186-1-step-standard-rules))
- Profit target 10%.
- Daily loss: "limited to 4% of the initial account balance", resetting daily at 5 PM EST.
- Maximum loss: "The maximum trailing drawdown is set at 6% of the highest balance or equity reached". "Once your account reaches 6% profit from the initial balance, the trailing drawdown will lock at your starting balance."
- Minimum days: at least 3 trading days to pass, and "Minimum 3 trading days required before requesting payouts".

**Blue Guardian 1 Step Nano**, for comparison (it has a 50% funded consistency rule): 4% daily loss using the higher of balance or equity at reset; the trailing drawdown locks at the starting balance at +6%, and a 1% buffer is then added. [OFF-SNIP] ([1 Step Nano Rules](https://help.blueguardian.com/en/articles/16444654-1-step-nano-rules))

**Blue Guardian 2 Step Standard** [OFF-SNIP] ([Blue Guardian 2 Step Standard Rules](https://help.blueguardian.com/en/articles/14062291-2-step-standard-rules))
- Targets 8% (Phase 1) and 4% (Phase 2).
- Daily loss 4% of the initial balance.
- "The maximum total loss allowed in 2 Step Standard account is 8%" (the type was not stated in the snippet).
- Guardian Shield payout conditions: "First Breach: Profit split is reduced to 50%. Second Breach: The account is permanently breached."

**Blue Guardian Guardian Shield**
- "1-Step, 2-Step, and 3-Step challenge accounts use a 2% Guardian Shield threshold." An activation is a "soft breach": trading can resume.
- On funded accounts, the "first activation reduces profit split from 80% to 50%. Second activation closes the account … changes are permanent".
- Source: [OFF-SNIP], a 2025 blog, so the "80%" may be outdated; the help centre now states an 85% base split. ([Blue Guardian blog: Guardian Shield 2025](https://blueguardian.com/blogs/funded-account-trading-rules-2025))
- Third-party summary: "If your PnL on open trades reaches a 2% loss (1% loss on instant account), Guardian Shield will, in most cases, automatically close all open trades for all symbols." [SEC-SNIP] ([Damn Prop Firms](https://damnpropfirms.com/prop-firms/blue-guardian-consistency-rule-and-drawdown/))

**Blue Guardian weekend and news**
- "There are no restrictions on holding trades over night or the weekend on all account types." [OFF-SNIP] ([Blue Guardian Platform Rules](https://help.blueguardian.com/en/articles/9661525-platform-rules))
- News on funded accounts: ±5-minute restriction, with profits removed (see §2). [OFF-SNIP] (same article)

**Conflict (Blue Guardian)**
- A third-party summary says "Drawdown is end-of-day trailing on every model and locks after your first payout; daily loss limits are soft". [SEC-SNIP] ([Damn Prop Firms](https://damnpropfirms.com/prop-firms/blue-guardian-consistency-rule-and-drawdown/))
- This probably describes the futures line and contradicts the CFD help-centre wording ("highest balance or equity"; lock at +6%).

### Inferences
- **Combined open risk is capped at both firms.** An EA holding XAUUSD and NAS100 at the same time must keep total open loss below:
  - **1% of the balance** on a GFT Instant Premium bought from 2 Sep 2026 (a hard breach); the user's account likely falls under this, which needs checking;
  - **2%** at Blue Guardian (a soft close in the challenge; on a funded account a permanent cut to a 50% split, and closure on the second activation).
  - In effect this is a maximum risk-per-position rule.
- **Blue Guardian's trailing maximum** follows the "highest balance or equity". Intraday equity peaks may therefore raise the floor until the +6% lock.
- **GFT 1-Step's 6% static maximum** is more EA-friendly than a trailing limit, but the model is VPS-banned for new purchases.

### Gaps
- GFT 1-Step: whether a floating-loss rule applies; the official profit target.
- GFT Instant Premium: whether the trailing drawdown ever locks (for example at the initial balance).
- Blue Guardian 2 Step Standard: minimum days, the maximum-loss type (static or trailing) and the daily-loss basis.
- Maven, Alpha Capital, BrightFunded and Instant Funding: all core risk rules are unknown.

## 8. Payouts (first payout, frequency, profit split, minimum)

### Takeaway
- **GFT:** bi-weekly payouts on the 1-Step (80% split), Instant GOAT (80%) and Instant HERO (90%). Split and cycle for Instant Premium were **not captured**.
- **Blue Guardian:** first payout 14 days after the first trade, then every 14 days, minimum $100. Base split 85% on 1 Step and 2 Step Standard; a 7-day/90% add-on is available.
- **Alpha Capital** (secondary source): Bi-Weekly payouts on a 14-day cycle, minimum $100.
- **Maven, BrightFunded, Instant Funding:** unknown.

### Cited Findings
- **GFT 1-Step:** "Payout Cycle: Bi-weekly (Every 14 days)"; "Profit Split: 80%". [OFF-SNIP] ([GFT 1 STEP MODEL](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model)) The 80% appeared in the summary that also had the conflicting 15% claim. Bi-weekly was confirmed twice.
- **Other GFT models** [OFF-SNIP]:
  - Instant GOAT: 80%, bi-weekly. ([Instant GOAT](https://help.goatfundedtrader.com/en/articles/13574117-instant-funding-goat-model))
  - Instant HERO: 90%, bi-weekly. ([Instant HERO](https://help.goatfundedtrader.com/en/articles/16097387-instant-hero-model))
  - GOAT BLITZ: 80%, bi-weekly. ([GOAT BLITZ](https://help.goatfundedtrader.com/en/articles/11111955-goat-blitz-model))
  - Goat 1$: bi-weekly, $100 lifetime cap. ([Goat 1$](https://help.goatfundedtrader.com/en/articles/11769239-goat-1-model))
  - 2-Step Standard and 3-Step: 80%. ([2-Step Standard](https://help.goatfundedtrader.com/en/articles/13575169-2-step-standard); [3-Step](https://help.goatfundedtrader.com/en/articles/10630343-3-step-model))
- **GFT Pay Later:** after a payout, the trailing drawdown "is reset to 6% below the initial balance (in the funded stage)". [OFF-SNIP] ([GFT PAY LATER MODEL](https://help.goatfundedtrader.com/en/articles/12822025-pay-later-model))
- General GFT article, not captured: [All about Rewards and Profit Splits](https://help.goatfundedtrader.com/en/articles/9549359-all-about-rewards-and-profit-splits).
- **Blue Guardian:** [OFF-SNIP] ([Blue Guardian: How do payouts work?](https://help.blueguardian.com/en/articles/9660857-how-do-payouts-work))
  - "The first payout occurs 14 days after the first trade", then every 14 days counted from the previous request.
  - "The minimum withdrawal amount is $100."
  - Processed "within 24 business hours".
  - Optional 7-day payout add-on.
  - Add-on article: [7-Day Payout and 90% Profit Split Add-On](https://help.blueguardian.com/en/articles/10967614-how-to-benefit-from-our-7-day-payout-and-90-profit-split-add-on).
  - Base split of 85% for 1 Step Standard and 2 Step Standard. [OFF-SNIP] ([1 Step Standard](https://help.blueguardian.com/en/articles/14062186-1-step-standard-rules); [2 Step Standard](https://help.blueguardian.com/en/articles/14062291-2-step-standard-rules))
  - A secondary source lists "90% profit split, and weekly 90% payout" for the 1-Step Standard 10K, probably including the add-on or a promotion. [SEC-SNIP] ([PropFirmMatch Blue Guardian](https://propfirmmatch.com/prop-firms/blue-guardian))
- **Alpha Capital:** [MIXED-SNIP] ([Alpha Capital: Rules Explained 2026](https://alphacapitalgroup.uk/posts/alpha-capital-rules-explained-drawdown-profit-targets-daily-loss-and-evaluation-rules-2026); [Lune Alpha](https://lunefi.com/blog/alpha-capital-complete-guide-to-rules-and-payouts))
  - "Biweekly payouts follow a 14-day cycle starting from your first trade on the qualified account."
  - "The minimum payout amount is $100 in gross profits."
  - The first Bi-Weekly payout needs at least 5 trading days using the same strategy.
  - On-Demand payouts need at least 2% gross profit.

### Inferences
- A funded Blue Guardian Standard account has its first possible payout about 14 days after the first funded trade. The 3-trading-day minimum is not a bottleneck at that pace.

### Gaps
- GFT Instant Premium: split, cycle and minimum payout were not captured. The local EA report assumes 5 valid days, 10 days and a $131.25 minimum profit; this was not verified here.
- Profit splits for Alpha Capital plans.
- Maven, BrightFunded and Instant Funding: payout terms are unknown.

## 9. Price of the smallest account (ideally 10k)

### Takeaway
Only a few prices were found, all from undated, promotion-dependent secondary listings:
- Blue Guardian 1 Step Standard 10K: $48.50 on discount ($97 regular).
- GFT Instant GOAT 10K: $79 on discount ($158 regular).
- GFT Pay Later: $5 entry fee, then an activation fee after passing.
- GFT Goat 1$: $1.

Prices for GFT 1-Step 10K and Instant Premium 10K, and for the other four firms, are unknown.

### Cited Findings
- Blue Guardian 1 Step Standard 10K: "$48.50 (regular $97.00)". [SEC-SNIP] ([PropFirmMatch Blue Guardian](https://propfirmmatch.com/prop-firms/blue-guardian))
- GFT GOAT Instant 10K: "$79.00 (regular price $158.00)". [SEC-SNIP] ([PropFirmMatch GFT GOAT Instant 10K](https://propfirmmatch.com/prop-firm-challenges/goat-funded-trader---goat---instant-10k))
- GFT Pay Later: "$5 entry fee … the balance fee ranges from $78 on a $5,000 account to $598 on a $100,000 one". [SEC-SNIP] ([CryptoSlate](https://cryptoslate.com/prop-firms/goat-funded-trader-review/))
- GFT Goat 1$: "The only available account size … is $1,000, and it costs just $1." [OFF-SNIP] ([GFT Goat 1$ MODEL](https://help.goatfundedtrader.com/en/articles/11769239-goat-1-model))
- Instant Funding account sizes are said to range from "$1,250 to $80,000". [SEC-SNIP] ([Lune Instant Funding rules](https://lunefi.com/blog/instant-funding-rules))

### Inferences
- Both PropFirmMatch prices look like roughly 50%-off promotions, so list prices are about double.

### Gaps
- GFT 1-Step 10K, GFT Instant Premium 10K and Blue Guardian 2 Step Standard 10K prices.
- All prices for Maven, Alpha Capital, BrightFunded and Instant Funding.
- The date of every PropFirmMatch price.

## 10. Official URLs of model and rules pages

### Takeaway
Official rules pages exist for every GFT and Blue Guardian model listed above; they were identified but could not be opened. For the other four firms only a few official URLs appeared in search results.

### Cited Findings
- **GFT help centre (models):**
  - [1 STEP](https://help.goatfundedtrader.com/en/articles/10630134-1-step-model)
  - [2-Step Standard](https://help.goatfundedtrader.com/en/articles/13575169-2-step-standard)
  - [2 Step GOAT](https://help.goatfundedtrader.com/en/articles/13575348-2-step-goat-model)
  - [2-Step PRO (discontinued)](https://help.goatfundedtrader.com/en/articles/13778401-2-step-pro-model)
  - [3 STEP](https://help.goatfundedtrader.com/en/articles/10630343-3-step-model)
  - [Instant Premium](https://help.goatfundedtrader.com/en/articles/16013484-instant-premium-model)
  - [Instant GOAT](https://help.goatfundedtrader.com/en/articles/13574117-instant-funding-goat-model)
  - [Instant HERO](https://help.goatfundedtrader.com/en/articles/16097387-instant-hero-model)
  - [Instant PRO](https://help.goatfundedtrader.com/en/articles/13574328-instant-funding-pro-model)
  - [Instant Standard (discontinued)](https://help.goatfundedtrader.com/en/articles/13574475-instant-funding-standard-model)
  - [Instant Blitz](https://help.goatfundedtrader.com/en/articles/13484273-instant-blitz-model)
  - [GOAT BLITZ](https://help.goatfundedtrader.com/en/articles/11111955-goat-blitz-model)
  - [Goat 1$](https://help.goatfundedtrader.com/en/articles/11769239-goat-1-model)
  - [Pay Later](https://help.goatfundedtrader.com/en/articles/12822025-pay-later-model)
  - [Models collection](https://help.goatfundedtrader.com/en/collections/11811982-models)
- **GFT help centre (rules):**
  - [Consistency Rule](https://help.goatfundedtrader.com/en/articles/15290379-what-is-the-consistency-rule)
  - [IP/VPS policy](https://help.goatfundedtrader.com/en/articles/10742103-ip-address-and-account-access-policy)
  - [EAs](https://help.goatfundedtrader.com/en/articles/10749630-can-i-use-expert-advisors-eas)
  - [Prohibited practices](https://help.goatfundedtrader.com/en/articles/10742118-what-are-prohibited-trading-practices)
  - [News](https://help.goatfundedtrader.com/en/articles/10742084-is-news-trading-allowed)
  - [Weekend](https://help.goatfundedtrader.com/en/articles/10742082-can-i-hold-trades-over-the-weekend)
  - [Platforms](https://help.goatfundedtrader.com/en/articles/10741900-which-platforms-can-i-trade-on)
  - [Instruments](https://help.goatfundedtrader.com/en/articles/10741905-what-instruments-can-i-trade)
  - [Rules collection](https://help.goatfundedtrader.com/en/collections/11969353-rules)
  - [Inactivity](https://help.goatfundedtrader.com/en/articles/10742197-is-there-any-inactivity-limit) (not captured)
- **Blue Guardian help centre (CFD models):**
  - [Account Models](https://help.blueguardian.com/en/collections/18967956-account-models)
  - [1 Step Standard](https://help.blueguardian.com/en/articles/14062186-1-step-standard-rules)
  - [2 Step Standard](https://help.blueguardian.com/en/articles/14062291-2-step-standard-rules)
  - [1 Step Nano](https://help.blueguardian.com/en/articles/16444654-1-step-nano-rules)
  - [2 Step Nano](https://help.blueguardian.com/en/articles/16445450-2-step-nano-rules)
  - [2 Step Pro](https://help.blueguardian.com/en/articles/14062433-2-step-pro-rules)
  - [Instant Standard](https://help.blueguardian.com/en/articles/14061082-instant-standard-account-rules)
  - [Instant Starter](https://help.blueguardian.com/en/articles/14061939-instant-starter)
  - [BNPL](https://help.blueguardian.com/en/articles/15859899-buy-now-pay-later-bnpl-rules)
- **Blue Guardian help centre (rules):**
  - [Consistency Rule](https://help.blueguardian.com/en/articles/10690013-consistency-rule)
  - [Platform Rules](https://help.blueguardian.com/en/articles/9661525-platform-rules)
  - [Payouts](https://help.blueguardian.com/en/articles/9660857-how-do-payouts-work)
  - [Prohibited practices](https://help.blueguardian.com/en/articles/9661512-prohibited-trading-practices-account-policies)
  - [Maximum Daily Loss](https://help.blueguardian.com/en/articles/9661421-what-is-the-maximum-daily-loss)
- **Alpha Capital (official):** [Product overview](https://alphacapitalgroup.uk/product); [Rules Explained 2026](https://alphacapitalgroup.uk/posts/alpha-capital-rules-explained-drawdown-profit-targets-daily-loss-and-evaluation-rules-2026); [2026 pricing update](https://alphacapitalgroup.uk/resources/alpha-capital-2026-plan-pricing-update)
- **BrightFunded (official):** [Current evaluation rules](https://help.brightfunded.com/en/articles/9241611-what-are-the-current-rules-for-the-evaluation-process)
- **Instant Funding (official):** only a generic [consistency-rule explainer](https://instantfunding.com/trading-rules-explained-what-is-a-consistency-rule-in-prop-trading/) was found.

### Inferences
- The GFT and Blue Guardian help centres are the authoritative sources. Every [OFF-SNIP] fact above should be re-checked by opening those pages from a network that can reach them.

### Gaps
- No official model or rules URLs were found for **Maven Trading** (maventrading.com and help.maventrading.com were blocked, and no search was left).
- No per-model pages were found for **Instant Funding** or **BrightFunded**, nor for Alpha Capital's One/Pro/Swing/Direct model pages.
