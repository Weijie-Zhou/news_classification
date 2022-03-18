import os
import sys
# 当前脚本的路径
curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath是当前脚本路径的上级目录，就是说如果自定义模块xxx在当前脚本的上级目录下，那么rootpath就是自定义模块所在的位置
rootPath = os.path.split(curPath)[0]
# 添加到sys.path中
sys.path.append(rootPath)

from flask import Flask
from flask_restful import Api

from online import logger
from online.http.resources.hello_resource import HelloResource
from online.http.resources.classification_resource import ClassificationResource
from predict import Predict


def start_server(port=8000):
    # 如果输入第1个参数，将第1个参数解析为端口号
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    # 实例化flask app
    app = Flask(__name__)
    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False)) # 设置ensure_ascii=False, 确保接口返回的中文正常
    api = Api(app)
    # 实例化predict对象，准备传入到resource里面
    predict = Predict()
    resource_class_kwargs = {'predict': predict}
    # 为api添加hello路由，classification路由
    api.add_resource(HelloResource, '/') # hello路由用于快速服务可用性
    api.add_resource(ClassificationResource, '/cls', resource_class_kwargs=resource_class_kwargs) # cls路由用于预测新闻分类
    # 启动服务，设置host port
    # host='0.0.0.0', 表示外部机器可以访问，必须设置为0.0.0.0
    # threaded=False，表示我们的主程序是单线程模式，需要一个一个处理请求(我们的word_graph对象不是线程安全的)
    logger.info('server starts port {}'.format(port))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=False)


if __name__ == '__main__':
    start_server()