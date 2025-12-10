#!/usr/bin/env python3
import sys
import os
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, accuracy_score
from sklearn.model_selection import train_test_split

def parse_cell_line(sample):
    m = re.match(r"(.*)_HIC(\d+)$", sample)
    if m:
        cell_line = m.group(1)
        n = int(m.group(2))
        return cell_line, n
    else:
        raise ValueError(f"Could not parse cell line from: {sample}")

def linear_classifier(df: pd.DataFrame):
    df["y"] = df["Replicates"].astype(int)
    X = df[["score"]]
    y = df["y"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=12)

    # Train LogisticRegression model (curve fit)
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Get ROC curve from model
    fpr, tpr, thresholds = roc_curve(y_test, model.predict_proba(X_test)[:,1])

    # Use Youden’s J statistic = tpr - fpr to get best threshold from ROC
    best_idx = np.argmax(tpr - fpr)
    best_threshold = thresholds[best_idx]

    print(f"Best threshold from ROC: {best_threshold:.4f}")

    # Apply best threshold
    y_pred_best = (model.predict_proba(X_test)[:,1] >= best_threshold).astype(int)
    acc_best = accuracy_score(y_test, y_pred_best)
    print(f"Accuracy with best threshold: {acc_best:.3f}")

    # Threshold directly from raw scores
    scores = X_test["score"].values
    fpr_raw, tpr_raw, score_thresholds = roc_curve(y_test, scores)

    idx_raw = np.argmax(tpr_raw - fpr_raw)
    best_score_threshold = score_thresholds[idx_raw]

    print(f"Best concordance score threshold: {best_score_threshold:.4f}")

def get_threshold(df: pd.DataFrame):
    df["y"] = df["Replicates"].astype(int)
    threshold = df.loc[df["y"] == 0, "score"].max()
    print(f"Threshold (highest score for non-replicate pair): {threshold:.4f}")

    df["pred"] = (df["score"] > threshold).astype(int)
    accuracy = accuracy_score(df["y"], df["pred"])
    print(f"Accuracy using threshold: {accuracy:.3f}")

    return threshold

score_file = sys.argv[1]
# output_dir = sys.argv[2]

df = pd.read_csv(score_file, delimiter='\t', comment='#')
df.columns = ["Sample1", "Sample2", "score"]

df[["CellLine1", "SampleNum1"]] = df["Sample1"].apply(lambda x: pd.Series(parse_cell_line(x)))
df[["CellLine2", "SampleNum2"]] = df["Sample2"].apply(lambda x: pd.Series(parse_cell_line(x)))

df["Replicates"] = (df["CellLine1"] == df["CellLine2"])

# Summarize scores
summary = df.groupby("Replicates")["score"].mean().rename({True: "Replicates", False: "Non-Replicates"})
print("Average concordance scores:")
print(summary)

threshold = get_threshold(df)

plt.figure(figsize=(6, 6))
df_reps = df[df["Replicates"] == True].copy()
df_nonreps = df[df["Replicates"] == False].copy()
df_reps["idx"] = range(len(df_reps))
df_nonreps["idx"] = range(len(df_reps), len(df))
plt.scatter(df_reps["idx"], df_reps["score"], c="tab:green", alpha=0.8, label="Replicates")
plt.scatter(df_nonreps["idx"], df_nonreps["score"], c="tab:red", alpha=0.8, label="Non-Replicates")
plt.axhline(y=threshold, color="black", linestyle="--", linewidth=1.5, alpha=0.7, label=f"Threshold = {threshold:.3f}")

plt.xticks([])
# plt.xlabel("Index")
plt.ylabel("Condordance Score", fontsize=12)
# plt.title(r"Gaussian ($\sigma$=2)")
# plt.title("Scores by (Non-)Replicates")
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(score_file), "scores.svg"), format="svg")
plt.close()

# linear_classifier(df)

# Heatmap of average scores between cell lines
df["pair"] = df.apply(lambda x: tuple(sorted([x["CellLine1"], x["CellLine2"]])), axis=1)
avg_scores = df.groupby("pair")["score"].mean()

cellLines = sorted(set(df['CellLine1']))
matrix = pd.DataFrame(np.nan, index=cellLines, columns=cellLines)

for (l1, l2), val in avg_scores.items():
    matrix.loc[l1, l2] = val
    matrix.loc[l2, l1] = val  # symmetric
mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)

plt.figure(figsize=(6, 6))
sns.heatmap(matrix, annot=True, cmap="viridis", fmt=".2f", mask=mask)
# plt.title("Average Concordance Scores by Cell Line Pairs")
plt.savefig(os.path.join(os.path.dirname(score_file), "cell_line_heatmap.svg"), format="svg")
plt.close()
