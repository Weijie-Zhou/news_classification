import random
from multiprocessing import Pool
import pandas as pd
from nlpcda import Similarword, CharPositionExchange, baidu_translate, Simbert
from sqlalchemy import create_engine

# 配置数据库
engine = create_engine('mysql+pymysql://xxxx:xxxxxx#@127.0.0.1:3306/train')


def similar_word(text, nums=5):
    # 随机同义词替换
    smw = Similarword(
        create_num=nums, # 返回最多几个增强文本
        change_rate=0.3, # 文本改变率
        seed=random.randint(0, 1000) # 随机种子
    )
    return smw.replace(text)


def char_position_exchange(text, nums=5):
    # 随机置换邻近的字
    s = CharPositionExchange(
        create_num=nums, # 返回最多几个增强文本
        change_rate=0.3, # 文本改变率
        char_gram=5, # 某个字只和邻近的5个字交换
        seed=random.randint(0, 1000) # 随机种子
    )
    res = s.replace(text)
    return res


def sim_bert(text, nums=5):
    config = {
        'model_path': './chinese_simbert_L-4_H-312_A-12',
        'CUDA_VISIBLE_DEVICES': '0,1',
        'max_len': len(text),
        'seed': random.randint(0, 1000) # 随机种子
    }
    simbert = Simbert(config=config)
    synonyms = simbert.replace(sent=text, create_num=nums)
    return [data[0] for data in synonyms]


def translate(text, nums=5):
    # 翻译互转实现的增强
    # 两遍洗数据法（回来的中文一般和原来不一样，要是一样，就不要了，靠运气？）
    res = []
    for i in range(nums):
        en_s = baidu_translate(content=text, appid='xxxxxxxx', secretKey='xxxxxxx', t_from='zh', t_to='en')
        zh_s = baidu_translate(content=en_s, appid='xxxxxxxx', secretKey='xxxxxxx', t_from='en', t_to='zh')
        res.append(zh_s)
    return res


def main_func(i, nums=5):
    # 对传入的文本进行文本增强
    try:
        print(i)
        dic = lst[i]
        text = dic['inputs']
        labels = dic['labels']
        iterators = dic['iterators']
        res = []
        for i in range(iterators):
            # 随机取一种文本增强方法
            funcs = [similar_word, char_position_exchange, sim_bert, translate]
            func = random.choice(funcs)
            augements = func(text, nums)
            res.extend([{'inputs': augement, 'labels': labels} for augement in augements])
        res_df = pd.DataFrame(res)
        res_df.to_sql('data', con=engine, if_exists='append', index=False)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    train_data = []
    with open('../data/train.txt', 'r', encoding='utf8') as f:
        for line in f.readlines():
            if line.strip() == '':
                continue
            inputs, labels = line.strip().split('\t')
            dic = {}
            dic['inputs'] = inputs
            dic['labels'] = labels
            train_data.append(dic)
    train_df = pd.DataFrame(train_data)
    print(train_df.head())
    # 对以下标签的数据进行文本增强
    need_augement_label = ['教育', '家居', '财经', '房产', '社会', '游戏', '彩票', '星座', '时尚']
    lst = []
    for label in need_augement_label:
        label_df = train_df[train_df['labels']==label]
        # 将该标签的数据量补齐到50000左右
        sample_len = (50000 - len(label_df)) // 5
        print('sample_len:', sample_len)
        if sample_len >= len(label_df):
            iterators = sample_len // len(label_df) + 1
            for i in range(len(label_df['inputs'])):
                dic = {}
                dic['inputs'] = label_df['inputs'].iloc[i]
                dic['labels'] = label
                dic['iterators'] = iterators
                lst.append(dic)
        else:
            sample = random.sample(list(label_df['inputs']), sample_len)
            for i in sample:
                dic = {}
                dic['inputs'] = i
                dic['labels'] = label
                dic['iterators'] = 1
                lst.append(dic)
    # 使用多进程进行文本增强
    pool = Pool(10)
    pool.map(main_func, [i for i in range(len(lst))])

    augement_df = pd.read_sql('select * from data', con=engine)
    all_df = pd.concat([train_df, augement_df])
    with open('../data/train_augement.txt', 'w', encoding='utf8') as f:
        for i in range(len(all_df)):
            f.write(all_df.iloc[i]['inputs'] + '\t' + all_df.iloc[i]['labels'] + '\n')