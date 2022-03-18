import logging.handlers

# 获取logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # 设置logger级别

# 生成文件handler，打印到文件
# 按天滚动的log，一天滚动一次，只保留最近7个日志文件(即保留最近7天)
file_handler = logging.handlers.TimedRotatingFileHandler('./logs/root.log', 'D', 1, 7)
file_handler.setLevel(logging.DEBUG)

# 设置formatter
# 打印日志时间、级别、文件名、行号、函数名称、内容
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s: %(lineno)s - %(funcName)s() - %(message)s'
)

# 将formatter设置到两个handler
file_handler.setFormatter(formatter)

# 将handler设置到logger
logger.addHandler(file_handler)