# SHIVA SPIN-THA v7.4 — RuleAudit Report

**N synthetic cases:** 10,000
**Drivers analysed:** 13

## Headline diagnostics

- **Firing**: DEAD: 'low_sit_av_hyper' fires in 0 of 10000 cases
- **Correlation**: EXTREME-COLLINEAR: 'delta_ss_stiff' ↔ 'mob_stiff' (|r|=1.000)
- **Correlation**: EXTREME-COLLINEAR: 'delta_ss_hyper' ↔ 'mob_hyper' (|r|=1.000)
- **Correlation**: COLLINEAR: 'delta_ss_hyper' ↔ 'deep_flex' (|r|=0.931)
- **Correlation**: COLLINEAR: 'mob_hyper' ↔ 'deep_flex' (|r|=0.931)
- **Correlation**: COLLINEAR: 'delta_ss_hyper' ↔ 'sit_to_stand' (|r|=0.658)
- **Correlation**: COLLINEAR: 'mob_hyper' ↔ 'sit_to_stand' (|r|=0.658)
- **Correlation**: COLLINEAR: 'deep_flex' ↔ 'sit_to_stand' (|r|=0.613)
- **Correlation**: COLLINEAR: 'delta_ss_stiff' ↔ 'deep_flex' (|r|=0.531)
- **Correlation**: COLLINEAR: 'mob_stiff' ↔ 'deep_flex' (|r|=0.531)
- **VIF**: EXTREME-VIF: 'delta_ss_hyper' has VIF=inf
- **VIF**: EXTREME-VIF: 'mob_hyper' has VIF=inf
- **VIF**: EXTREME-VIF: 'mob_stiff' has VIF=inf
- **VIF**: EXTREME-VIF: 'delta_ss_stiff' has VIF=8.88e+03
- **VIF**: HIGH-VIF: 'deep_flex' has VIF=7.95
- **Sensitivity**: INTERACTION-DOMINATED: 'pi' (S1=-0.002, ST=0.092, interaction share 102.4%)
- **Sensitivity**: INTERACTION-DOMINATED: 'll' (S1=-0.020, ST=0.094, interaction share 121.5%)
- **Sensitivity**: INTERACTION-DOMINATED: 'ss_standing' (S1=0.028, ST=0.562, interaction share 95.1%)
- **Sensitivity**: INTERACTION-DOMINATED: 'ss_sitting' (S1=0.158, ST=0.677, interaction share 76.7%)
- **Sensitivity**: INERT: 'pt_standing' has ST=0.0000 — input does not move score
- **Sensitivity**: INTERACTION-DOMINATED: 'cup_anteversion' (S1=0.020, ST=0.139, interaction share 85.8%)
- **Sensitivity**: INERT: 'cup_inclination' has ST=0.0000 — input does not move score
- **Sensitivity**: INTERACTION-DOMINATED: 'femoral_version' (S1=0.018, ST=0.111, interaction share 83.7%)
- **Identifiability**: COLLAPSE: total=18.0 has 122.0 cases collapsing to 2.0 patterns (div=0.016)
- **Identifiability**: COLLAPSE: total=21.0 has 193.0 cases collapsing to 1.0 patterns (div=0.005)
- **Identifiability**: COLLAPSE: total=27.0 has 176.0 cases collapsing to 1.0 patterns (div=0.006)
- **Identifiability**: COLLAPSE: total=29.0 has 166.0 cases collapsing to 1.0 patterns (div=0.006)
- **Identifiability**: COLLAPSE: total=32.0 has 179.0 cases collapsing to 1.0 patterns (div=0.006)
- **Identifiability**: COLLAPSE: total=33.0 has 379.0 cases collapsing to 2.0 patterns (div=0.005)
- **Identifiability**: COLLAPSE: total=35.0 has 306.0 cases collapsing to 1.0 patterns (div=0.003)
- **Identifiability**: COLLAPSE: total=41.0 has 330.0 cases collapsing to 1.0 patterns (div=0.003)
- **Identifiability**: COLLAPSE: total=45.0 has 179.0 cases collapsing to 3.0 patterns (div=0.017)
- **Identifiability**: COLLAPSE: total=47.0 has 591.0 cases collapsing to 1.0 patterns (div=0.002)
- **Identifiability**: COLLAPSE: total=50.0 has 174.0 cases collapsing to 3.0 patterns (div=0.017)
- **Identifiability**: COLLAPSE: total=51.0 has 311.0 cases collapsing to 4.0 patterns (div=0.013)
- **Identifiability**: COLLAPSE: total=57.0 has 304.0 cases collapsing to 3.0 patterns (div=0.010)
- **Identifiability**: COLLAPSE: total=59.0 has 225.0 cases collapsing to 2.0 patterns (div=0.009)
- **Identifiability**: COLLAPSE: total=61.0 has 131.0 cases collapsing to 2.0 patterns (div=0.015)
- **Identifiability**: COLLAPSE: total=62.0 has 262.0 cases collapsing to 3.0 patterns (div=0.011)
- **Identifiability**: COLLAPSE: total=63.0 has 508.0 cases collapsing to 4.0 patterns (div=0.008)
- **Identifiability**: COLLAPSE: total=65.0 has 419.0 cases collapsing to 3.0 patterns (div=0.007)
- **Identifiability**: COLLAPSE: total=66.0 has 111.0 cases collapsing to 2.0 patterns (div=0.018)
- **Identifiability**: COLLAPSE: total=67.0 has 223.0 cases collapsing to 2.0 patterns (div=0.009)
- **Identifiability**: COLLAPSE: total=69.0 has 146.0 cases collapsing to 2.0 patterns (div=0.014)
- **Identifiability**: COLLAPSE: total=71.0 has 446.0 cases collapsing to 3.0 patterns (div=0.007)
- **Identifiability**: COLLAPSE: total=73.0 has 104.0 cases collapsing to 1.0 patterns (div=0.010)
- **Identifiability**: COLLAPSE: total=75.0 has 219.0 cases collapsing to 2.0 patterns (div=0.009)
- **Identifiability**: COLLAPSE: total=77.0 has 811.0 cases collapsing to 3.0 patterns (div=0.004)
- **Identifiability**: COLLAPSE: total=78.0 has 100.0 cases collapsing to 1.0 patterns (div=0.010)
- **Identifiability**: COLLAPSE: total=79.0 has 168.0 cases collapsing to 1.0 patterns (div=0.006)
- **Identifiability**: COLLAPSE: total=81.0 has 375.0 cases collapsing to 2.0 patterns (div=0.005)
- **Identifiability**: COLLAPSE: total=87.0 has 189.0 cases collapsing to 1.0 patterns (div=0.005)
- **Identifiability**: COLLAPSE: total=93.0 has 290.0 cases collapsing to 1.0 patterns (div=0.003)

## 1. Driver firing rates

|                   |   fire_rate |   mean_contrib |
|:------------------|------------:|---------------:|
| pi_ll_mismatch    |       0.757 |          11.36 |
| uncert_fv         |       0.644 |           7.73 |
| uncert_overall    |       0.639 |           3.83 |
| comb_vers_oob     |       0.626 |           8.77 |
| delta_ss_stiff    |       0.459 |           9.19 |
| mob_stiff         |       0.459 |           4.59 |
| deep_flex         |       0.249 |           1    |
| mob_hyper         |       0.224 |           1.79 |
| delta_ss_hyper    |       0.224 |           4.02 |
| low_sit_av_stiff  |       0.151 |           2.41 |
| sit_to_stand      |       0.111 |           0.44 |
| high_sit_av_stiff |       0.035 |           0.21 |
| low_sit_av_hyper  |       0     |           0    |

## 2. Driver orthogonality

Maximum off-diagonal |r| = 1.000

![Correlation heatmap](fig_correlation.png)

## 3. Variance Inflation Factor

|                   |      VIF |
|:------------------|---------:|
| delta_ss_hyper    |  inf     |
| mob_hyper         |  inf     |
| mob_stiff         |  inf     |
| delta_ss_stiff    | 8883.5   |
| deep_flex         |    7.953 |
| sit_to_stand      |    1.763 |
| low_sit_av_stiff  |    1.319 |
| high_sit_av_stiff |    1.09  |
| uncert_fv         |    1.001 |
| uncert_overall    |    1.001 |
| pi_ll_mismatch    |    1.001 |
| comb_vers_oob     |    1.001 |

![VIF](fig_vif.png)

## 4. Sensitivity analysis

|                 |     S1 |    ST |
|:----------------|-------:|------:|
| ss_sitting      |  0.158 | 0.677 |
| ss_standing     |  0.028 | 0.562 |
| cup_anteversion |  0.02  | 0.139 |
| femoral_version |  0.018 | 0.111 |
| ll              | -0.02  | 0.094 |
| pi              | -0.002 | 0.092 |
| conf_fv         |  0.095 | 0.082 |
| conf_overall    |  0.015 | 0.021 |
| pt_standing     |  0     | 0     |
| cup_inclination |  0     | 0     |

![Sobol indices](fig_sobol.png)

![OAT sensitivity](fig_oat.png)

## 5. Identifiability per total score

|   total |   n_cases |   n_patterns |   diversity_ratio |
|--------:|----------:|-------------:|------------------:|
|       0 |        41 |            1 |        0.0243902  |
|       6 |        48 |            1 |        0.0208333  |
|      12 |        64 |            1 |        0.015625   |
|      14 |        60 |            1 |        0.0166667  |
|      15 |        96 |            1 |        0.0104167  |
|      16 |         5 |            1 |        0.2        |
|      18 |       122 |            2 |        0.0163934  |
|      19 |        13 |            1 |        0.0769231  |
|      20 |        87 |            1 |        0.0114943  |
|      21 |       193 |            1 |        0.00518135 |
|      22 |         8 |            1 |        0.125      |
|      24 |         7 |            1 |        0.142857   |
|      25 |        15 |            1 |        0.0666667  |
|      26 |        97 |            1 |        0.0103093  |
|      27 |       176 |            1 |        0.00568182 |
|      29 |       166 |            1 |        0.0060241  |
|      30 |        50 |            3 |        0.06       |
|      31 |        15 |            1 |        0.0666667  |
|      32 |       179 |            1 |        0.00558659 |
|      33 |       379 |            2 |        0.00527704 |
|      34 |        15 |            1 |        0.0666667  |
|      35 |       306 |            1 |        0.00326797 |
|      36 |       108 |            4 |        0.037037   |
|      37 |        34 |            1 |        0.0294118  |
|      39 |        28 |            1 |        0.0357143  |
|      40 |        30 |            1 |        0.0333333  |
|      41 |       330 |            1 |        0.0030303  |
|      42 |        87 |            3 |        0.0344828  |
|      44 |        78 |            2 |        0.025641   |
|      45 |       179 |            3 |        0.0167598  |
|      46 |        46 |            2 |        0.0434783  |
|      47 |       591 |            1 |        0.00169205 |
|      48 |       181 |            4 |        0.0220994  |
|      49 |        44 |            1 |        0.0227273  |
|      50 |       174 |            3 |        0.0172414  |
|      51 |       311 |            4 |        0.0128617  |
|      52 |        68 |            2 |        0.0294118  |
|      54 |        49 |            2 |        0.0408163  |
|      55 |        73 |            1 |        0.0136986  |
|      56 |       138 |            3 |        0.0217391  |
|      57 |       304 |            3 |        0.00986842 |
|      58 |        25 |            1 |        0.04       |
|      59 |       225 |            2 |        0.00888889 |
|      60 |        68 |            2 |        0.0294118  |
|      61 |       131 |            2 |        0.0152672  |
|      62 |       262 |            3 |        0.0114504  |
|      63 |       508 |            4 |        0.00787402 |
|      64 |        40 |            1 |        0.025      |
|      65 |       419 |            3 |        0.0071599  |
|      66 |       111 |            2 |        0.018018   |
|      67 |       223 |            2 |        0.00896861 |
|      68 |        21 |            1 |        0.047619   |
|      69 |       146 |            2 |        0.0136986  |
|      71 |       446 |            3 |        0.00672646 |
|      72 |        57 |            1 |        0.0175439  |
|      73 |       104 |            1 |        0.00961538 |
|      75 |       219 |            2 |        0.00913242 |
|      77 |       811 |            3 |        0.00369914 |
|      78 |       100 |            1 |        0.01       |
|      79 |       168 |            1 |        0.00595238 |
|      81 |       375 |            2 |        0.00533333 |
|      83 |        63 |            1 |        0.015873   |
|      87 |       189 |            1 |        0.00529101 |
|      93 |       290 |            1 |        0.00344828 |

![Identifiability](fig_identifiability.png)
