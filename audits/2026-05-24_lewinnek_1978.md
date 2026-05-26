# Lewinnek safe zone (1978) — RuleAudit Report

**N synthetic cases:** 10,000
**Drivers analysed:** 4

## Headline diagnostics

- **Identifiability**: COLLAPSE: total=0.0 has 5209.0 cases collapsing to 1.0 patterns (div=0.000)
- **Identifiability**: COLLAPSE: total=1.0 has 4055.0 cases collapsing to 4.0 patterns (div=0.001)
- **Identifiability**: COLLAPSE: total=2.0 has 736.0 cases collapsing to 4.0 patterns (div=0.005)

## 1. Driver firing rates

|          |   fire_rate |   mean_contrib |
|:---------|------------:|---------------:|
| av_high  |       0.168 |           0.17 |
| av_low   |       0.161 |           0.16 |
| inc_high |       0.158 |           0.16 |
| inc_low  |       0.066 |           0.07 |

## 2. Driver orthogonality

Maximum off-diagonal |r| = 0.000

![Correlation heatmap](fig_correlation.png)

## 3. Variance Inflation Factor

|          |   VIF |
|:---------|------:|
| av_low   | 1.04  |
| av_high  | 1.04  |
| inc_low  | 1.014 |
| inc_high | 1.013 |

![VIF](fig_vif.png)

## 4. Sensitivity analysis

|                 |    S1 |    ST |
|:----------------|------:|------:|
| cup_anteversion | 0.525 | 0.52  |
| cup_inclination | 0.482 | 0.477 |

![Sobol indices](fig_sobol.png)

![OAT sensitivity](fig_oat.png)

## 5. Identifiability per total score

|   total |   n_cases |   n_patterns |   diversity_ratio |
|--------:|----------:|-------------:|------------------:|
|       0 |      5209 |            1 |       0.000191975 |
|       1 |      4055 |            4 |       0.000986436 |
|       2 |       736 |            4 |       0.00543478  |

![Identifiability](fig_identifiability.png)
