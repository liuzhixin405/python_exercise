#!/bin/bash

echo "========================================"
echo "        FeedMusic 项目启动脚本"
echo "========================================"
echo

# 检查 Python 环境
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查 Node.js 环境
echo "检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi

echo "环境检查完成！"
echo

# 启动后端服务
echo "启动后端服务..."
cd backend

echo "安装 Python 依赖..."
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "警告: 依赖安装可能有问题，但继续启动..."
fi

echo "启动 Flask 后端服务..."
python3 app.py &
BACKEND_PID=$!

echo "等待后端服务启动..."
sleep 5

# 启动前端服务
echo "启动前端服务..."
cd ../frontend

echo "安装 Node.js 依赖..."
npm install > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "警告: 依赖安装可能有问题，但继续启动..."
fi

echo "启动 React 前端服务..."
npm start &
FRONTEND_PID=$!

echo
echo "========================================"
echo "          服务启动完成！"
echo "========================================"
echo "后端服务: http://localhost:5000"
echo "前端应用: http://localhost:3000"
echo
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait 