"""Sample TV-style commentary queries over the tidy dataset with pandas.

    python examples/commentary_queries.py [data/tidy/S24]

Each query is a filter and a sort over one or two flat files, as the data
model intends (docs/data-model-v2.md section 1, rule 4).
"""
import sys
import pandas as pd

d = (sys.argv[1] if len(sys.argv) > 1 else "data/tidy/S24").rstrip("/") + "/"
jm = pd.read_csv(d + "judge_marks.csv")
pf = pd.read_csv(d + "performances.csv")
cw = pd.read_csv(d + "couple_weeks.csv")
rr = pd.read_csv(d + "results_rounds.csv")

print("Each judge's highest mark so far, and the first time they gave it")
first = (jm.sort_values("d_perf_seq")
           .groupby("judge_slug")
           .apply(lambda g: g[g["mark"] == g["mark"].max()].iloc[0][["mark", "week_number", "chart_label", "dance_key"]], include_groups=False))
print(first.to_string(), "\n")

tens = jm[(jm.judge_slug == "craig-revel-horwood") & (jm["mark"] == 10)].sort_values("d_perf_seq")
print("Craig's first 10 of the series:", "none yet" if tens.empty else tens.iloc[0][["week_number", "chart_label", "dance_key"]].to_dict(), "\n")

print("Judge generosity (mean mark)")
print(jm.groupby("judge_slug")["mark"].mean().round(2).sort_values().to_string(), "\n")

latest = int(pf.loc[pf.stated_total.notna(), "week_number"].max())
print(f"Leaderboard, week {latest}")
print(pf[(pf.week_number == latest) & pf.stated_total.notna()]
      .sort_values("stated_total", ascending=False)[["chart_label", "dance_key", "stated_total"]].to_string(index=False), "\n")

print("Rounds where the casting vote decided the exit")
print(rr.loc[rr.casting_vote_used == True, ["round_key", "casting_vote_slug", "vote_direction"]].to_string(index=False), "\n")

print("Byes granted")
print(cw.loc[cw.bye_granted == True, ["couple_week_key", "absence_reason"]].to_string(index=False), "\n")

print("Times in the bottom group per couple")
print(cw[cw.at_risk == True].groupby("couple_key").size().sort_values(ascending=False).to_string())
