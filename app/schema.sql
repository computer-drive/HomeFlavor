-- 运行此文件以创建所有需要的表

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_num INTEGER UNIQUE NOT NULL,
    table_num INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN (
        'pending', -- 待处理（下单后的状态）
        'cooking', -- 制作中
        'done',    -- 已完成（全部的菜出完）
        'canceled',-- 已取消（用户或管理员取消订单）
        'paid'     -- 已结账（用户已支付）
    )),
    items_json TEXT NOT NULL, -- 订单中的菜单项，JSON格式存储
    total_price INTEGER NOT NULL -- 订单总金额，单位：分
);

-- 菜单表
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- 菜品名称
    price INTEGER NOT NULL, -- 菜品单价，单位：分
    category TEXT NOT NULL, -- 菜品分类
    description TEXT, -- 菜品描述
    image_url TEXT, -- 菜品图片URL
    is_available INTEGER DEFAULT 1, -- 是否可用，默认值为1（可用）
    options_json TEXT -- 菜品可选配置，JSON格式存储
)

    