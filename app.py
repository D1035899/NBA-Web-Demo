import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import pandas as pd
from flask import Flask, render_template, redirect, url_for, jsonify, request, session
import sqlite3
# from modules.predict import PredictModel
from modules.mod import PredictionModel

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 依據選擇的隊伍取得球員名單
def get_players_by_team(team_abbreviation):
    conn = sqlite3.connect('./data/NBA.db')
    cursor = conn.cursor()

    cursor.execute('SELECT playerid, name, team FROM players WHERE team = ?', (team_abbreviation,))
    players = cursor.fetchall()

    conn.close()
    return [{'id': player[0], 'name': player[1], 'team': player[2]} for player in players]

#取得球隊名單
def get_teams():
    conn = sqlite3.connect('./data/NBA.db')
    cursor = conn.cursor()

    cursor.execute('SELECT teamid, name, abbreviation FROM teams')
    teamRoster = cursor.fetchall()

    conn.close()
    return teamRoster

'''
    api part
'''

# 取得首頁
@app.route('/')
def index():
    teamRoster = get_teams()
    teamRoster = [(team[1], team[2]) for team in teamRoster] # team[0]: name, team[1]: abbreviation
    return render_template('index.html', teams=teamRoster)

# 取得球員名單，並回傳json形式的名單
@app.route('/get_players/<team_abbreviation>')
def get_players(team_abbreviation):
    players = get_players_by_team(team_abbreviation)
    return jsonify({'players': players})

#進行預測
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        model = PredictionModel()
        conn = sqlite3.connect('./data/NBA.db')
        cursor = conn.cursor()
        selectedTeam1 = request.form.get('selectTeam1')
        cursor.execute('SELECT teamid FROM teams WHERE abbreviation = ?', (selectedTeam1,))
        selectedTeam1 = cursor.fetchall()
        selectedTeam2 = request.form.get('selectTeam2')
        cursor.execute('SELECT teamid FROM teams WHERE abbreviation = ?', (selectedTeam2,))
        selectedTeam2 = cursor.fetchall()

        selectedTeam1 = selectedTeam1[0][0]
        selectedTeam2 = selectedTeam2[0][0]
        selectedPlayers1 = list(map(int, request.form.getlist('selectedPlayer1')))
        selectedPlayers2 = list(map(int, request.form.getlist('selectedPlayer2')))
        print(f"player1: {selectedPlayers1}")
        print(f"player2: {selectedPlayers2}")
        predictResult = model.prediction(selectedPlayers1, selectedPlayers2)
        print(f"{predictResult}")
        print(f"主場勝率: {predictResult[0][0]}")
        print(f"客場勝率: {predictResult[0][1]}")

        if(predictResult[0][0] > predictResult[0][1]):
            winner = '主場'
            loser = '客場'
        else:
            winner = '客場'
            loser = '主場'

        selectedTeam1 = str(selectedTeam1)
        selectedTeam2 = str(selectedTeam2)
        if 'predictions' not in session:
            session['predictions'] = []

        prediction_id = len(session['predictions']) + 1
        if 'predictions' in session:
            if len(session['predictions']) == 0:
                print('沒有偵測到相同的隊伍組合')
                pass
            else:
                for prediction in session['predictions']:
                    if set(prediction['players1']) == set(selectedPlayers1) and set(prediction['players2']) == set(selectedPlayers2):
                        print('偵測到相同的隊伍組合')
                        return render_template('predict.html', predictResult=prediction['result'], winner=prediction['winner'], players1=prediction['players1'], players2=prediction['players2'], team1=prediction['team1'], team2=prediction['team2'])
                    elif set(prediction['players1']) == set(selectedPlayers2) and set(prediction['players2']) == set(selectedPlayers1):
                        print('偵測到相同的隊伍組合 (反向)')
                        return render_template('predict.html', predictResult=prediction['result'], winner=prediction['loser'], players1=prediction['players2'], players2=prediction['players1'], team1=prediction['team2'], team2=prediction['team1'])
                    else:
                        print('沒有偵測到相同的隊伍組合')
        prediction_data = {
            'id': prediction_id,
            'result': predictResult.tolist(),
            'team1': selectedTeam1,
            'team2': selectedTeam2,
            'players1': selectedPlayers1,
            'players2': selectedPlayers2,
            'winner': winner,
            'loser': loser
        }
        session['predictions'].append(prediction_data)
        print(f"儲存的預測結果:\n{session['predictions']}")
        return render_template('predict.html', predictResult=predictResult, winner=winner, players1=selectedPlayers1, players2=selectedPlayers2, team1=selectedTeam1, team2=selectedTeam2)

# 返回首頁
@app.route('/back', methods=['GET'])
def back():
    return redirect(url_for('index'))

# @app.route('/compare', methods=['POST'])
# def compare():
#     team1Players = request.json.get('team1Players')
#     team2Players = request.json.get('team2Players')

#     model = PredictionModel()
#     new_prediction_result = model.prediction(team1Players, team2Players)

#     # 從 session 中取得之前的預測結果
#     last_prediction = session.get('last_prediction')

#     if last_prediction:
#         comparison_result = {
#             'new_prediction': new_prediction_result.tolist(),
#             'last_prediction': last_prediction,
#             'is_same': new_prediction_result.tolist() == last_prediction
#         }
#     else:
#         comparison_result = {
#             'new_prediction': new_prediction_result.tolist(),
#             'last_prediction': None,
#             'is_same': False
#         }
#     return jsonify(comparison_result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')