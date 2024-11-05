import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import pandas as pd
from flask import Flask, render_template, redirect, url_for, jsonify, request
import sqlite3
from modules.predict import PredictModel

app = Flask(__name__)

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
        model = tf.keras.models.load_model("./model/my_modelmax.h5")
        data = pd.read_csv("./data/mixData.csv")
        file_path = './data/selected_columns_s.txt'
        prediction = PredictModel(model, data, file_path)
        conn = sqlite3.connect('./data/NBA.db')
        cursor = conn.cursor()
        selectedTeam1 = request.form.get('selectTeam1')
        cursor.execute('SELECT teamid FROM teams WHERE abbreviation = ?', (selectedTeam1,))
        selectedTeam1 = cursor.fetchall()
        print(selectedTeam1)
        selectedTeam2 = request.form.get('selectTeam2')
        cursor.execute('SELECT teamid FROM teams WHERE abbreviation = ?', (selectedTeam2,))
        selectedTeam2 = cursor.fetchall()

        selectedTeam1 = selectedTeam1[0][0]
        selectedTeam2 = selectedTeam2[0][0]
        selectedPlayers1 = list(map(int, request.form.getlist('selectedPlayer1')))
        selectedPlayers2 = list(map(int, request.form.getlist('selectedPlayer2')))

        # print(selectedTeam1)
        # print(selectedTeam2)
        # print(selectedPlayers1)
        # print(selectedPlayers2)

        result, probabilities = prediction.predict_game(selectedPlayers1, selectedPlayers2, selectedTeam1, selectedTeam2, selectedTeam1)
        prediction.print_prediction_result(result, probabilities)
        win = probabilities['win']
        loss = probabilities['loss']
        if win > loss:
            winResult = "主場獲勝"
        else :
            win = 2
            winResult = "客場獲勝"
        selectedTeam1 = str(selectedTeam1)
        selectedTeam2 = str(selectedTeam2)
        return render_template('predict.html', winResult=winResult, players1=selectedPlayers1, players2=selectedPlayers2, team1=selectedTeam1, team2=selectedTeam2)

# 返回首頁
@app.route('/back', methods=['GET'])
def back():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')