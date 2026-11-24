import argparse
import sqlite3
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Train a model")
    ap.add_argument("--db", default="battleship.db")
    ap.add_argument("--model", default="battleship_model.json")
    args = ap.parse_args()
    with sqlite3.connect(args.db) as con:
        df = pd.read_sql_query("SELECT * FROM moves", con)
    df = df.drop(columns=["id"])
    df = df.astype("category")

    label_encoder = LabelEncoder()
    X = df.loc[:, df.columns != "rc"]
    y = label_encoder.fit_transform(df["rc"])
    X_train, X_val, y_train, y_val = train_test_split(X, y, train_size=0.9, stratify=y)
    del X, y, df

    print("Training...")
    clf = xgb.XGBClassifier(
        tree_method="hist",
        enable_categorical=True,
        eval_metric="mlogloss",
        n_estimators=1000,
        learning_rate=0.1,
        early_stopping_rounds=10,
        n_jobs=-1,
    )
    eval_list = [(X_val, y_val)]
    clf.fit(
        X_train,
        y_train,
        eval_set=eval_list,
    )

    print("Saving the model...")
    clf.save_model(Path(__file__).parent / args.model)
    joblib.dump(label_encoder, Path(__file__).parent / "label.encoder")
