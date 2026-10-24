"""
Customer Shopping Behavior - End-to-End Data Analysis
-----------------------------------------------------
Run:  python analysis.py
Needs: pandas, matplotlib, seaborn, scipy
Steps: 1) Load  2) Clean  3) Explore  4) Segment  5) Test hypotheses  6) Save charts + tables
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CHARTS = os.path.join(HERE, "charts")
OUT_TABLES = os.path.join(HERE, "tables")
os.makedirs(OUT_CHARTS, exist_ok=True)
os.makedirs(OUT_TABLES, exist_ok=True)
sns.set_theme(style="whitegrid")
AMT = "Purchase Amount (USD)"

# ------------------------------------------------------------------ 1. LOAD
df = pd.read_csv(os.path.join(HERE, "data", "customer_shopping_behavior.csv"))
print("Shape:", df.shape)

# ----------------------------------------------------------------- 2. CLEAN
print("\nMissing values:\n", df.isna().sum()[df.isna().sum() > 0])
print("Duplicate rows:", df.duplicated().sum(), "| duplicate IDs:", df["Customer ID"].duplicated().sum())

# Fill the 37 missing ratings with the median rating of the same category
df["Review Rating"] = df["Review Rating"].fillna(
    df.groupby("Category")["Review Rating"].transform("median")
)

# "Promo Code Used" is identical to "Discount Applied" -> drop the duplicate column
assert (df["Discount Applied"] == df["Promo Code Used"]).all()
df = df.drop(columns=["Promo Code Used"])

# Feature engineering
df["Age Group"] = pd.cut(df["Age"], [17, 25, 35, 45, 55, 65, 80],
                         labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66+"])
df["Loyalty Tier"] = pd.cut(df["Previous Purchases"], [0, 10, 25, 40, 50],
                            labels=["New (1-10)", "Regular (11-25)", "Loyal (26-40)", "VIP (41-50)"])
df["Spend Band"] = pd.cut(df[AMT], [0, 40, 60, 80, 100],
                          labels=["Low ($20-40)", "Mid ($41-60)", "High ($61-80)", "Premium ($81-100)"])
df.to_csv(os.path.join(HERE, "data", "customer_shopping_behavior_cleaned.csv"), index=False)

# --------------------------------------------------------------- 3. EXPLORE
def summary(col):
    t = df.groupby(col, observed=True)[AMT].agg(customers="count", revenue="sum", avg_spend="mean").round(2)
    t["revenue_share_%"] = (t["revenue"] / t["revenue"].sum() * 100).round(1)
    return t.sort_values("revenue", ascending=False)

for col in ["Category", "Item Purchased", "Season", "Gender", "Age Group", "Location",
            "Subscription Status", "Discount Applied", "Shipping Type", "Payment Method",
            "Frequency of Purchases", "Loyalty Tier"]:
    summary(col).to_csv(os.path.join(OUT_TABLES, f"by_{col.lower().replace(' ', '_')}.csv"))

print("\nTotal revenue: $", df[AMT].sum(), "| Avg order: $", round(df[AMT].mean(), 2))
print("\nRevenue by category:\n", summary("Category"))
print("\nRevenue by season:\n", summary("Season"))
print("\nTop 10 states:\n", summary("Location").head(10))

# Rating by item
rating_item = df.groupby("Item Purchased")["Review Rating"].mean().round(2).sort_values()
rating_item.to_csv(os.path.join(OUT_TABLES, "avg_rating_by_item.csv"))

# Category x Season revenue
cat_season = pd.crosstab(df["Category"], df["Season"], values=df[AMT], aggfunc="sum")

# --------------------------------------------------------------- 4. CHARTS
def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_CHARTS, name), dpi=140)
    plt.close()

# 1 Revenue by category
s = summary("Category")
ax = s["revenue"].plot(kind="bar", color=sns.color_palette("viridis", len(s)), figsize=(7, 4.5))
ax.set_title("Revenue by Category"); ax.set_ylabel("Revenue (USD)"); ax.set_xlabel("")
for i, v in enumerate(s["revenue"]):
    ax.text(i, v + 1000, f"${v/1000:.0f}K\n({s['revenue_share_%'].iloc[i]}%)", ha="center", fontsize=9)
plt.xticks(rotation=0); ax.set_ylim(0, s["revenue"].max() * 1.2)
save("01_revenue_by_category.png")

# 2 Revenue by season
s = summary("Season").reindex(["Spring", "Summer", "Fall", "Winter"])
ax = s["revenue"].plot(kind="bar", color="#3b82a0", figsize=(7, 4.5))
ax.set_title("Revenue by Season"); ax.set_ylabel("Revenue (USD)"); ax.set_xlabel("")
plt.xticks(rotation=0); ax.set_ylim(50000, s["revenue"].max() * 1.05)
save("02_revenue_by_season.png")

# 3 Category x Season heatmap
plt.figure(figsize=(7, 4.5))
sns.heatmap(cat_season, annot=True, fmt=",.0f", cmap="YlGnBu")
plt.title("Revenue: Category x Season (USD)")
save("03_category_season_heatmap.png")

# 4 Top / bottom 10 states
s = summary("Location")["revenue"]
pd.concat([s.head(10), s.tail(5)]).sort_values().plot(
    kind="barh", figsize=(7, 6), color="#e07b39")
plt.title("Top 10 and Bottom 5 States by Revenue"); plt.xlabel("Revenue (USD)")
save("04_states_top_bottom.png")

# 5 Spend by age group (average)
ax = df.groupby("Age Group", observed=True)[AMT].mean().plot(kind="bar", color="#6a994e", figsize=(7, 4.5))
ax.set_title("Average Spend per Purchase by Age Group"); ax.set_ylabel("USD"); ax.set_xlabel("")
ax.set_ylim(0, 75); plt.xticks(rotation=0)
save("05_avg_spend_by_age.png")

# 6 Discount vs no discount
ax = df.groupby("Discount Applied")[AMT].mean().plot(kind="bar", color=["#8d99ae", "#ef476f"], figsize=(5, 4.5))
ax.set_title("Avg Spend: Discount vs No Discount"); ax.set_ylabel("USD"); ax.set_xlabel("Discount applied")
ax.set_ylim(0, 75); plt.xticks(rotation=0)
save("06_discount_effect.png")

# 7 Subscription: share and spend
fig, axes = plt.subplots(1, 2, figsize=(9, 4))
df["Subscription Status"].value_counts().plot(kind="pie", autopct="%1.0f%%", ax=axes[0], colors=["#bdbdbd", "#4c78a8"])
axes[0].set_title("Subscribers vs Non-subscribers"); axes[0].set_ylabel("")
df.groupby("Subscription Status")[AMT].mean().plot(kind="bar", ax=axes[1], color=["#bdbdbd", "#4c78a8"])
axes[1].set_title("Avg Spend"); axes[1].set_ylim(0, 75); axes[1].set_xlabel(""); plt.sca(axes[1]); plt.xticks(rotation=0)
save("07_subscription.png")

# 8 Gender split
fig, axes = plt.subplots(1, 2, figsize=(9, 4))
df["Gender"].value_counts().plot(kind="pie", autopct="%1.0f%%", ax=axes[0], colors=["#4c78a8", "#f58518"])
axes[0].set_title("Customer Gender Split"); axes[0].set_ylabel("")
df.groupby("Gender")[AMT].mean().plot(kind="bar", ax=axes[1], color=["#f58518", "#4c78a8"])
axes[1].set_title("Avg Spend"); axes[1].set_ylim(0, 75); axes[1].set_xlabel(""); plt.sca(axes[1]); plt.xticks(rotation=0)
save("08_gender.png")

# 9 Ratings by item
plt.figure(figsize=(7, 7))
rating_item.plot(kind="barh", color="#5c7aea")
plt.xlim(3.4, 4.0); plt.title("Average Review Rating by Item"); plt.xlabel("Rating")
save("09_rating_by_item.png")

# 10 Correlation heatmap
plt.figure(figsize=(5.5, 4.5))
sns.heatmap(df[[AMT, "Age", "Review Rating", "Previous Purchases"]].corr(), annot=True, fmt=".2f",
            cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation of Numeric Columns")
save("10_correlation.png")

# 11 Loyalty tiers
s = summary("Loyalty Tier").reindex(["New (1-10)", "Regular (11-25)", "Loyal (26-40)", "VIP (41-50)"])
ax = s["customers"].plot(kind="bar", color="#2a9d8f", figsize=(7, 4.5))
ax.set_title("Customers by Loyalty Tier (Previous Purchases)"); ax.set_ylabel("Customers"); ax.set_xlabel("")
plt.xticks(rotation=0)
save("11_loyalty_tiers.png")

# -------------------------------------------------------- 5. HYPOTHESIS TESTS
def verdict(p):
    return "SIGNIFICANT difference" if p < 0.05 else "no significant difference"

results = []
# a) Discount vs no discount (t-test)
a = df.loc[df["Discount Applied"] == "Yes", AMT]; b = df.loc[df["Discount Applied"] == "No", AMT]
t, p = stats.ttest_ind(a, b, equal_var=False)
results.append(("Spend: discount vs no discount (t-test)", round(p, 4), verdict(p)))
# b) Male vs female spend (t-test)
a = df.loc[df["Gender"] == "Male", AMT]; b = df.loc[df["Gender"] == "Female", AMT]
t, p = stats.ttest_ind(a, b, equal_var=False)
results.append(("Spend: male vs female (t-test)", round(p, 4), verdict(p)))
# c) Subscriber vs non-subscriber spend (t-test)
a = df.loc[df["Subscription Status"] == "Yes", AMT]; b = df.loc[df["Subscription Status"] == "No", AMT]
t, p = stats.ttest_ind(a, b, equal_var=False)
results.append(("Spend: subscriber vs non-subscriber (t-test)", round(p, 4), verdict(p)))
# d) Spend across categories / seasons / states (ANOVA)
for col in ["Category", "Season", "Age Group", "Shipping Type", "Payment Method", "Location"]:
    groups = [g[AMT].values for _, g in df.groupby(col, observed=True)]
    f, p = stats.f_oneway(*groups)
    results.append((f"Spend across {col} (ANOVA)", round(p, 4), verdict(p)))
# e) Rating across items (ANOVA)
groups = [g["Review Rating"].values for _, g in df.groupby("Item Purchased")]
f, p = stats.f_oneway(*groups)
results.append(("Rating across items (ANOVA)", round(p, 4), verdict(p)))
# f) Gender vs category (chi-square)
chi, p, _, _ = stats.chi2_contingency(pd.crosstab(df["Gender"], df["Category"]))
results.append(("Gender vs category mix (chi-square)", round(p, 4), verdict(p)))
# g) Subscription vs purchase frequency (chi-square)
chi, p, _, _ = stats.chi2_contingency(pd.crosstab(df["Subscription Status"], df["Frequency of Purchases"]))
results.append(("Subscription vs purchase frequency (chi-square)", round(p, 4), verdict(p)))

res = pd.DataFrame(results, columns=["Test", "p_value", "Conclusion (alpha=0.05)"])
res.to_csv(os.path.join(OUT_TABLES, "hypothesis_tests.csv"), index=False)
print("\nHypothesis tests:\n", res.to_string(index=False))
print("\nDone. Charts ->", OUT_CHARTS, "| Tables ->", OUT_TABLES)
