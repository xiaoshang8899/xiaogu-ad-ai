-- ==========================================
-- 彤愿文化 AI 客服数据库结构
-- SQLite
-- ==========================================

PRAGMA foreign_keys = ON;

-- 客户表
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 微信相关
    openid TEXT UNIQUE,
    unionid TEXT,

    -- 客户基本信息
    nickname TEXT,
    phone TEXT,
    company_name TEXT,
    business_name TEXT,

    -- 客户来源
    source TEXT DEFAULT 'wechat',

    -- 客户意向
    intention TEXT DEFAULT 'unknown',
    intention_score INTEGER DEFAULT 0,

    -- 客服状态
    status TEXT DEFAULT 'new',
    human_takeover INTEGER DEFAULT 0,

    -- 备注
    notes TEXT,

    -- 时间
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_contact_at TEXT
);


-- 对话表
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_id INTEGER NOT NULL,

    -- 对话来源
    channel TEXT DEFAULT 'wechat',

    -- 用户消息
    user_message TEXT NOT NULL,

    -- AI回复
    ai_reply TEXT,

    -- 是否人工回复
    is_human INTEGER DEFAULT 0,

    -- 时间
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE CASCADE
);


-- 客户意向记录
CREATE TABLE IF NOT EXISTS customer_intentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_id INTEGER NOT NULL,

    intention TEXT NOT NULL,

    score INTEGER DEFAULT 0,

    reason TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE CASCADE
);


-- 系统操作日志
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    level TEXT DEFAULT 'INFO',

    event TEXT NOT NULL,

    message TEXT,

    ip_address TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 常用索引
CREATE INDEX IF NOT EXISTS idx_customers_openid
ON customers(openid);

CREATE INDEX IF NOT EXISTS idx_customers_phone
ON customers(phone);

CREATE INDEX IF NOT EXISTS idx_customers_intention
ON customers(intention);

CREATE INDEX IF NOT EXISTS idx_customers_status
ON customers(status);

CREATE INDEX IF NOT EXISTS idx_conversations_customer
ON conversations(customer_id);

CREATE INDEX IF NOT EXISTS idx_conversations_created
ON conversations(created_at);

CREATE INDEX IF NOT EXISTS idx_intentions_customer
ON customer_intentions(customer_id);


-- ==========================================
-- 社区电子屏小区资源表
-- 动态业务数据
-- ==========================================

CREATE TABLE IF NOT EXISTS communities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    area TEXT NOT NULL,
    community_name TEXT NOT NULL,

    screen_location TEXT,

    screen_status TEXT DEFAULT 'unknown',

    availability TEXT DEFAULT 'unknown',

    description TEXT,

    last_verified_at TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_communities_area
ON communities(area);


CREATE INDEX IF NOT EXISTS idx_communities_name
ON communities(community_name);


CREATE INDEX IF NOT EXISTS idx_communities_availability
ON communities(availability);


CREATE INDEX IF NOT EXISTS idx_communities_status
ON communities(screen_status);


CREATE INDEX IF NOT EXISTS idx_communities_updated
ON communities(updated_at);


-- 防止同一区域重复录入同名小区
CREATE UNIQUE INDEX IF NOT EXISTS
idx_communities_area_name
ON communities(area, community_name);
