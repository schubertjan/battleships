import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb

from simulate_games import COLS_ROWS, DEFAULT_FLEET_SUNK

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Play a game")
    ap.add_argument("--model", default="battleship_model.json")
    ap.add_argument("--game", default="game.csv")
    ap.add_argument("--fleet_sunk", type=json.loads, default=DEFAULT_FLEET_SUNK)
    args = ap.parse_args()

    clf = xgb.XGBClassifier()
    clf.load_model(Path(__file__).parent / args.model)
    label_encoder = joblib.load(Path(__file__).parent / "label.encoder")

    df = pd.read_csv(args.game, index_col=["r"])
    state = pd.DataFrame([df.to_numpy().flatten().tolist()], columns=COLS_ROWS)
    fleet_sunk = pd.DataFrame([args.fleet_sunk], dtype="category")
    X = pd.concat([state, fleet_sunk], axis=1).astype("category")

    print(label_encoder.inverse_transform(clf.predict(X)))
