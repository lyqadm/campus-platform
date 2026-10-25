import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI(title="智慧校园闲置交易与综合互助平台")
DB_FILE = "campus.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 30 条新增演示商品（覆盖数码电子/图书教材/代步工具/生活百货/文体乐器/运动健身/美妆个护/服饰鞋包）
NEW_ITEMS = [
    ("Kindle Paperwhite 4 电子书阅读器", "数码电子", 350.0, "九成新", "张三(学生)", "在售", "考研上岸退坑，屏幕无划痕，送磁吸保护套和数据线"),
    ("罗技 K380 多设备蓝牙键盘", "数码电子", 85.0, "九五新", "李四(学生)", "在售", "可同时连手机平板电脑三台设备，粉白配色，附电池"),
    ("小米手环 8 NFC 版", "数码电子", 129.0, "九成新", "王五(学生)", "在售", "刷食堂饭卡超方便，续航两周，附两条替换表带"),
    ("绿联 Type-C 六合一拓展坞", "数码电子", 69.0, "九成新", "张三(学生)", "在售", "课设答辩连投影神器，HDMI+千兆网口+三个USB"),
    ("富士 instax mini12 拍立得", "数码电子", 420.0, "九成新", "李四(学生)", "待审核", "社团招新用过两次，附相纸十张和奶茶色相机包"),
    ("倍思 65W 氮化镓充电头", "数码电子", 45.0, "九五新", "王五(学生)", "在售", "笔记本手机都能快充，宿舍限电也带得动"),
    ("高等数学同济版上下册+习题全解指南", "图书教材", 28.0, "八成新", "王五(学生)", "在售", "重点已用荧光笔标好，期末周救急必备"),
    ("大学英语四级真题逐句精解（含听力码）", "图书教材", 18.0, "七成新", "张三(学生)", "在售", "已过级退坑，前五套已写完，附赠答题卡"),
    ("数据结构（C语言版）严蔚敏教材", "图书教材", 20.0, "八成新", "李四(学生)", "在售", "考研408打基础，各章笔记夹在书里一起送"),
    ("计算机二级 MS Office 高级应用题库", "图书教材", 12.0, "九成新", "王五(学生)", "在售", "软件激活码没用完，考前刷两周稳过"),
    ("C Primer Plus 第6版 + 明解C语言合售", "图书教材", 45.0, "八成新", "张三(学生)", "在售", "编程入门两件套，无笔记无划线"),
    ("九号电动滑板车 F2 Pro", "代步工具", 1399.0, "八成新", "张三(学生)", "在售", "东区到西区通勤神器，续航40km，送车锁和头盔"),
    ("凤凰26寸复古通勤自行车", "代步工具", 150.0, "七成新", "王五(学生)", "在售", "大四毕业急出，链条刚上过油，自带车筐"),
    ("迪卡侬 RC100 公路自行车", "代步工具", 1100.0, "九成新", "李四(学生)", "待审核", "只骑了一个学期，变速顺滑，附打气筒和尾灯"),
    ("小米平衡车 Plus 蓝牙版", "代步工具", 750.0, "八成新", "张三(学生)", "已售出", "操场遛弯用，电池健康，原装充电器齐全"),
    ("宜家床上折叠电脑桌", "生活百货", 40.0, "八成新", "王五(学生)", "在售", "床上写代码追剧神器，桌腿可折叠不占空间"),
    ("富光保温杯 500ml", "生活百货", 25.0, "全新未拆", "张三(学生)", "在售", "社团发的奖品重复了，保温12小时"),
    ("手持挂烫机迷你便携款", "生活百货", 55.0, "八成新", "李四(学生)", "在售", "面试前熨衬衫用过几次，水箱大好收纳"),
    ("宿舍遮光床帘 1.2米+全套支架", "生活百货", 35.0, "八成新", "王五(学生)", "在售", "装上秒变单人小世界，遮光率90%"),
    ("小熊宿舍电煮锅 1.2L", "生活百货", 65.0, "九成新", "张三(学生)", "已售出", "煮面煮小火锅全能，功率小不限电"),
    ("USB静音夹式小风扇", "生活百货", 22.0, "八成新", "李四(学生)", "在售", "夹床头夹书桌都行，三档风速几乎听不见"),
    ("雅马哈 F600 民谣吉他", "文体乐器", 480.0, "九成新", "李四(学生)", "在售", "琴颈无变形，附琴包、变调夹和三本教程"),
    ("卡马 B1 面单吉他", "文体乐器", 260.0, "八成新", "王五(学生)", "在售", "新手练了半年已换新弦，音色在线"),
    ("61键电子琴初学套装", "文体乐器", 180.0, "八成新", "张三(学生)", "待审核", "音乐选修课结课出，带琴架，可插耳机静音练"),
    ("斯伯丁7号PU篮球", "运动健身", 110.0, "八成新", "王五(学生)", "在售", "室外场打过一学期，气足不起皮"),
    ("尤尼克斯羽毛球拍双拍套装", "运动健身", 150.0, "九成新", "李四(学生)", "在售", "附球一筒和双拍包，约球神器"),
    ("可调节哑铃 20kg 一对", "运动健身", 130.0, "八成新", "张三(学生)", "在售", "宿舍撸铁必备，包胶设计不吵楼下"),
    ("完美日记眼影盘+化妆刷套装", "美妆个护", 60.0, "九成新", "李四(学生)", "在售", "囤重复了，眼影只用过两次，刷具全新"),
    ("飞利浦电动牙刷 HX3216", "美妆个护", 89.0, "九成新", "王五(学生)", "在售", "双十一囤多了，全新未拆仅开封外盒"),
    ("北面情侣款冲锋衣 M码", "服饰鞋包", 320.0, "九成新", "张三(学生)", "在售", "买大了一码，防水透气，可小刀"),
]

# 演示留言（通过商品标题定位 id，新旧库通用；只随种子/迁移写入一次）
DEMO_COMMENTS = [
    ("罗技 G Pro 无线鼠标", "张三(学生)", "楼主，打瓦灵敏度跟手吗？", "10-23"),
    ("罗技 G Pro 无线鼠标", "李四(学生)", "自用很跟手，可北苑食堂当面验货", "10-23"),
    ("2027考研英语黄皮书全套", "张三(学生)", "学长能再便宜5块吗？", "10-24"),
    ("iPad Air 5 64G 蓝色 + Apple Pencil", "王五(学生)", "电池健康度有截图吗？想周末面交", "10-24"),
    ("Kindle Paperwhite 4 电子书阅读器", "李四(学生)", "晚上熄灯后背光刺眼吗？", "10-24"),
    ("迪卡侬 RC100 公路自行车", "王五(学生)", "我178骑合适吗？变速是几个速别？", "10-24"),
    ("斯伯丁7号PU篮球", "张三(学生)", "周末约球！这个球室外场耐磨吗", "10-24"),
    ("尤尼克斯羽毛球拍双拍套装", "李四(学生)", "球拍断过线吗？求实拍图", "10-24"),
    ("捷安特山地变速自行车", "张三(学生)", "车子还在吗？想周末去看车", "10-23"),
    ("小米护眼宿舍充电台灯", "张三(学生)", "熄灯后能亮多久呀？", "10-23"),
    ("小米护眼宿舍充电台灯", "王五(学生)", "实测六小时没问题，放心", "10-24"),
    ("高等数学同济版上下册+习题全解指南", "李四(学生)", "重点笔记能拍照看看吗", "10-23"),
    ("雅马哈 F310 民谣木吉他", "张三(学生)", "新人入门够用吗？求实话", "10-24"),
    ("漫步者头戴式降噪蓝牙耳机", "王五(学生)", "图书馆戴真的隔音吗", "10-23"),
    ("小米手环 8 NFC 版", "李四(学生)", "续航真能两周？", "10-24"),
    ("九号电动滑板车 F2 Pro", "王五(学生)", "可以先试骑一圈再决定吗", "10-24"),
    ("宜家床上折叠电脑桌", "李四(学生)", "可以送到楼下自提点吗", "10-24"),
]

def init_db():
    conn = get_db()
    c = conn.cursor()
    # 1. 创建用户表、商品表、订单表、失物招领表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, role TEXT, dept TEXT, balance REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, category TEXT, price REAL, condition TEXT,
        seller TEXT, status TEXT, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER, item_title TEXT, buyer TEXT, seller TEXT,
        price REAL, order_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS lost_found (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kind TEXT, title TEXT, location TEXT, contact TEXT, pub_date TEXT, publisher TEXT DEFAULT '')''')

    # 1.5 旧库迁移：失物招领表补充发布人字段（用于"本人只能删除自己发布的信息"）
    cols = [r[1] for r in c.execute("PRAGMA table_info(lost_found)").fetchall()]
    if "publisher" not in cols:
        c.execute("ALTER TABLE lost_found ADD COLUMN publisher TEXT DEFAULT ''")
        for title, publisher in [
            ("丢失深蓝色校园一卡通（学号尾号0821）", "张三(学生)"),
            ("捡到 AirPods Pro 耳机充电仓一个", "李四(学生)"),
            ("遗失黑色天堂雨伞及《离散数学》教材", "王五(学生)"),
        ]:
            c.execute("UPDATE lost_found SET publisher=? WHERE title=? AND (publisher IS NULL OR publisher='')",
                      (publisher, title))

    # 1.6 旧库迁移：修正历史订单的 item_id 指向
    #     原种子订单引用了不存在的商品 id（与新商品 id 冲突后会误伤上架/下架/删除的锁定判断），
    #     商品标题对不上的订单统一改为 item_id=0，仅作交易历史展示
    c.execute("""UPDATE orders SET item_id = 0
                 WHERE item_id != 0
                   AND item_title != COALESCE((SELECT title FROM items WHERE items.id = orders.item_id), '')""")
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER, commenter TEXT, content TEXT, comment_date TEXT)''')

    # 2. 如果数据库是空的，自动塞入逼真的初始演示数据
    need_demo_comments = False
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ("张三(学生)", "student", "计算机学院", 1500.0),
            ("李四(学生)", "student", "外国语学院", 860.0),
            ("王五(学生)", "student", "机械工程学院", 420.0),
            ("Admin(管理员)", "admin", "校团委信息中心", 9999.0)
        ]
        c.executemany("INSERT INTO users (username, role, dept, balance) VALUES (?,?,?,?)", users)

        items = [
            ("罗技 G Pro 无线鼠标", "数码电子", 260.0, "九成新", "李四(学生)", "在售", "宿舍自用半年，箱说全，无双击，送鼠标垫"),
            ("2027考研英语黄皮书全套", "图书教材", 35.0, "全新未拆", "王五(学生)", "在售", "买重了，一页没写，北苑食堂当面交易"),
            ("捷安特山地变速自行车", "代步工具", 450.0, "八成新", "李四(学生)", "在售", "大四毕业挥泪甩卖，刹车灵敏，送车锁"),
            ("小米护眼宿舍充电台灯", "生活百货", 29.9, "九五新", "王五(学生)", "在售", "三档调光，断电续航6小时，毕业带不走"),
            ("iPad Air 5 64G 蓝色 + Apple Pencil", "数码电子", 2100.0, "九五新", "李四(学生)", "在售", "平时只用来记高数笔记，电池健康度94%"),
            ("《软件工程导论（第6版）》课本", "图书教材", 15.0, "八成新", "王五(学生)", "在售", "内有期末重点勾画，学弟学妹考前突击必备"),
            ("雅马哈 F310 民谣木吉他", "文体乐器", 380.0, "九成新", "李四(学生)", "待审核", "社团演出用过两次，附送琴包、变调夹和拨片"),
            ("漫步者头戴式降噪蓝牙耳机", "数码电子", 120.0, "九成新", "张三(学生)", "已售出", "图书馆自习神器，耳罩刚换新")
        ]
        c.executemany("INSERT INTO items (title, category, price, condition, seller, status, description) VALUES (?,?,?,?,?,?,?)",
                      items + NEW_ITEMS)

        orders = [
            (8, "漫步者头戴式降噪蓝牙耳机", "李四(学生)", "张三(学生)", 120.0, "10-18"),
            (0, "高等数学同济第七版上下册", "张三(学生)", "王五(学生)", 25.0, "10-19"),
            (0, "寝室多功能折叠桌", "王五(学生)", "李四(学生)", 30.0, "10-20"),
            (0, "Casio 科学计算器", "张三(学生)", "李四(学生)", 45.0, "10-21"),
            (0, "尤克里里23寸小吉他", "李四(学生)", "王五(学生)", 110.0, "10-22"),
            (0, "机械键盘红轴87键", "张三(学生)", "王五(学生)", 160.0, "10-23"),
            (0, "索尼便携蓝牙音箱", "王五(学生)", "张三(学生)", 220.0, "10-24")
        ]
        c.executemany("INSERT INTO orders (item_id, item_title, buyer, seller, price, order_date) VALUES (?,?,?,?,?,?)", orders)

        lost_items = [
            ("寻物启事", "丢失深蓝色校园一卡通（学号尾号0821）", "第三教学楼 204 阶梯教室", "138****5521", "2026-10-23", "张三(学生)"),
            ("失物招领", "捡到 AirPods Pro 耳机充电仓一个", "第一食堂二楼麻辣烫窗口", "放于食堂一楼失物招领处", "2026-10-24", "李四(学生)"),
            ("寻物启事", "遗失黑色天堂雨伞及《离散数学》教材", "图书馆四楼自习区靠窗", "微信：campus_zhang", "2026-10-24", "王五(学生)"),
        ]
        c.executemany("INSERT INTO lost_found (kind, title, location, contact, pub_date, publisher) VALUES (?,?,?,?,?,?)", lost_items)
        need_demo_comments = True
    elif c.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 8:
        # 3. 兼容旧版演示库：商品表还是原来的 8 条种子数据时，追加 30 条新演示商品
        #    （用户已自行发布过商品则不动，避免污染数据）
        c.executemany("INSERT INTO items (title, category, price, condition, seller, status, description) VALUES (?,?,?,?,?,?,?)", NEW_ITEMS)
        need_demo_comments = True

    # 4. 给部分商品塞几条逼真的演示留言（只随种子/迁移写入一次，防止重复）
    if need_demo_comments:
        for title, commenter, content, cdate in DEMO_COMMENTS:
            row = c.execute("SELECT id FROM items WHERE title=?", (title,)).fetchone()
            if row:
                c.execute("INSERT INTO comments (item_id, commenter, content, comment_date) VALUES (?,?,?,?)",
                          (row[0], commenter, content, cdate))
    conn.commit()
    conn.close()

init_db()

# 数据请求模型
class PublishItemReq(BaseModel):
    title: str
    category: str
    price: float
    condition: str
    seller: str
    description: str

class BuyItemReq(BaseModel):
    item_id: int
    buyer: str

class LostFoundReq(BaseModel):
    kind: str
    title: str
    location: str
    contact: str
    publisher: str = ""

class RechargeReq(BaseModel):
    username: str
    amount: float

class CommentReq(BaseModel):
    item_id: int
    commenter: str
    content: str

@app.get("/api/init_info")
def get_all_info(username: str = "张三(学生)"):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    items = [dict(r) for r in conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()]
    comment_counts = {r["item_id"]: r["n"] for r in conn.execute(
        "SELECT item_id, COUNT(*) AS n FROM comments GROUP BY item_id").fetchall()}
    for it in items:
        it["comment_count"] = comment_counts.get(it["id"], 0)
    orders = [dict(r) for r in conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()]
    lost_found = [dict(r) for r in conn.execute("SELECT * FROM lost_found ORDER BY id DESC").fetchall()]
    
    # 统计图表数据（在售商品分类占比 + 近7天交易额）——只统计"在售"，上下架后扇形图实时变化
    cat_stats = [dict(r) for r in conn.execute("SELECT category as name, COUNT(*) as value FROM items WHERE status='在售' GROUP BY category").fetchall()]
    day_stats = [dict(r) for r in conn.execute("SELECT order_date, SUM(price) as total FROM orders GROUP BY order_date ORDER BY order_date").fetchall()]
    conn.close()
    return {
        "user": dict(user) if user else {},
        "items": items,
        "orders": orders,
        "lost_found": lost_found,
        "charts": {"categories": cat_stats, "daily_sales": day_stats}
    }

@app.post("/api/items")
def publish_item(req: PublishItemReq):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="商品名称不能为空")
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="商品描述不能为空")
    if req.price < 0:
        raise HTTPException(status_code=400, detail="价格不能为负数")
    conn = get_db()
    conn.execute(
        "INSERT INTO items (title, category, price, condition, seller, status, description) VALUES (?,?,?,?,?,?,?)",
        (req.title, req.category, req.price, req.condition, req.seller, "在售", req.description)
    )
    conn.commit()
    conn.close()
    return {"msg": "发布成功"}

@app.post("/api/buy")
def buy_item(req: BuyItemReq):
    conn = get_db()
    item = conn.execute("SELECT * FROM items WHERE id=?", (req.item_id,)).fetchone()
    buyer = conn.execute("SELECT * FROM users WHERE username=?", (req.buyer,)).fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=400, detail="商品不存在")
    if item["status"] != "在售":
        conn.close()
        raise HTTPException(status_code=400, detail="商品已售出或未上架")
    if not buyer:
        conn.close()
        raise HTTPException(status_code=404, detail="买家账户不存在")
    if item["seller"] == req.buyer:
        conn.close()
        raise HTTPException(status_code=400, detail="不能购买自己发布的商品")
    if buyer["balance"] < item["price"]:
        conn.close()
        raise HTTPException(status_code=400, detail="账户余额不足，请先充值")
    
    # 扣减买家余额、增加卖家余额、更新商品状态、写入订单
    conn.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (item["price"], req.buyer))
    conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (item["price"], item["seller"]))
    conn.execute("UPDATE items SET status = '已售出' WHERE id = ?", (req.item_id,))
    conn.execute("INSERT INTO orders (item_id, item_title, buyer, seller, price, order_date) VALUES (?,?,?,?,?,?)",
                 (item["id"], item["title"], req.buyer, item["seller"], item["price"], "10-24"))
    conn.commit()
    conn.close()
    return {"msg": "购买成功！订单已生成"}

@app.post("/api/recharge")
def recharge(req: RechargeReq):
    """用户余额充值"""
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于0")
    conn = get_db()
    if not conn.execute("SELECT id FROM users WHERE username=?", (req.username,)).fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="用户不存在")
    conn.execute("UPDATE users SET balance = balance + ? WHERE username=?", (req.amount, req.username))
    conn.commit()
    new_balance = conn.execute("SELECT balance FROM users WHERE username=?", (req.username,)).fetchone()["balance"]
    conn.close()
    return {"msg": f"充值成功！到账 {req.amount} 元", "balance": new_balance}

@app.get("/api/comments/{item_id}")
def get_comments(item_id: int):
    """查看某商品的留言评论列表（按时间倒序）"""
    conn = get_db()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM comments WHERE item_id=? ORDER BY id DESC", (item_id,)).fetchall()]
    conn.close()
    return {"comments": rows}

@app.post("/api/comments")
def add_comment(req: CommentReq):
    """给商品发布留言评论"""
    content = req.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="留言内容不能为空")
    conn = get_db()
    if not conn.execute("SELECT id FROM items WHERE id=?", (req.item_id,)).fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="商品不存在")
    conn.execute("INSERT INTO comments (item_id, commenter, content, comment_date) VALUES (?,?,?,?)",
                 (req.item_id, req.commenter, content, "10-24"))
    conn.commit()
    conn.close()
    return {"msg": "留言成功"}

@app.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: int, username: str):
    """删除留言：本人可删自己的留言，管理员可删除任何留言"""
    conn = get_db()
    row = conn.execute("SELECT * FROM comments WHERE id=?", (comment_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="留言不存在")
    user = conn.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
    is_admin = user and user["role"] == "admin"
    if row["commenter"] != username and not is_admin:
        conn.close()
        raise HTTPException(status_code=403, detail="只能删除自己发布的留言")
    conn.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()
    return {"msg": "删除成功"}

@app.post("/api/audit/{item_id}")
def audit_item(item_id: int, status: str, username: str):
    """管理员审核：仅管理员角色可执行，学生调用返回 403"""
    conn = get_db()
    user = conn.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
    if not user or user["role"] != "admin":
        conn.close()
        raise HTTPException(status_code=403, detail="仅管理员可执行审核操作")
    if not conn.execute("SELECT id FROM items WHERE id=?", (item_id,)).fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="商品不存在")
    cur = conn.execute("SELECT status FROM items WHERE id=?", (item_id,)).fetchone()
    has_order = conn.execute("SELECT id FROM orders WHERE item_id=?", (item_id,)).fetchone()
    # 有过交易记录（或当前已售出）的商品禁止一切状态变更（上架/下架），防止二次销售和数据不一致
    if cur["status"] == "已售出" or has_order:
        conn.close()
        raise HTTPException(status_code=400, detail="该商品已存在交易记录，不可上架或下架")
    conn.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
    conn.commit()
    conn.close()
    return {"msg": "状态已更新"}

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, username: str):
    """删除商品：卖家可删自己发布的（已售出除外），管理员可删任何；连带删除留言（历史订单保留）"""
    conn = get_db()
    item = conn.execute("SELECT seller, status FROM items WHERE id=?", (item_id,)).fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="商品不存在")
    user = conn.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
    is_admin = user and user["role"] == "admin"
    if item["seller"] != username and not is_admin:
        conn.close()
        raise HTTPException(status_code=403, detail="只能删除自己发布的商品")
    has_order = conn.execute("SELECT id FROM orders WHERE item_id=?", (item_id,)).fetchone()
    if not is_admin and (item["status"] == "已售出" or has_order):
        conn.close()
        raise HTTPException(status_code=403, detail="该商品已产生交易记录，不可删除")
    conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.execute("DELETE FROM comments WHERE item_id=?", (item_id,))
    conn.commit()
    conn.close()
    return {"msg": "删除成功"}

@app.post("/api/lost_found")
def add_lost_found(req: LostFoundReq):
    """发布寻物启事/失物招领（所有字段必填）"""
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="物品描述不能为空")
    if not req.location.strip():
        raise HTTPException(status_code=400, detail="地点不能为空")
    if not req.contact.strip():
        raise HTTPException(status_code=400, detail="联系方式不能为空")
    conn = get_db()
    conn.execute("INSERT INTO lost_found (kind, title, location, contact, pub_date, publisher) VALUES (?,?,?,?,?,?)",
                 (req.kind, req.title, req.location, req.contact, "2026-10-24", req.publisher))
    conn.commit()
    conn.close()
    return {"msg": "发布成功"}

@app.delete("/api/lost_found/{item_id}")
def delete_lost_found(item_id: int, username: str):
    """删除失物招领信息：本人可删自己发布的，管理员可删除任何"""
    conn = get_db()
    row = conn.execute("SELECT * FROM lost_found WHERE id=?", (item_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="信息不存在")
    user = conn.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
    is_admin = user and user["role"] == "admin"
    if row["publisher"] != username and not is_admin:
        conn.close()
        raise HTTPException(status_code=403, detail="只能删除自己发布的信息")
    conn.execute("DELETE FROM lost_found WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return {"msg": "删除成功"}

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)