import pandas as pd
import numpy as np
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
import tensorflow as tf
from tensorflow import nn


class PredictionModel():
    def __init__(self):
        self.model = self.loadModel("./model/final_model.h5")
        self.selectedFeatures = self.getFeaturesCols('./data/selected_columns_s.txt')
        self.data = pd.read_csv('./data/Looki.csv')
        self.shape = 1444


    def loadModel(self, modelPath):
        try:
            model = tf.keras.models.load_model(modelPath)
            print("載入模型成功")
            return model
        except Exception as e:
            print(f"載入模型失敗: {e}")
            return None


    def getFeaturesCols(self, filePath):
        with open(filePath, 'r') as file:
            features = [line.strip() for line in file]
        return features

    def process_player_ids(self, player_ids, data, selected_columns, result_array):
        for player_id in player_ids:
            found = False
            for idx in range(len(data) - 1, -1, -1):  # 從最後一行開始
                if data.loc[idx, 'playerid'] == player_id:  # 找到對應的 player_id
                    # 提取該行的特徵數據
                    selected_data = data.loc[idx, selected_columns]
                    # 存到結果陣列中
                    result_array.append(selected_data)
                    found = True
                    break  # 找到後跳出內部循環，進行下一個 player_id 的處理

            if not found:
                # 如果沒有找到該 player_id，填充一行全為 0 的數據
                zero_data = pd.Series([0] * len(selected_columns), index=selected_columns)
                result_array.append(zero_data)

    def prediction(self, team1Players, team2Players):
        result_array = []
        scaler = MinMaxScaler()
        self.process_player_ids(team1Players, self.data, self.selectedFeatures, result_array)
        self.process_player_ids(team2Players, self.data, self.selectedFeatures, result_array)
        # print(result)
        resultDf = pd.DataFrame(result_array)
        # print(resultDf)
        feature_vector = resultDf.values.flatten()
        feature_vector = np.append(feature_vector,776)
        # 將一維向量轉換為 DataFrame 的一行
        flattenedDf = pd.DataFrame([feature_vector])
        for column in flattenedDf.select_dtypes(include=['object']).columns:
            flattenedDf[column] = flattenedDf[column].apply(lambda x: 1 if x == 'TRUE' else 0)
        flattenedDf = scaler.fit_transform(flattenedDf)
        # input_vector = scaler.transform(flattenedDf)
        # print(f"flattenedDf: {flattenedDf}")
        input_vector = flattenedDf.reshape(1, 1, 511)
        # print()
        input_vector = input_vector.astype(np.float32)
        if self.model:
            predicted_class = self.model.predict(input_vector)
            return predicted_class
        else:
            print("沒有模型")
            return None


if __name__ == "__main__":
    model = PredictionModel()
    team1_player_ids = [1627759, 1629626, 201143, 1628401, 203935]
    team2_player_ids = [1629628, 1629656, 1630167, 1630193, 1630540]
    predictResult = model.prediction(team1_player_ids, team2_player_ids)
    print("Predicted class:", predictResult)
