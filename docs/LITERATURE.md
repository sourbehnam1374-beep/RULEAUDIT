# Literature grounding for RuleAudit

This document grounds the RuleAudit protocol in the published methodology of
clinical-decision-rule (CDR) appraisal, sensitivity analysis, model-selection
theory, and the orthopedic rules used as worked examples. It is the evidence
base behind `METHODOLOGY.md`: where that document *defines* the six tests, this
one says *where each idea comes from* and *what gap RuleAudit fills* relative to
the established literature.

The short version: the CDR literature has mature standards for the
**derivation → validation → impact** lifecycle, but those standards are almost
entirely *data-dependent* — they assume you already have a cohort. RuleAudit
occupies the under-served slot *before* derivation data exists: a **data-free,
structural** pre-check of an expert-authored rule. It does not replace TRIPOD,
PROBAST, or prospective validation; it screens for pathologies that those
data-driven tools are not designed to catch and that no outcome study can later
repair.

---

## 1. The CDR lifecycle: derivation, validation, impact

The canonical framing of a clinical decision (prediction) rule is a **three-stage
lifecycle**, set out in McGinn et al.'s *Users' Guides to the Medical Literature*
(JAMA, 2000):

1. **Derivation** — identify candidate predictors and assemble them into a rule.
2. **Validation** — show the rule performs on data not used to build it
   (narrow → broad/external validation).
3. **Impact analysis** — show that *using* the rule changes clinician behaviour
   and improves outcomes or efficiency.

A rule's "level of evidence" rises as it climbs these stages; impact analysis is
the most demanding and the rarest. Reviews of CDR methodology consistently find
that the large majority of published rules never progress beyond derivation, and
that methodological quality at the derivation stage is uneven.

**Where RuleAudit sits.** Every stage above presumes data. An expert-derived rule
(weights set by consensus, not fitted) can be written down with *zero* derivation
cohort — and that is exactly when its structural pathologies are cheapest to fix
and most expensive to discover later. RuleAudit is a **stage-zero** check: it
operates on the rule's *function*, sampling synthetic inputs over declared
physiologic bounds, so five of its six tests need no patient data at all. This is
complementary to the McGinn lifecycle, not a substitute for any stage of it.

---

## 2. Reporting and risk-of-bias standards: TRIPOD and PROBAST

Two instruments dominate modern prediction-model appraisal:

- **TRIPOD** (Transparent Reporting of a multivariable prediction model for
  Individual Prognosis Or Diagnosis), 2015 — a **22-item reporting checklist**
  for diagnostic/prognostic model studies. Updated as **TRIPOD+AI** (2024) and,
  in protocol, **TRIPOD-AI** for machine-learning models.
- **PROBAST** (Prediction model Risk Of Bias ASsessment Tool), Wolff et al.,
  *Ann Intern Med* 2019 — a risk-of-bias and applicability instrument with
  **20 signalling questions across four domains: participants, predictors,
  outcome, and analysis**. Its successor **PROBAST+AI** (Moons et al., *BMJ*
  2025) splits assessment into model-development (16 questions) and
  model-evaluation (18 questions) parts over the same four domains.

Both are aimed at *studies that fit and report a model on data*. PROBAST's
"analysis" domain, for instance, asks about sample size, handling of missing
data, and optimism/overfitting — questions that simply do not apply to a rule
whose weights were never fitted.

**Where RuleAudit sits.** RuleAudit is best read as a structural pre-filter that
*feeds* a future TRIPOD report and *anticipates* PROBAST's "predictors" and
"analysis" concerns at the point where the rule is still just a function. A
driver that is dead (Test I), collinear (Tests II–III), or part of a sprawling,
non-identifiable label (Test V) is a predictor-domain problem that PROBAST would
eventually flag — but PROBAST needs a fitted model and a cohort to flag it.
RuleAudit flags it on day one. The protocol's own "What this protocol does *not*
claim" section is deliberately scoped to leave TRIPOD/PROBAST/prospective trials
in place as the downstream authorities.

---

## 3. Sensitivity analysis: why Sobol, and why not OAT alone (Test IV)

RuleAudit's Test IV pairs **one-at-a-time (OAT)** sweeps with **variance-based
(Sobol) global sensitivity indices**, and the choice is principled.

- **OAT** varies one input while holding the rest fixed at a reference point. It
  is intuitive and cheap, but the sensitivity-analysis literature (Saltelli and
  colleagues) is emphatic that OAT **cannot detect interactions** between inputs
  and explores only a thin slice of input space around the reference point. For a
  rule whose drivers fire on *combinations* of inputs, OAT systematically
  understates the importance of inputs that act indirectly.
- **Variance-based / Sobol' indices** decompose output variance into
  contributions from each input and its interactions. The **first-order index
  S₁** captures an input's direct effect; the **total-order index S_T** (Homma &
  Saltelli, 1996) captures its direct effect *plus all interactions*. The theory
  traces to Sobol' (1990/1993) and is consolidated in Saltelli et al.'s *Global
  Sensitivity Analysis: The Primer* (2008).

A large gap between S_T and S₁ is precisely the signature of an input that "hides"
in OAT — RuleAudit's `hidden_interaction` flag. The GAP worked example is the
textbook case: pelvic incidence has S₁ ≈ 0.02 but S_T ≈ 0.36 because it shifts
three ideal-target formulae at once.

**Caveat carried into the report.** Sobol variance decomposition assumes
**independent inputs**, so RuleAudit's Sobol/OAT stage samples uniformly and
independently over declared bounds rather than through any correlated
`joint_sampler` — a deliberate, documented mismatch with the firing/correlation
tests. (This is now noted both in `core.py` and in the generated report.)

---

## 4. Complexity and the MDL view of "calibration debt" (Test VI)

Test VI quantifies how many *bits* an expert rule wastes relative to a fitted
baseline, using the **Minimum Description Length (MDL)** principle.

- MDL (Rissanen, 1978) selects the model that minimises the total code length of
  *model plus data given model*. In the **two-part code**,
  **L(D; M) = L(M) + L(D | M)** — the cost to describe the model plus the cost to
  describe the data's residuals under it.
- The crucial property, stressed by Grünwald (*The Minimum Description Length
  Principle*, 2007), is that the complexity penalty **arises from coding theory
  rather than an ad-hoc heuristic** — distinguishing MDL from criteria like AIC
  whose penalty term is more arbitrary. MDL also needs no assumption that the data
  came from a "true" model.

RuleAudit operationalises this as **calibration debt**: the description-length
difference between the expert rule and the best L1-regularised logistic-regression
baseline on the same features. Positive debt means a simpler fitted model would
describe the outcomes at least as cheaply; debt that *grows* with cohort size
signals permanent structural inefficiency rather than small-sample noise. This is
the protocol's only outcome-dependent test, and the MDL framing is what lets
"the expert rule is over-built" be stated as a number of bits rather than an
opinion.

> Note on weights and VIF (Test III): MDL also clarifies why multicollinearity
> matters even for *unfitted* expert rules. If two drivers are collinear, the
> rule spends weight bits (L(M)) describing a signal it has already encoded —
> redundant model description length with no reduction in L(D | M).

---

## 5. The orthopedic worked examples — why these three

The three bundled rules were chosen because each cleanly exhibits one of the
failure modes RuleAudit targets.

### Lewinnek "safe zone" (1978) — mechanism erasure
The Lewinnek safe zone defines acetabular cup targets of **40° ± 10°
inclination** and **15° ± 10° anteversion** on supine radiographs. It is one of
the most-cited rules in hip arthroplasty, yet:
- Abdel et al. (CORR, 2016, "What Safe Zone?") found that **58% (120/206) of
  *dislocated* THAs had cups inside the Lewinnek safe zone** — mean inclination
  44° ± 8° (84% in zone) and anteversion 15° ± 9° (69% in zone). The zone failed
  to discriminate the very outcome it was meant to prevent.
- Subsequent work established that a **functional (dynamic) safe zone** accounting
  for spinopelvic mobility outperforms the static Lewinnek box, and that the
  original references are **frequently misquoted**, with the thresholds resting on
  a small original sample.

This is RuleAudit's **mechanism-erasure** signature: a single broad label (SAFE)
spans so much anatomy that it cannot stratify risk within itself.

### GAP score (Yilgor et al., JBJS 2017) — mechanism sprawl & hidden interactions
The Global Alignment and Proportion (GAP) score predicts mechanical complications
after adult-spinal-deformity surgery from pelvic-incidence-based proportional
parameters (relative pelvic version, relative lumbar lordosis, lordosis
distribution index, relative spinopelvic alignment, plus an age factor). In its
original derivation/validation (222 patients, split 148/74) it reported an
excellent validation AUC of **0.92**, with mechanical-complication rates of 6% /
47% / 95% across the proportioned (0–2) / moderately (3–6) / severely (>7)
disproportioned categories.

It illustrates two pathologies RuleAudit targets:
- **Hidden interaction load** — pelvic incidence drives the score only
  *indirectly*, through three ideal-target formulae at once (caught by Sobol, not
  OAT). This is not just an artifact of the audit: an independent study found
  GAP's components are themselves strongly intercorrelated — relative pelvic
  version tracks the Schwab pelvic-tilt modifier (ρ = −0.84) and relative lumbar
  lordosis tracks the PI-LL modifier (ρ = −0.94) — empirical confirmation of the
  collinearity that Tests II–III flag.
- **Mechanism sprawl** — many distinct driver patterns collapse onto the same
  total at category boundaries. The structural prediction is that such a rule
  will validate *inconsistently* across cohorts, and the external-validation
  record bears this out: against the original AUC of 0.92, independent cohorts
  report anywhere from "no discriminatory power" (AUC 0.50, Bari 2019; AUC 0.60,
  Kwan 2020) to moderate (AUC 0.84, Ham 2021), with a 2023 meta-analysis pooling
  to only **AUC ≈ 0.69 ("poor discrimination")** across 2,092 patients. This
  scatter is exactly the downstream signature mechanism sprawl predicts.

### SHIVA SPIN-THA (Sour, 2026) — driver inflation
The author's own internal spinopelvic THA score is preserved as an audit
reference precisely because it fails loudly: exactly-collinear drivers
(r = 1.00 between mobility flags and their delta-SS sources, VIF → ∞), a dead
driver, and inert inputs — the **driver-inflation** failure mode that motivated
building RuleAudit in the first place.

### Pitfalls of expert-derived scores, generalised
Across these examples the recurring hazards are the well-known weaknesses of
consensus scoring systems, each mapped to a RuleAudit test:

| Pitfall of expert scores | RuleAudit test |
|---|---|
| Arbitrary / unidentifiable weight assignment | III (VIF), VI (MDL debt) |
| Threshold & band-edge effects (step responses, off-by-ε cuts) | IV-a (OAT step-shaped), and the documented `.1` band-edge offsets in `rules/gap.py` |
| Overlapping / double-counted criteria | II (orthogonality), III (VIF) |
| Dead or always-on criteria | I (firing rates) |
| Labels too broad / too sprawling to generalise | V (identifiability) |

---

## 6. Net positioning

RuleAudit is a **data-free, structural audit** that is **complementary to**, not
competitive with, the established CDR toolchain:

- It runs **before** McGinn's derivation stage, when no cohort exists.
- It screens for **predictor- and structure-level** problems that **PROBAST**
  would eventually attribute to a fitted model and **TRIPOD** would expect a
  study to report — but does so on the bare rule.
- Its sensitivity stage uses **Sobol/Saltelli** total-order indices because
  expert rules are full of input *interactions* that **OAT** alone misses.
- Its complexity stage uses **MDL** so "this rule is over-built" is a bit count,
  not an aesthetic judgement.

A clean RuleAudit report is necessary but **not sufficient**: peer review,
external validation, and prospective impact analysis remain the authorities on
whether a structurally sound rule is also *clinically* useful.

---

## Sources

The clinical anchors and the PROBAST framework facts have been **verified against
the peer-reviewed primary literature**: the Abdel 2016 dislocation figures
(58% within zone; 44°±8° / 15°±9°), the GAP score's design and 0.92 validation
AUC with its 6/47/95% category rates, GAP's inconsistent external validation and
component collinearity, and PROBAST's "20 signalling questions / four domains"
structure are all drawn from the source articles below. The other framework
definitions (TRIPOD item count, the McGinn three stages, the Sobol/OAT and MDL
distinctions) are corroborated across multiple scholarly sources. Exact
author/year details for classic methods papers should be checked against the
primary article before manuscript citation.

- McGinn et al., *Users' Guides to the Medical Literature, XXII: How to use articles about clinical decision rules*, JAMA 2000 — three-stage lifecycle. See discussion: [Guiding Outcomes with Clinical Prediction Rules](https://rehabpub.com/industry-news/research/guiding-outcomes-with-clinical-prediction-rules/)
- [Methodological standards for the development and evaluation of clinical prediction rules: a review of the literature](https://d-nb.info/119734635X/34)
- [Framework for the impact analysis and implementation of Clinical Prediction Rules (CPRs) — PubMed](https://pubmed.ncbi.nlm.nih.gov/21999201/?dopt=Abstract)
- [Clinical Prediction Rules for Physical Therapy Interventions: A Systematic Review (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2636674/)
- PROBAST (four domains, 20 signalling questions): [PROBAST: A Tool to Assess the Risk of Bias and Applicability of Prediction Model Studies](https://consensus.app/papers/details/17a2602fae335f9b81b077edee90cd0c/) (Wolff et al., 2019, Annals of Internal Medicine) · E&E: [PROBAST Explanation and Elaboration](https://consensus.app/papers/details/bd14473cef8b554497cbed42a08d7a94/) (Moons et al., 2019)
- PROBAST+AI update: [PROBAST+AI: an updated quality, risk of bias, and applicability assessment tool](https://consensus.app/papers/details/a5c81c0c866c5d92bd13b33ac4b45e5a/) (Moons et al., 2025, The BMJ)
- TRIPOD / AI extensions: [Protocol for TRIPOD-AI and PROBAST-AI (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8273461/) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/34244270/)
- [A roadmap to fair and trustworthy prediction model validation in healthcare (arXiv)](https://arxiv.org/pdf/2304.03779)
- Variance-based sensitivity analysis (Sobol/Saltelli, total-order indices, OAT limits): [Sensitivity analysis: a coming of age (INRIA HAL)](https://inria.hal.science/inria-00386559/document) · [Variance-based sensitivity analysis: the quest for better estimators (arXiv)](https://arxiv.org/pdf/2203.00639) · [Global Sensitivity Analysis: The Primer (ResearchGate)](https://www.researchgate.net/publication/253328104_Global_Sensitivity_Analysis_The_Primer)
- MDL: [The Minimum Description Length principle in model selection (DiVA)](https://www.diva-portal.org/smash/get/diva2:456685/fulltext01.pdf) · [Minimum description length — Scholarpedia](http://www.scholarpedia.org/article/Minimum_description_length) · [Revisiting MDL complexity in overparameterized models (arXiv)](https://arxiv.org/pdf/2006.10189)
- Lewinnek safe zone — primary evidence: [What Safe Zone? The Vast Majority of Dislocated THAs Are Within the Lewinnek Safe Zone for Acetabular Component Position](https://consensus.app/papers/details/49bb0bf658405d4ea10101744ae32ebd/) (Abdel et al., 2016, Clin Orthop Relat Res) · systematic review: [Acetabular cup position and risk of dislocation in primary THA](https://consensus.app/papers/details/de5c172e1f6152178b11ec49bdee144e/) (Seagrave et al., 2016, Acta Orthop — "the Lewinnek safe zone could not be justified")
- GAP score — derivation & validation: [Global Alignment and Proportion (GAP) Score: Development and Validation](https://consensus.app/papers/details/9f3647df3a19589e926d02412a82e127/) (Yilgor et al., 2017, JBJS, validation AUC 0.92)
- GAP score — inconsistent external validation: [Bari et al., 2019, Spine Deformity (AUC 0.50)](https://consensus.app/papers/details/0c2907a80f1e5e04bb157279b8e0f0de/) · [Kwan et al., 2020, Clin Orthop Relat Res (AUC 0.60)](https://consensus.app/papers/details/ddcf8e4269c95017b4cffe5ef47514fb/) · [Ham et al., 2021, Eur Spine J (AUC 0.84)](https://consensus.app/papers/details/7ab2df66e374547abfd9bbff6e7e40c7/) · [Gendreau et al., 2023, World Neurosurg — meta-analysis, pooled AUC 0.69](https://consensus.app/papers/details/8f762808fa8252889c3d1b898e88556b/)
- GAP score — component collinearity: [Jacobs et al., 2019, The Spine Journal (GAP RPV vs Schwab PT ρ=−0.84; RLL vs PI-LL ρ=−0.94)](https://consensus.app/papers/details/80d69b9f356d5ff8abb1efb8c3d773c8/)
