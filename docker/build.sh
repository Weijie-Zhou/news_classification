img_name=api-news-classification # 镜像名，即项目名
img_tag=`date '+%Y%m%d_%H%M%S'` # 声明镜像tag为 日期+时间c

docker build -f docker/Dockerfile -t ${img_name}:${img_tag} .