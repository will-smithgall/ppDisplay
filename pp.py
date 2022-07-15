from ensurepip import bootstrap
from re import M, sub
import re
import requests
import json
from dotenv import load_dotenv
import os
from flask import Flask, render_template

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
    best_scores_url = f"https://osu.ppy.sh/api/v2/users/{id}/scores/best?limit=1"

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

app = Flask(__name__)


@app.route("/")
def home():
    token = get_token()
    most_recent = get_best_scores(7429544, token)  # get_recent_score(7429544, token)

    # user_img = get_user_img(most_recent)
    # beatmap_card = get_beatmap_img(most_recent)

    return render_template("index.html", most_recent=most_recent)
    # return render_template("index.html", most_recent = most_recent)


if __name__ == "__main__":
    app.debug = True
    app.run()
