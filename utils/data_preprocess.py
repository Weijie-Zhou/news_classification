import json
import random
from collections import Counter


def load_data(path, is_train_dev=True):
    # 读取数据
    data = []
    with open(path, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if line.strip() == '':
                continue
            dic = {}
            if is_train_dev:
                dic['inputs'] = line.strip().split('\t')[0]
                dic['labels'] = line.strip().split('\t')[1]
                data.append(dic)
            else:
                dic['inputs'] = line.strip()
                data.append(dic)
    return data


def save_data(path, data):
    # 保存处理后数据为json格式
    with open(path, 'w', encoding='utf8') as f:
        for i in data:
            f.write(json.dumps(i, ensure_ascii=False))
            f.write('\n')


def main(train_data, dev_data, test_data):
    labels = set([data['labels'] for data in train_data])
    config = {}
    config['train_size'] = len(train_data)
    config['eval_size'] = len(dev_data)
    config['task_tag'] = 'classification'
    config['labels_map'] = {label: int(index) for index, label in enumerate(labels)}
    config['labels_balance'] = {'train_labels': dict(Counter([data['labels'] for data in train_data])),
                                'eval_labels': dict(Counter([data['labels'] for data in dev_data]))}
    save_data('../data/train_augement.json', train_data)
    save_data('../data/eval.json', dev_data)
    save_data('../data/test.json', test_data)
    with open('../data/config.json', 'w', encoding='utf8') as f:
        json.dump(config, f, ensure_ascii=False)
 

if __name__ == '__main__':
    train_data = load_data('../data/train_augement.txt')
    random.shuffle(train_data)
    dev_data = load_data('../data/dev.txt')
    test_data = load_data('../data/test.txt', is_train_dev=False)
    print('train_data_length:', len(train_data))
    print('dev_data_length:', len(dev_data)) 
    print('test_data_length:', len(test_data))
    main(train_data, dev_data, test_data)