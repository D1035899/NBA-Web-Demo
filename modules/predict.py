import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split


class PredictModel():
    def __init__(self, model, data, file_path):
        self.scaler = None
        self.model = model
        self.data = data
        self.selected_columns = self.get_select_columns(file_path)
        self.index_of_home = self.get_index_home()
        self.index_of_team = self.get_index_team()


    def get_select_columns(self, filePath):
        with open(filePath, 'r') as file:
            selected_columns = [line.strip() for line in file]
        # print(selected_columns)
        return selected_columns

    def get_index_home(self):
        home_to_find = "home"
        index_of_home = self.selected_columns.index(home_to_find) if home_to_find in self.selected_columns else None
        return index_of_home

    def get_index_team(self):
        team_to_find = "team"
        index_of_team = self.selected_columns.index(team_to_find) if team_to_find in self.selected_columns else None
        return index_of_team


    def standardization(self):
        # 標準化
        scaler = MinMaxScaler()

        # 主客場
        self.data['home_basic'] = self.data['home_basic'].apply(lambda x: 1 if x == 'TRUE' else 0)

        # 依照gameid進行分組，每一組代表一場比賽
        games = self.data.groupby('gameid')

        # 將每場比賽中的所有球員數據合併成一個特徵向量
        X = []
        y = []

        for gameid, group in games:
            if len(group) != 30:  # 每場比賽最多有30位球員
                continue

            # 將每場比賽中的所有球員數據合併成一個特徵向量
            #game_features = group.drop(columns=['gameid', 'win', 'home_basic']).values.flatten()
            game_features = group[self.selected_columns].values.flatten()

            # 主客場
            #home_basic = group['home_basic'].iloc[0]
            #game_features = np.append(game_features, home_basic)

            X.append(game_features)
            y.append(group['win'].iloc[0])

        X = np.array(X)
        y = np.array(y)

        # 勝負
        y = np.where(y == 'TRUE', 1, 0)
        y = to_categorical(y, 2)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
        # X_train_df = pd.DataFrame(X_train)
        # X_train_df.to_csv('/content/X_trainA.csv', index=False)

        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        return scaler


    # 輸入新的資料進行預測
    def predict_game(self, team1_player_ids, team2_player_ids, team1, team2, homeis):
        self.scaler = self.standardization()
        # 創建球員字典，將球員ID映射到其特徵向量 @
        player_dict = {}
        player_dict1 = {}
        player_dict2 = {}
        player_groups = self.data.groupby('playerid')

        for player_id, group in player_groups:
            # 計算所有列的平均值，除了 'team'
            features = group[self.selected_columns].mean().values

            # 建立一個副本來避免影響原始數據
            features1 = features.copy()
            features2 = features.copy()

            # 替換特定位置的值
            features1[self.index_of_team] = team1
            features1[self.index_of_home] = homeis
            features2[self.index_of_team] = team2
            features2[self.index_of_home] = homeis

            # 將結果存入字典
            player_dict1[player_id] = features1
            player_dict2[player_id] = features2
        # print(features)

        if len(team1_player_ids) != 5 or len(team2_player_ids) != 5:
            raise ValueError("每支球隊需要提供5個球員的ID")
        # features1_df = pd.DataFrame(features)
        # features1_df.to_csv('/content/features1.csv', index=False)

        # 設playerid為0的球員，其特徵全為0
        player_dict[0] = np.zeros_like(features)

        # 從字典中提取球員特徵
        team1_features = [player_dict1[player_id] for player_id in team1_player_ids]
        team2_features = [player_dict2[player_id] for player_id in team2_player_ids]

        # 如果少於15名球員，用playerid為0的球員數據進行填充
        while len(team1_features) < 15:
            team1_features.append(player_dict[0])
        while len(team2_features) < 15:
            team2_features.append(player_dict[0])

        # 將兩隊特徵合併，並展平成一維陣列
        game_features = np.concatenate([f.flatten() for f in team1_features + team2_features])

        # 新增主客場訊息
        #home_basic = 1 if home_basic == 'TRUE' else 0
        #game_features = np.append(game_features, home_basic).reshape(1, -1)
        game_features = game_features.reshape(1, -1)
        game_features = game_features.astype(np.float32)

        # game_features_df = pd.DataFrame(game_features)
        # game_features_df.to_csv('/content/game_features.csv', index=False)
        # 標準化
        game_features = self.scaler.transform(game_features) # Use transform, not fit_transform
        # 預測
        prediction = self.model.predict(game_features)

        # 定義類別
        classes = ['win', 'loss']

        # 找出最可能的
        predicted_class = classes[np.argmax(prediction)]

        # 產生包含所有類別機率
        prediction = prediction / prediction.sum()
        probabilities = {cls: f"{prob:.10f}" for cls, prob in zip(classes, prediction[0])}

        return predicted_class, probabilities


    def print_prediction_result(self, result, probabilities):
        print(f"比赛结果預測: {result}")
        print("輸贏概率：")
        for cls, prob in probabilities.items():
            print(f"{cls}: {prob}")


if __name__ == "__main__":
    model = tf.keras.models.load_model("../model/my_modelmax.h5")
    data = pd.read_csv("../data/mixData.csv")
    file_path = '../data/selected_columns_s.txt'
    prediction = PredictModel(model, data, file_path)
    team1_player_ids = [1627759, 1629626, 201143, 1628401, 203935]
    team2_player_ids = [202699, 200782, 203954, 1630178, 201933]
    team1 = 2
    team2 = 22
    homeis = 2
    result, probabilities = prediction.predict_game(team1_player_ids, team2_player_ids, team1, team2, homeis)
    prediction.print_prediction_result(result, probabilities)