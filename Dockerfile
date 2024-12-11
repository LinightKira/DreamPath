FROM python:3.10 as builder

WORKDIR /home/DreamPath_Server

COPY requirements.txt requirements.txt
#RUN  pip install --upgrade pip
#RUN  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install -r requirements.txt

COPY app_server app_server
COPY migrations migrations
#COPY app.py config.py fssl.key fssl.pem ./

CMD ["flask","db","upgrade"]
#CMD ["python", "init_db.py"]   #初始化数据库
CMD ["python", "app.py"]
