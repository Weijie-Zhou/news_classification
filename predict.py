import math
import time
import json
import torch
from transformers import AutoTokenizer


class Predict():
    def __init__(self):
        # 初始化设备
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained('./chinese-roberta-wwm-ext')
        # 加载模型
        self.model = torch.load('./output/pytorch_model.h5', map_location=self.device)
        self.model.eval()
        # 将模型拷贝到设备上
        self.model.to(self.device)
        # 加载labels_map
        self.labels_map = json.load(open('data/config.json'))['labels_map']
        self.labels_map = {int(value): key for key, value in self.labels_map.items()}

    def predict_one(self, review):
        # 对一条传入的样本进行预测
        if type(review) == str:
            review = [review]
        encoded = self.tokenizer.batch_encode_plus(batch_text_or_text_pairs=review,
                                              padding=True,
                                              max_length=48,
                                              truncation=True)
        new_batch = {}
        for key, value in encoded.items():
            new_batch[key] = torch.tensor(value, device=self.device)
        eval_loss, logits = self.model(**new_batch)
        # 通过argmax提取概率最大值的索引来获得预测标签的id
        batch_predictions = torch.argmax(logits, dim=-1).detach().cpu().numpy().tolist()
        # 将预测结果加入到predictions
        return self.labels_map[batch_predictions[0]]

    def predict_batch(self, reviews, batch_size=32):
        # 对传入的样本按照batch_size大小进行批预测
        predict_steps = math.ceil(len(reviews) / batch_size)
        print('predict_steps: ', predict_steps)
        # 保存预测结果
        predictions = []
        for i in range(predict_steps):
            print('now step: ', i)
            review_lst = list(reviews[i*batch_size: (i+1)*batch_size])
            encoded = self.tokenizer.batch_encode_plus(batch_text_or_text_pairs=review_lst,
                                                  padding=True,
                                                  max_length=48,
                                                  truncation=True)
            new_batch = {}
            for key, value in encoded.items():
                new_batch[key] = torch.tensor(value, device=self.device)
            eval_loss, logits = self.model(**new_batch)
            # 通过argmax提取概率最大值的索引来获得预测标签的id
            batch_predictions = torch.argmax(logits, dim=-1).detach().cpu().numpy().tolist()
            # 将预测结果加入到predictions
            predictions += [self.labels_map[prediction] for prediction in batch_predictions]
        return predictions


if __name__ == '__main__':
    # start = time.time()
    # test_data = []
    # with open('data/test.txt', 'r', encoding='utf8') as f:
    #     for line in f.readlines():
    #         if line.strip() == '':
    #             continue
    #         test_data.append(line.strip())
    # print(len(test_data))
    # predict_label = predict_batch(test_data, 32)
    # print(len(predict_label), len(test_data))
    # print(time.time() - start)
    # with open('result.txt', 'w', encoding='utf8') as f:
    #     for i in predict_label:
    #         f.write(i + '\n')
    start = time.time()
    test_text = '郑智连续2年专砍领头羊一击便冲垮400分钟0失球防线'
    predict = Predict()
    print(predict.predict_one(test_text))
    print(time.time() - start)