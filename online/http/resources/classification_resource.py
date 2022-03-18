import json
import time

from flask import request
from flask_restful import Resource

from online import logger


class ClassificationResource(Resource):
    '''
    新闻标题分类路由，主要调用predict.predict_one
    '''
    def __init__(self, predict):
        # 使用传过来的predict对象，进行后面的新闻类别预测
        self.predict = predict

    def post(self):
        # 定义post请求
        # 解析输入json为一个dict
        data = request.get_json()
        init_time = time.time()
        result = {
            'status': 'OK', # 本次请求返回状态
            'msg': '' # 额外说明
        }
        request_id = data.get('request_id') # 支持传入request_id，便于线上追踪请求
        try:
            assert data, '请确保输入不为空'
            # 从data中取出用户输入的各种参数
            content = data['content']
            assert type(content) == str and len(content) <= 48, 'content must be str, and length <= 48'
            logger.info('request_id: {}, content: {} ...'.format(request_id, content))
            # 调用predict对象的predict_one方法
            r = self.predict.predict_one(content)
            # 将预测的类别放到result中
            result['result'] = r
        except Exception as e:
            # 出现异常，打印异常栈，更改本次请求状态为ERROR
            logger.exception(e)
            result['status'] = 'ERROR'
            result['msg'] = str(e)
        logger.info('request_id: {}, result: {} ..., cost time: {}s'.format(
            request_id, json.dumps(result, ensure_ascii=False), time.time() - init_time
        ))
        return result