import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from modules.predict import PredictModel

app = Flask(__name__)

def get_players():
    conn = sqlite3.connect('./data/NBA.db')
    cursor = conn.cursor()

    cursor.execute('SELECT playerid, name FROM players')
    playersBasicData = cursor.fetchall()

    conn.close()
    return playersBasicData

def get_teams():
    conn = sqlite3.connect('./data/NBA.db')
    cursor = conn.cursor()

    cursor.execute('SELECT teamid, name FROM teams')
    teamsBasicData = cursor.fetchall()

    conn.close()
    return teamsBasicData

@app.route('/')
def index():
    players = get_players()
    teams = get_teams()
    return render_template('index.html', players=players, teams=teams)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        model = tf.keras.models.load_model("./model/my_modelmax.h5")
        data = pd.read_csv("./data/mixData.csv")
        file_path = './data/selected_columns_s.txt'
        prediction = PredictModel(model, data, file_path)
        selectedTeam1 = request.form.get('selectTeam1')
        selectedTeam2 = request.form.get('selectTeam2')
        selectedPlayers1 = list(map(int, request.form.getlist('selectedPlayer1')))
        selectedPlayers2 = list(map(int, request.form.getlist('selectedPlayer2')))


        print(f"team1: {selectedTeam1}")
        print(f"player: {selectedPlayers1}\n")
        print(f"team2: {selectedTeam2}")
        print(f"player: {selectedPlayers2}")

        result, probabilities = prediction.predict_game(selectedPlayers1, selectedPlayers2, selectedTeam1, selectedTeam2, selectedTeam1)
        prediction.print_prediction_result(result, probabilities)
        win = probabilities['win']
        loss = probabilities['loss']
        if win > loss:
            winResult = "主場獲勝"
        else :
            win = 2
            winResult = "客場獲勝"
        return render_template('predict.html', predictResult=result, winResult=winResult, players1=selectedPlayers1, players2=selectedPlayers2, team1=selectedTeam1, team2=selectedTeam2)

@app.route('/back', methods=['GET'])
def back():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')