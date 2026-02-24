import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from flask import g, current_app
import json
import os
class DatabaseConnection:
    '''
    控制数据库连接
    '''
    def __init__(self):
        self.connection: sqlite3.Connection = None # type: ignore
        
        self.accounts = None
        self.orders = None
        self.dishes = None

    def connect(self):
        '''
        连接数据库
        Argruments:
            None
        Returns:
            None
        '''
        
        # 判断是否已经连接
        if self.connection:
            current_app.logger.warning("Can't connect to database because it's already connected.")
            return self.connection
        
        # 连接数据库
        self.connection = sqlite3.connect(current_app.config['database']["file"])

        # 启用行工厂
        self.connection.row_factory = sqlite3.Row # type: ignore

        # 启用外键约束
        self.connection.execute("PRAGMA foreign_keys = ON;") # type: ignore

        # 初始化DAO实例
        self.accounts = AccountDAO(self)
        self.orders = OrderDAO(self)
        self.dishes = DishDAO(self)

        current_app.logger.info(f"Connected to database: {current_app.config['database']['file']}")

        return self.connection
    
    def close(self):
        '''
        关闭数据库连接
        Argruments:
            None
        Returns:
            None
        '''
        # 判断数据库是否连接
        if self.connection:
            self.connection.close()
            self.connection = None #type: ignore
            current_app.logger.info("Database connection closed.")
        else:
            current_app.logger.warning("Can't close database because it's not connected.")
    
    def commit(self):
        '''
        提交数据库事务
        Argruments:
            None
        Returns:
            None
        '''

        if self.connection:
            self.connection.commit()
        else:
            current_app.logger.warning("Can't commit database because it's not connected.")
    
    def rollback(self):
        '''
        回滚数据库事务
        Argruments:
            None
        Returns:
            None
        '''

        if self.connection:
            self.connection.rollback()
        else:
            current_app.logger.warning("Can't rollback database because it's not connected.")

    def execute(self, sql: str, params: tuple = ()):
        '''
        执行SQL语句。
        Argruments:
            sql: SQL语句
            params: 参数
        Returns:
            None
        '''
        if self.connection:
            cursor = self.connection.cursor()
            return cursor.execute(sql, params)
        else:
            current_app.logger.warning("Can't execute SQL because it's not connected.")

    def fetch_one(self, sql: str, params: tuple = ()):
        '''
        执行SQL语句并返回第一条记录。
        Argruments:
            sql: SQL语句
            params: 参数
        Returns:
            None
        '''
        cursor = self.execute(sql, params)
        row = cursor.fetchone() 
        return dict(row) if row else None
    
    def fetch_all(self, sql: str, params: tuple = ()):
        '''
        执行SQL语句并返回所有记录。
        Argruments:
            sql: SQL语句
            params: 参数
        Returns:
            None
        '''
        cursor = self.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def insert(self, sql: str, params: tuple = ()):
        '''
        执行SQL语句并返回插入的记录ID。
        Argruments:
            sql: SQL语句
            params: 参数
        Returns:
            int: 插入的记录ID
        '''
        cursor: sqlite3.Cursor = self.execute(sql, params)
        return cursor.lastrowid
    
        

    # 上下文管理器
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.commit()
        else:
            self.rollback()

        self.close()

# flask 集成
def get_dbconn():
    '''
    获取当前请求的数据库连接。
    Arguments:
        None
    Returns:
        Database: 数据库连接

    '''
    if 'db' not in g:
        g.db = DatabaseConnection()
        g.db.connect()
    else:
        current_app.logger.debug("Using existing database connection in this request.")
        
    return g.db

def close_dbconn  (e=None):
    '''
    关闭当前请求的数据库连接。
    Arguments:
        e: 异常
    Returns:
        None
    '''

    db = g.pop('db', None)

    if db is not None:
        db.close()
        
class BaseDAO:
    '''
    控制数据库操作的基类
    '''
    def __init__(self, conn: DatabaseConnection=None): # type:ignore
        self.conn = conn


    def _get_conn(self):
        '''获取数据库连接'''
        return self.conn

    
    def execute(self, sql, params=()):
        '''执行SQL并返回cursor'''
        return self.conn.execute(sql, params) #type: ignore
    
    def executemany(self, sql, params_list):
        '''批量执行SQL'''
        return self.conn.executemany(sql, params_list)#type: ignore
    
    def fetch_one(self, sql, params=()):
        '''查询单条记录，返回字典'''
        cursor = self.execute(sql, params)
        row = cursor.fetchone()#type: ignore
        if row:
            return dict(row)
        return None
    
    def fetch_all(self, sql, params=()):
        '''查询多条记录，返回字典列表'''
        cursor = self.execute(sql, params)
        rows = cursor.fetchall()#type: ignore
        return [dict(row) for row in rows]
    
    def insert(self, sql, params=()):
        '''插入并返回自增ID'''
        cursor = self.execute(sql, params)
        return cursor.lastrowid #type: ignore

class AccountDAO:
    '''
    控制账户的数据库操作
    '''
    def __init__(self, conn: DatabaseConnection=None): # type:ignore
        self.conn = conn
    
    def create(self, username:str, password: str, is_admin: bool=False, enabled: bool=True):
        '''
        创建一个新账户
        Arguments:
            username: 用户名
            password: 密码（未加密）
            is_admin: 是否为管理员
            enabled: 是否启用
        Returns:
            int: 新账户的ID
        '''
        # 生成密码哈希
        password_hash = generate_password_hash(password)

        sql = '''
        INSERT INTO users (username, password, is_admin, enabled)
        VALUES (?, ?, ?, ?)
        '''
        params = (username, password_hash, int(is_admin), int(enabled))
        return self.conn.insert(sql, params)
    
    def auth(self, username: str, password: str):
        '''
        
        验证账户登录
        Arguments:
            username: 用户名
            password: 密码（未加密）
        Returns:
            dict: 账户信息字典（包含id, username, is_admin, enabled）
            None: 如果验证失败
        '''
        # 先根据用户名查询用户
        sql = '''
        SELECT id, username, password, is_admin, enabled FROM users
        WHERE username = ?
        '''
        params = (username,)
        
        user = self.conn.fetch_one(sql, params)
        
        # 验证密码
        if user and check_password_hash(user['password'], password):
            # 移除密码字段后返回
            del user['password']
            return user
        return None
    
    def get_user(self, user_id: int = 0, username: str = ""):
        '''
        获取账户信息。传递账户ID或用户名，返回账户信息。
        Arguments:
            user_id: 账户ID
            username: 用户名
        Returns:
            dict: 账户信息字典（包含id, username, is_admin, enabled）
            None: 如果未找到账户
        '''
        if user_id:
            sql = '''
            SELECT id, username, is_admin, enabled FROM users
            WHERE id = ?
            '''
            params = (user_id,)
        elif username:
            sql = '''
            SELECT id, username, is_admin, enabled FROM users
            WHERE username = ?
            '''
            params = (username,)
        else:
            return None
    
    def get_all(self):
        '''
        获取所有账户信息。
        Arguments:
            None
        Returns:
            list: 账户信息字典列表（包含id, username, is_admin, enabled）
        '''
        sql = '''
        SELECT id, username, is_admin, enabled FROM users
        '''
        return self.conn.fetch_all(sql)
    
class OrderDAO:
    '''
    控制订单的数据库操作
    '''
    def __init__(self, conn: DatabaseConnection=None): # type:ignore
        self.conn = conn
    
    def create(self, 
        table_num: int,
        items: list[tuple[int, int]]
    ):
        '''
        创建一个新订单。
        Arguments:
            table_num: 桌号
            items: 订单中的菜单项ID列表。每个元素为一个元组，包含菜单项ID和数量。
        Returns:
            int: 新订单的ID
        '''

        # 获取当前最新订单的订单号，计算出下一个订单号    
        ## 查询今天已有多少单
        result = self.conn.fetch_one("SELECT count(*) as count FROM orders WHERE DATE(time) = DATE('now')")
        
        # 如果今天没有订单，则从1开始
        if result is None:
            next_order_num = 1
        else:
            next_order_num = result["count"] + 1
        
        # 查询menu表，将含有菜品id的items转换为数据库格式的json
        ## 获取items参数中的所有菜单项ID
        items_id = [item[0] for item in items]

        ## 查询menu表，获取所有菜单项的信息
        placeholders = ','.join(['?'] * len(items_id))
        dishs = self.conn.fetch_all(f"SELECT id, name, price FROM menu WHERE id IN ({placeholders})", tuple(items_id))
        
        ## 转换为字典方便查询
        dish_dict = {dish["id"]: dish for dish in dishs}

        ## 创建items_json，并计算总价格
        item_json_list = []
        total_price : int = 0
        for item in items:
            item_json_list .append({
                "id": item[0] , # 菜单项ID
                "name": dish_dict[item[0]]["name"], # 菜单项名称
                "price": dish_dict[item[0]]["price"], # 菜单项价格
                "quantity": item[1], # 数量
            })
            total_price += dish_dict[item[0]]["price"] * item[1]
        
        ## 转换为json字符串
        items_json = json.dumps(item_json_list, ensure_ascii=False)


        # 插入订单到orders数据库
        sql = '''
        INSERT INTO orders (order_num, table_num, items_json, total_price, status)
        VALUES (?, ?, ?, ?, 'pending')
        '''
        params = (next_order_num, table_num, items_json, total_price)
        
        return self.conn.insert(sql, params)
    
class DishDAO:
    '''
    菜品数据访问对象
    对应表: menu
    '''
    
    def __init__(self, conn: DatabaseConnection = None):
        '''
        初始化菜品DAO
        Args:
            conn: 数据库连接
        '''
        self.conn = conn
    
    def _get_db(self):
        '''获取数据库连接'''
        return self.conn
    
    # ==================== 基础增删改查 ====================
    
    def create(self, 
               name: str, 
               price: int, 
               category: str, 
               description: str = "",
               image_url: str = "",
               is_available: bool = True,
               options_json: dict = None) -> int:
        '''
        创建新菜品
        Args:
            name: 菜品名称
            price: 价格（单位：分）
            category: 分类
            description: 描述
            image_url: 图片URL
            is_available: 是否可用
            options_json: 可选配置（如辣度、规格等）
        Returns:
            int: 新菜品的ID
        '''
        db = self.conn
        
        # 处理options_json
        if options_json is None:
            options_json = {}
        options_str = json.dumps(options_json, ensure_ascii=False)
        
        sql = '''
        INSERT INTO menu 
        (name, price, category, description, image_url, is_available, options_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (name, price, category, description, image_url, 
                  int(is_available), options_str)
        
        return db.insert(sql, params)
    
    def get_by_id(self, dish_id: int) -> dict:
        '''
        根据ID获取菜品
        Args:
            dish_id: 菜品ID
        Returns:
            dict: 菜品信息，不存在返回None
        '''
        db = self.conn
        
        dish = db.fetch_one('SELECT * FROM menu WHERE id = ?', (dish_id,))
        if dish:
            # 解析JSON字段
            if dish.get('options_json'):
                dish['options'] = json.loads(dish['options_json'])
            else:
                dish['options'] = {}
            # 删除原始JSON字段（可选）
            del dish['options_json']
        
        return dish
    
    def update(self, dish_id: int, **kwargs) -> bool:
        '''
        更新菜品信息
        Args:
            dish_id: 菜品ID
            **kwargs: 要更新的字段，如 name='新名称', price=3000
        Returns:
            bool: 是否更新成功
        '''
        db = self.conn
        
        # 构建动态SQL
        fields = []
        values = []
        
        # 特殊处理options_json
        if 'options' in kwargs:
            kwargs['options_json'] = json.dumps(kwargs.pop('options'), ensure_ascii=False)
        
        for key, value in kwargs.items():
            # 只更新menu表中存在的字段
            if key in ['name', 'price', 'category', 'description', 
                      'image_url', 'is_available', 'options_json']:
                fields.append(f'{key} = ?')
                if key == 'is_available':
                    values.append(int(value))
                else:
                    values.append(value)
        
        if not fields:
            return False
        
        values.append(dish_id)
        sql = f'UPDATE menu SET {", ".join(fields)} WHERE id = ?'
        
        db.execute(sql, tuple(values))
        db.commit()
        return True
    
    def delete(self, dish_id: int) -> bool:
        '''
        删除菜品（物理删除）
        Args:
            dish_id: 菜品ID
        Returns:
            bool: 是否删除成功
        '''
        db = self.conn
        db.execute('DELETE FROM menu WHERE id = ?', (dish_id,))
        db.commit()
        return True
    
    def set_availability(self, dish_id: int, is_available: bool) -> bool:
        '''
        设置菜品是否可用
        Args:
            dish_id: 菜品ID
            is_available: 是否可用
        Returns:
            bool: 是否设置成功
        '''
        return self.update(dish_id, is_available=is_available)
    
    # ==================== 查询方法 ====================
    
    def get_all(self, include_unavailable: bool = False) -> list[dict]:
        '''
        获取所有菜品
        Args:
            include_unavailable: 是否包含不可用的菜品
        Returns:
            list: 菜品列表
        '''
        db = self.conn
        
        if include_unavailable:
            dishes = db.fetch_all('SELECT * FROM menu ORDER BY category, id')
        else:
            dishes = db.fetch_all('''
                SELECT * FROM menu 
                WHERE is_available = 1 
                ORDER BY category, id
            ''')
        
        # 解析JSON字段
        for dish in dishes:
            if dish.get('options_json'):
                dish['options'] = json.loads(dish['options_json'])
            else:
                dish['options'] = {}
            del dish['options_json']
        
        return dishes
    
    def get_by_category(self, category: str) -> list[dict]:
        '''
        获取指定分类的菜品
        Args:
            category: 分类名称
        Returns:
            list: 菜品列表
        '''
        db = self.conn
        
        dishes = db.fetch_all('''
            SELECT * FROM menu 
            WHERE category = ? AND is_available = 1
            ORDER BY id
        ''', (category,))
        
        for dish in dishes:
            if dish.get('options_json'):
                dish['options'] = json.loads(dish['options_json'])
            del dish['options_json']
        
        return dishes
    
    def get_categories(self) -> list[str]:
        '''
        获取所有分类
        Returns:
            list: 分类名称列表
        '''
        db = self.conn
        
        rows = db.fetch_all('''
            SELECT DISTINCT category FROM menu 
            WHERE is_available = 1
            ORDER BY category
        ''')
        
        return [row['category'] for row in rows]
    
    def get_menu_by_category(self) :
        '''
        获取按分类组织的菜单（用于前端展示）
        Returns:
            dict: {
                '热菜': [...],
                '凉菜': [...],
                ...
            }
        '''
        dishes = self.get_all(include_unavailable=False)
        
        menu = {}
        for dish in dishes:
            category = dish['category']
            if category not in menu:
                menu[category] = []
            
            # 转换为前端友好的格式
            menu[category].append({
                'id': dish['id'],
                'name': dish['name'],
                'price': dish['price'] / 100,  # 转成元
                'description': dish['description'],
                'image': dish['image_url'],
                'options': dish.get('options', {})
            })
        
        return menu
    
    def search(self, keyword: str) -> list[dict]:
        '''
        搜索菜品（按名称模糊搜索）
        Args:
            keyword: 关键词
        Returns:
            list: 匹配的菜品列表
        '''
        db = self.conn
        
        dishes = db.fetch_all('''
            SELECT * FROM menu 
            WHERE name LIKE ? AND is_available = 1
            ORDER BY category, id
        ''', (f'%{keyword}%',))
        
        return dishes
    
    # ==================== 批量操作 ====================
    
    def create_batch(self, dishes: list[dict]) -> list[int]:
        '''
        批量创建菜品
        Args:
            dishes: 菜品列表，每个元素是create方法的参数
        Returns:
            list: 创建的菜品ID列表
        '''
        ids = []
        for dish in dishes:
            dish_id = self.create(**dish)
            ids.append(dish_id)
        return ids
    
    def delete_batch(self, dish_ids: list[int]) -> int:
        '''
        批量删除菜品
        Args:
            dish_ids: 菜品ID列表
        Returns:
            int: 实际删除的数量
        '''
        if not dish_ids:
            return 0
        
        db = self._get_db()
        placeholders = ','.join(['?'] * len(dish_ids))
        db.execute(f'DELETE FROM menu WHERE id IN ({placeholders})', tuple(dish_ids))
        db.commit()
        
        return len(dish_ids)
    
    # ==================== 统计方法 ====================
    
    def count_by_category(self) -> list[dict]:
        '''
        统计每个分类的菜品数量
        Returns:
            list: [{'category': '热菜', 'count': 10}, ...]
        '''
        db = self.conn
        
        return db.fetch_all('''
            SELECT category, COUNT(*) as count 
            FROM menu 
            WHERE is_available = 1
            GROUP BY category
            ORDER BY category
        ''')
    
    def get_price_range(self, category: str = None) -> dict:
        '''
        获取菜品价格范围
        Args:
            category: 指定分类，None则统计所有
        Returns:
            dict: {'min': 最小价格, 'max': 最大价格, 'avg': 平均价格}
        '''
        db = self.conn
        
        if category:
            sql = 'SELECT MIN(price) as min, MAX(price) as max, AVG(price) as avg FROM menu WHERE category = ? AND is_available = 1'
            params = (category,)
        else:
            sql = 'SELECT MIN(price) as min, MAX(price) as max, AVG(price) as avg FROM menu WHERE is_available = 1'
            params = ()
        
        result = db.fetch_one(sql, params)
        if result:
            return {
                'min': result['min'] / 100,
                'max': result['max'] / 100,
                'avg': result['avg'] / 100
            }
        return {'min': 0, 'max': 0, 'avg': 0}
    
def init_test_data():
    db = get_dbconn()

    db.accounts.create("admin", "123456", True, True)
    db.accounts.create("waiter1", "w123456", False, True)
    db.accounts.create("banned1", "c123456", False, False)

    db.close()

def reset_db():
    choice = input("Are you sure you want to reset the database? (y/n) ")
    if choice.lower() != 'y':
        print("Reset database operation cancelled.")
        return
    else:
        db = get_dbconn()
        
        if os.environ.get("ENVIRONMENT") == "production":
            print("You can't reset the database in production environment.")

        db.execute("DELETE FROM menu")
        db.execute("DELETE FROM accounts")
        db.execute("DELETE FROM orders")

        db.commit()

    