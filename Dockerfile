# 使用官方 Python 基础镜像
FROM python:3.9-slim
# 设置工作目录
WORKDIR /app
# 将当前目录下的所有文件复制到容器中
COPY . .
# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt
# 暴露 Streamlit 默认端口
EXPOSE 8501
# 启动 Streamlit 应用
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]