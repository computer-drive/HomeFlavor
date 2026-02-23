# HomeFlavor · 家味

供我家饭店使用的内部管理系统。帮助饭店运行的更高效。

## TODO

- [ ] 服务员登录系统
- [ ] 订单创建系统
- [ ] 后厨大屏自动刷新
- [ ] 加菜标记
- [ ] 出菜匹配
- [ ] 营业额统计

## 安装

```bash
# 克隆仓库
git clone https://github.com/computer-drive/HomeFlavor.git
cd homeflavor

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\scripts\activate
# Mac/Linux
source venv/bin/actvate

# 安装依赖
pip install -r requirements.txt
```



## 做此项目的原因

一名初三生，学过几年编程，但不想打比赛刷题。家里开饭店，想用代码解决实际问题，于是诞生了此项目。本项目仅由我一人开发。



# 项目结构

```
homeflavor/
├── app/
│   ├── __init__.py      # 应用工厂
│   ├── database.py      # 数据库操作
│   ├── auth.py          # 登录相关
│   ├── waiter.py        # 服务员点菜
│   ├── kitchen.py       # 后厨大屏
│   └── cashier.py       # 收银结账
├── templates/           # HTML页面
├── static/              # CSS/JS文件
└── run.py               # 启动入口
```

