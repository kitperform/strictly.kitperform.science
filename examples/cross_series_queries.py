"""Cross-series commentary queries over the packaged dataset with pandas.

    python -m strictly_parser.package      # builds data/package/*.csv first
    python examples/cross_series_queries.py [data/package]

Every answer is a filter, a group-by or a join over the flat files; the heavy lifting (which judge sat where,
which round a week belongs to, what a bye means) is already in the columns.
"""
import sys
import pandas as pd

d = (sys.argv[1] if len(sys.argv) > 1 else "data/package").rstrip("/") + "/"
jm = pd.read_csv(d + "judge_marks.csv")
pf = pd.read_csv(d + "performances.csv")
cw = pd.read_csv(d + "couple_weeks.csv")
cp = pd.read_csv(d + "couples.csv")
sp = pd.read_csv(d + "series_people.csv")
ps = pd.read_csv(d + "panel_seats.csv")
ep = pd.read_csv(d + "episodes.csv")
pm = pd.read_csv(d + "performance_music.csv")
songs = pd.read_csv(d + "songs.csv")
pd.set_option("display.width", 160)

print("Craig's first ever 10")
tens = jm[(jm.judge_slug == "craig-revel-horwood") & (jm["mark"] == 10)].sort_values(["series_number", "d_perf_seq"])
print(tens.iloc[0][["series_key", "week_number", "chart_label", "dance_key"]].to_dict(), "\n")

print("Judge generosity by series (mean mark), regular judges only")
reg = jm[jm.panel_role.isin(["regular", "head"])]
print(reg.pivot_table(index="judge_slug", columns="series_number", values="mark", aggfunc="mean").round(1).dropna(thresh=5).to_string(), "\n")

print("Perfect scores per series (judges' total equal to the scale maximum)")
perfect = pf[(pf.d_total == pf.d_scale_max) & pf.d_total.notna()]
print(perfect.groupby("series_key").size().to_string(), "\n")

print("Winners who had been in the bottom two along the way")
winners = cp.loc[cp.final_placement == 1, "couple_key"]
print(cw[cw.couple_key.isin(winners) & cw.result_status.isin(["bottom_two", "bottom_three"])][["couple_week_key", "result_status"]].to_string(index=False), "\n")

print("Byes, and the one that turned into a withdrawal")
byes = cw[cw.bye_granted == True][["couple_week_key", "absence_reason", "result_status"]]
print(byes.to_string(index=False), "\n")

print("Shows missed by each regular judge")
print(ps[ps.panel_role == "absent"].groupby("judge_slug").size().sort_values(ascending=False).to_string(), "\n")

print("Professionals by number of finals reached")
finals = cp[cp.d_reached_final == True]
print(finals.d_pro_slugs.str.split("|").explode().value_counts().head(10).to_string(), "\n")

print("Most-danced songs across all series (by Song, artist-independent)")
top = pm.merge(songs, on="song_key").groupby(["song_key", "title"]).size().sort_values(ascending=False).head(10)
print(top.to_string(), "\n")

print("Series with a Blackpool week")
print(ep[ep.venue_key == "blackpool-tower-ballroom"].groupby("series_key").size().to_string(), "\n")

print("Lowest judges' total ever for a dance that scored, and the week it happened")
scored = pf[pf.scoring_mode == "judge_marks"]
low = scored.loc[scored.d_total.idxmin()]
print(low[["performance_key", "d_total", "d_scale_max", "music_raw"]].to_dict(), "\n")

print("Stand-in and replacement professionals who scored 30 or more")
print(pf[pf.d_partnership_kind.isin(["substitute_temporary", "replacement_permanent"]) & (pf.d_total >= 30)][["performance_key", "performing_pro_slug", "d_total"]].to_string(index=False))
