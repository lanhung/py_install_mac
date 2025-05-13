import pymysql
import random
from datetime import datetime

# 数据库连接配置（请替换为你自己的）
db_config = {
    "host": "192.168.0.147",
    "user": "root",
    "password": "123456",
    "database": "xiaozhi_esp32_server",
    "charset": "utf8mb4"
}

# MAC 地址文件路径
mac_file = "mac_addresses.txt"

# 初始化
connection = None
cursor = None

try:
    # 连接数据库
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    # 读取 MAC 地址
    with open(mac_file, "r") as f:
        mac_list = [line.strip() for line in f if line.strip()]

    print(f"📥 读取到 {len(mac_list)} 个 MAC 地址")

    # 查询所有 user_id 和 agent_id
    cursor.execute("SELECT id, user_id FROM ai_agent")
    agents = cursor.fetchall()
    if not agents:
        raise Exception("❌ ai_agent 表中没有数据，无法插入设备")

    print(f"🔍 获取到 {len(agents)} 个 agent")

    # 当前时间
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 插入数据
    insert_sql = """
                 INSERT INTO ai_device (
                     id, user_id, mac_address, last_connected_at,
                     auto_update, board, alias, agent_id,
                     app_version, sort, creator, create_date,
                     updater, update_date
                 ) VALUES (
                              %s, %s, %s, %s,
                              %s, %s, %s, %s,
                              %s, %s, %s, %s,
                              %s, %s
                          ) \
                 """

    values = []
    for mac in mac_list:
        agent_id, user_id = random.choice(agents)
        values.append((
            mac, user_id, mac, now,
            0, 'bread-compact-wifi', None, agent_id,
            '1.5.9', 0, user_id, now,
            user_id, now
        ))

    cursor.executemany(insert_sql, values)
    connection.commit()

    print(f"✅ 成功插入 {len(values)} 条设备记录到 ai_device 表")

except Exception as e:
    print("❌ 出错：", e)

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
