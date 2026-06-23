# FootballerFun
Some silly stats for the world cup. I wanted to answer if/when Messi scored 13 goals in a succession of five matches, matching the World Cup record set by Just Fontaine.

## Lionel Messi’s Five-Match Goal Record

Using the new `PlayerMatchesProfile.py` analyzer against `leomessi_matches.csv`, we found Messi’s all-time five-match scoring peak: **15 goals across the span from 19 February 2012 through 11 March 2012** (matches 376–380). That streak represents the highest cumulative goal output he has ever produced over any five consecutive recorded matches, and he has not matched or surpassed it again in the dataset.

Running `python3 PlayerMatchesProfile.py --n-goals 13 --span 5` (equivalent to the threshold flags) shows that **every ≥13-goal five-match window also lives inside that same February–March 2012 heater**, largely because of the 7 March 2012 demolition of Bayer Leverkusen. Here are the unique matches that power those overlapping windows:

| Date       | Fixture                                 | Goals |
|------------|-----------------------------------------|-------|
| 2012-02-14 | Bayer Leverkusen vs Barcelona           | 1     |
| 2012-02-19 | Barcelona vs Valencia                   | 4     |
| 2012-02-26 | Atletico Madrid vs Barcelona            | 1     |
| 2012-02-29 | Switzerland vs Argentina                | 3     |
| 2012-03-07 | Barcelona vs Bayer Leverkusen           | 5     |
| 2012-03-11 | Racing Santander vs Barcelona           | 2     |
| 2012-03-17 | Sevilla vs Barcelona                    | 1     |
| 2012-03-20 | Barcelona vs Granada                    | 3     |

Even so, the `n_goal_in_m_matches` analysis shows that he continues to post remarkable goal-scoring streaks—hitting ≥13 goals in five-match windows multiple times—even now at age 38/39. It is unlikely he breaks that historic 15-goal mark, but it is astonishing that nearly two decades into his career he can still approach it.

This is purely AI prompted because at the end fo the day it's just a sliding window. Maybe I can extend this later. But this was for fun.
