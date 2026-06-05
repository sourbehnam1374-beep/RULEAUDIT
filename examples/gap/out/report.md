# GAP score (Yilgor 2017) — RuleAudit Report

**N synthetic cases:** 10,000
**Drivers analysed:** 5

## Headline diagnostics

- **Sensitivity**: INTERACTION-DOMINATED: 'pi' (S1=0.038, ST=0.311, interaction share 87.7%)
- **Sensitivity**: INTERACTION-DOMINATED: 'll_l1s1' (S1=0.239, ST=0.553, interaction share 56.9%)
- **Sensitivity**: INTERACTION-DOMINATED: 'll_l4s1' (S1=0.029, ST=0.160, interaction share 82.1%)
- **Identifiability**: COLLAPSE: total=0.0 has 316.0 cases collapsing to 1.0 patterns (div=0.003)
- **Identifiability**: COLLAPSE: total=1.0 has 802.0 cases collapsing to 4.0 patterns (div=0.005)
- **Identifiability**: COLLAPSE: total=2.0 has 1059.0 cases collapsing to 9.0 patterns (div=0.008)
- **Identifiability**: COLLAPSE: total=3.0 has 1610.0 cases collapsing to 18.0 patterns (div=0.011)
- **Identifiability**: COLLAPSE: total=4.0 has 1817.0 cases collapsing to 28.0 patterns (div=0.015)
- **Identifiability**: MECH-SPRAWL: total=6.0 encodes 40.0 distinct mechanism patterns across 1287.0 cases
- **Identifiability**: MECH-SPRAWL: total=7.0 encodes 37.0 distinct mechanism patterns across 861.0 cases
- **Identifiability**: MECH-SPRAWL: total=8.0 encodes 31.0 distinct mechanism patterns across 409.0 cases
- **Identifiability**: MECH-SPRAWL: total=9.0 encodes 20.0 distinct mechanism patterns across 214.0 cases

## 1. Driver firing rates

|     |   fire_rate |   mean_contrib |
|:----|------------:|---------------:|
| rpv |       0.628 |           1.42 |
| age |       0.498 |           0.5  |
| rll |       0.443 |           1.12 |
| rsa |       0.439 |           0.46 |
| ldi |       0.394 |           0.78 |

## 2. Driver orthogonality

Maximum off-diagonal |r| = 0.000

![Correlation heatmap](fig_correlation.png)

## 3. Variance Inflation Factor

|     |   VIF |
|:----|------:|
| age | 1.001 |
| rsa | 1.001 |
| rll | 1.001 |
| rpv | 1     |
| ldi | 1     |

![VIF](fig_vif.png)

## 4. Sensitivity analysis

|         |    S1 |    ST |
|:--------|------:|------:|
| ll_l1s1 | 0.239 | 0.553 |
| pi      | 0.038 | 0.311 |
| gt      | 0.147 | 0.201 |
| ss      | 0.097 | 0.185 |
| ll_l4s1 | 0.029 | 0.16  |
| age     | 0.031 | 0.035 |

![Sobol indices](fig_sobol.png)

![OAT sensitivity](fig_oat.png)

## 5. Identifiability per total score

|   total |   n_cases |   n_patterns |   diversity_ratio |
|--------:|----------:|-------------:|------------------:|
|       0 |       316 |            1 |        0.00316456 |
|       1 |       802 |            4 |        0.00498753 |
|       2 |      1059 |            9 |        0.00849858 |
|       3 |      1610 |           18 |        0.0111801  |
|       4 |      1817 |           28 |        0.01541    |
|       5 |      1502 |           36 |        0.023968   |
|       6 |      1287 |           40 |        0.03108    |
|       7 |       861 |           37 |        0.0429733  |
|       8 |       409 |           31 |        0.0757946  |
|       9 |       214 |           20 |        0.0934579  |
|      10 |        88 |           10 |        0.113636   |
|      11 |        26 |            4 |        0.153846   |
|      12 |         8 |            4 |        0.5        |

![Identifiability](fig_identifiability.png)
