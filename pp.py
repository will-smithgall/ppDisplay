from ensurepip import bootstrap
from re import M, sub
import re
import requests
import json
from dotenv import load_dotenv
import os
from flask import Flask, render_template, Markup

load_dotenv()


def get_token():
    token_url = "https://osu.ppy.sh/oauth/token"

    response = requests.post(
        token_url,
        json={
            "client_id": os.environ["CLIENT_ID"],
            "client_secret": os.environ["CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "scope": "public",
        },
    )

    return response.json()


def get_best_scores(id, token):
    best_scores_url = f"https://osu.ppy.sh/api/v2/users/{id}/scores/best?limit=5"

    response = requests.get(
        best_scores_url, headers={"Authorization": f"Bearer {token['access_token']}"}
    )

    return response.json()


def get_recent_score(id, token):
    scores_url = (
        f"https://osu.ppy.sh/api/v2/users/{id}/scores/recent?include_fails=1&limit=1"
    )

    response = requests.get(
        scores_url, headers={"Authorization": f"Bearer {token['access_token']}"}
    )

    if len(response.json()) == 0:
        print(f"Player ID {id} has not submitted a play in the last 24 hours!")

    return response.json()

def get_user_img(txt):
    for play in txt:
        user_img = play["user"]["avatar_url"]

    return user_img


# Passes in json formatted repsonse
# returns id of beatmap
def get_beatmap_img(txt):
    for play in txt:
        beatmapset_ids = play["beatmapset"]["covers"]["card@2x"]

    return beatmapset_ids


def get_play_info(txt):
    submitted_data = []

    for item in txt:
        item_stats = []
        item_stats.append(item["beatmapset"]["title"])
        item_stats.append(item["beatmapset"]["artist"])

        item_stats.append(item["rank"])
        item_stats.append(item["accuracy"])

        if item["pp"] is None:
            item_stats.append(0)
        else:
            item_stats.append(item["pp"])

        item_stats.append(item["mods"])
        item_stats.append(item["score"])
        item_stats.append(item["max_combo"])
        stats_formatted = f"{item['statistics']['count_300'] + item['statistics']['count_geki']}/{item['statistics']['count_100'] + item['statistics']['count_katu']}/{item['statistics']['count_50']}/{item['statistics']['count_miss']}"
        item_stats.append(stats_formatted)

        item_stats.append(item["beatmap"]["ar"])
        item_stats.append(item["beatmap"]["bpm"])
        item_stats.append(item["beatmap"]["difficulty_rating"])

        item_stats.append(item["beatmapset"]["covers"]["cover@2x"])

        submitted_data.append(item_stats)

        # if the flag is true, we also want to print, otherwise ignore

    return_string = ""

    for dataset in submitted_data:
        if dataset[5] == []:
            mods = "No Mod"
        else:
            mods = ", ".join(dataset[5])

        return_string += (
            f"{dataset[0]} - {dataset[1]}<br>"
            f"{dataset[2]}, {(dataset[3]*100):.2f}%, {dataset[4]:.1f}pp, {dataset[8]}<br>"
            f"{mods}, {dataset[7]:,}x, Score: {dataset[6]:,}<br>"
            f"AR {dataset[9]}, {dataset[10]} bpm, {dataset[11]} Stars<br>"
        )

    return return_string

#Get info
token = get_token()
most_recent = get_recent_score(7429544, token)
top_plays = get_best_scores(7429544, token)

app = Flask(__name__)



@app.route("/")
def home():
    formatted_recent = get_play_info(most_recent)
    user_img = get_user_img(most_recent)
    beatmap_card = get_beatmap_img(most_recent)
    return render_template("index.html", formatted_recent = Markup(formatted_recent), user_img = user_img, beatmap_card = beatmap_card)



if __name__ == "__main__":
    app.debug = True
    app.run()   