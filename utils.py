import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mini_league.conf import TARGET_SCORE, init_hcp
import ipywidgets as widgets

def get_scores_df():
  scores = open("./mini_league/scores.txt", "r").read()
  scores_list = [scores.split("\n")][0]
  scores_list = [[j.strip() for j in i.split(",")] for i in scores_list]
  scores_df = pd.DataFrame(scores_list, columns = ["Date", "Name", "Score", "Competition", "Final"])
  scores_df["Score"] = scores_df["Score"].apply(lambda x: int(x))
  scores_df = scores_df.reset_index()
  return scores_df

def get_hcp_dict(scores_df):
  hcp_dict = {"EC":{}, "D":{}, "A":{}}
  gone_thru_dates = []
  for date in scores_df["Date"].unique():
    gone_thru_dates.append(date)
    for name in ["EC", "D"]:
      person_df = scores_df[scores_df["Name"] == name]
      person_df_by_date = person_df.query("Date in {0}".format(gone_thru_dates))
      hcp = int(round((TARGET_SCORE - person_df_by_date["Score"].mean()) * 0.8, 0))
      if hcp <= 0: hcp = 0

      if date == scores_df["Date"].unique()[0]:
        hcp_dict[name][date] = {'current_week_hcp' : init_hcp[name],
                                'next_week_hcp' : hcp,}
      else:
        hcp_dict[name][date] = {'current_week_hcp' : hcp_dict[name][last_date]['next_week_hcp'],
                                'next_week_hcp' : hcp,}

      hcp_dict["A"][date] = {'current_week_hcp' : 0,
                              'next_week_hcp' : 0,}
    last_date = date
  return hcp_dict

def plot_history(player_ec,
                 player_d,
                 player_a,
                 average,
                 only_competitions,
                 with_hcp):

  scores_df = get_scores_df()
  hcp_dict = get_hcp_dict(scores_df)

  if only_competitions == "YES":
    tmp_df = scores_df[scores_df["Competition"] == "True"]
  elif only_competitions == "NO":
    tmp_df = scores_df[scores_df["Competition"] == "False"]
  elif only_competitions == "ALL":
    tmp_df = scores_df

  for index, player in enumerate([player_ec, player_d, player_a]):
    if index == 0:
      name = "EC"
      color = "green"
    elif index == 1:
      name = "D"
      color = "blue"
    elif index == 2:
      name = "A"
      color = "red"
    if player == True:
      tmp_df_name = tmp_df[tmp_df["Name"] == name]
      tmp_df_name = tmp_df_name.sort_values(by = ["Date", "index"])
      if with_hcp == "YES":
        tmp_df_name["Score"] = tmp_df_name.apply(lambda x: x.Score + hcp_dict[x.Name][x.Date]['current_week_hcp'], axis=1)

      score_val = tmp_df_name["Score"].values
      if average == 0:
        acc_avg = [int(round(np.mean(score_val[:ind+1]),0)) for ind, i in enumerate(score_val)]
      #elif average == -1:
        #dates, acc_avg = zip(*tmp_df_name.groupby("Date")["Score"].mean().reset_index().values)
      else:
        acc_avg = tmp_df_name["Score"].rolling(average).mean().fillna(tmp_df_name["Score"]).values

      plt.plot(score_val, "--o", alpha = 0.1, label=name, color=color)
      plt.plot(acc_avg, "--*", color=color, alpha = 0.6)

      plt.xticks(range(len(tmp_df_name)), tmp_df_name["Date"].values, rotation = 45)
      plt.legend()
  plt.show()
  display(pd.DataFrame.from_dict(hcp_dict))

def visualise():
  widgets.interact(plot_history,
                 player_ec = widgets.Checkbox(value=False, description='En-Cheng Chang', disabled=False, indent=False),
                 player_d  = widgets.Checkbox(value=False, description='Dramon Yang', disabled=False, indent=False),
                 player_a  = widgets.Checkbox(value=False, description='Alan Grant', disabled=False, indent=False),
                 average = widgets.IntSlider(value=0, min=0, max=7, step=1, description='Average Param:'),
                 only_competitions = widgets.Dropdown(options=['YES', 'NO', 'ALL'], value='ALL', description='Show Only Competitions:'),
                 with_hcp = widgets.Dropdown(options=['YES', 'NO'], value='YES', description='Scores With HCP:'),
                 )
  print("")