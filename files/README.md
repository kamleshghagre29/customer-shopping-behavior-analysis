# Customer Shopping Behavior Analysis

An end-to-end exploratory data analysis (EDA) of 3,900 retail customer purchases, covering data cleaning, business metrics, customer segmentation and statistical hypothesis testing.

**Tools:** Python (pandas, matplotlib, seaborn, scipy)

---

## 1. Business Questions
1. Which categories, items, seasons and states drive revenue?
2. Who are the customers (age, gender, loyalty, subscription)?
3. Do discounts, subscriptions or shipping options change how much customers spend?
4. Which differences are real, and which are just noise?

## 2. Dataset
| Item | Detail |
|---|---|
| Rows / columns | 3,900 customers / 18 columns |
| Key columns | Age, Gender, Item Purchased, Category, Purchase Amount (USD), Location, Season, Review Rating, Subscription Status, Shipping Type, Discount Applied, Previous Purchases, Payment Method, Frequency of Purchases |
| Grain | One row per customer (Customer ID is unique) |

## 3. Data Cleaning
| Issue | Action |
|---|---|
| 37 missing Review Ratings (~1%) | Filled with the median rating of the same Category (spread across all 4 categories, so no sign of bias) |
| `Promo Code Used` identical to `Discount Applied` in every row | Dropped the duplicate column |
| No duplicate rows or IDs | None needed |
| Created features | Age Group, Loyalty Tier (by previous purchases), Spend Band |

## 4. Key Findings

**Revenue: $233,081 | Average purchase: $59.76**

| Metric | Result |
|---|---|
| Top category | Clothing: $104K (44.7% of revenue), then Accessories $74K (31.8%), Footwear $36K (15.5%), Outerwear $18.5K (7.9%) |
| Top items | Blouse, Shirt, Dress (about $10.3K each); lowest is Jeans ($7.5K) |
| Best season | Fall: $60.0K and highest average spend ($61.56); Summer lowest ($55.8K, $58.41) |
| Top states | Montana ($5.8K), Illinois ($5.6K), California ($5.6K); lowest is Kansas ($3.4K) |
| Customers | 68% male, 32% female; average age 44; 27% subscribers |
| Discounts | 43% of purchases used a discount; those purchases average $59.28 vs $60.13 without |
| Best rated | Gloves (3.86), Sandals (3.84), Boots (3.82); lowest Shirt (3.62), Jeans (3.65) |

## 5. Statistical Tests (alpha = 0.05)
| Test | p-value | Result |
|---|---|---|
| Spend: discount vs no discount | 0.266 | No significant difference |
| Spend: male vs female | 0.378 | No significant difference |
| Spend: subscriber vs non-subscriber | 0.660 | No significant difference |
| Spend across categories | 0.225 | No significant difference |
| **Spend across seasons** | **0.011** | **Significant** |
| Spend across age groups | 0.703 | No significant difference |
| Spend across shipping types | 0.345 | No significant difference |
| Spend across payment methods | 0.747 | No significant difference |
| Spend across states | 0.097 | No significant difference |
| Rating across items | 0.663 | No significant difference |
| Gender vs category mix (chi-square) | 0.897 | No significant difference |
| Subscription vs purchase frequency (chi-square) | 0.691 | No significant difference |

**How to read this:** Only season shows a statistically significant difference (Fall about $3 higher than Summer per purchase). Because 12 tests were run, one result below 0.05 can appear by chance, and the effect is small, so treat it as a lead to confirm with more data and not as a proven pattern. Numeric columns are also almost uncorrelated with purchase amount (age -0.01, rating 0.03, previous purchases 0.01).

## 6. Business Recommendations
1. **Discounts are not paying for themselves.** 43% of purchases are discounted with no lift in spend. Test cutting discount depth or targeting it at specific segments (A/B test).
2. **Subscriptions add no visible value yet.** Subscribers do not spend more or buy more often. Review the perks so they drive behaviour (for example, exclusive items or faster shipping).
3. **Lean into Clothing and Accessories** (about 77% of revenue), and plan Fall inventory and promotions around the seasonal peak.
4. **Grow the female customer base** (32%). They spend the same as men, so acquisition is the gap and not spend.
5. **Investigate low states** (Kansas, Florida, New Jersey) for local marketing or logistics issues.
6. **Fix quality perception for Shirts and Jeans**, the lowest rated items.

## 7. Limitations
- No purchase dates or order IDs, so no time trends or repeat-purchase analysis.
- Group differences are small compared with the spread in spending (standard deviation about $23.70), which suggests the data may be synthetic or lightly varied.
- Review ratings are one rating per customer, not per product over time.

## 8. Project Structure
```
shopping_behavior_project/
├── README.md
├── analysis.py              # full reproducible pipeline
├── data/                    # raw + cleaned CSV
├── charts/                  # 11 PNG charts
└── tables/                  # summary tables + hypothesis test results (CSV)
```
Run with: `pip install pandas matplotlib seaborn scipy` then `python analysis.py`

## 9. Interview Talking Points
- **Cleaning decision:** "I imputed 37 missing ratings with the category median because missingness was spread evenly and correlations with rating were near zero, so a model would add nothing."
- **Found redundancy:** "I verified two columns were 100% identical with an assertion before dropping one."
- **Statistics:** "I did not just compare averages. I used t-tests, ANOVA and chi-square, and I noted that with 12 tests one significant p-value can happen by chance."
- **Honest conclusion:** "Most expected drivers, such as discounts, subscription and gender, showed no real effect, and I made recommendations around that."
