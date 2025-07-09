-- 删除已存在的表，如果需要的话（仅用于开发/测试环境，生产环境需谨慎）
DROP TABLE IF EXISTS app_user;
DROP SEQUENCE IF EXISTS app_user_id_seq;

-- 创建 app_user 表
CREATE TABLE app_user
(
    email             VARCHAR                     NOT NULL,
    hashed_password   VARCHAR                     NOT NULL,
    status            VARCHAR(20),
    id                INTEGER                     NOT NULL, -- 将 serial 改为 INTEGER，手动创建序列并指定默认值
    created_at        TIMESTAMP                   DEFAULT NOW() NOT NULL,
    updated_at        TIMESTAMP WITH TIME ZONE    DEFAULT NOW() NOT NULL,
    is_active         BOOLEAN,
    points            INTEGER,
    nickname          VARCHAR(255),
    avatar            VARCHAR(255),
    PRIMARY KEY (id) -- 明确指定主键
);

-- 添加列注释
COMMENT ON COLUMN app_user.id IS '主键ID';
COMMENT ON COLUMN app_user.updated_at IS '更新时间';
COMMENT ON COLUMN app_user.points IS '积分,用于面试支付时长';
COMMENT ON COLUMN app_user.nickname IS '昵称';
COMMENT ON COLUMN app_user.avatar IS '头像';

-- 设置表所有者
ALTER TABLE app_user OWNER TO root;

-- 创建序列并设置起始值为 100000
CREATE SEQUENCE app_user_id_seq
    START WITH 100000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 将 id 列的默认值设置为序列的下一个值
ALTER TABLE app_user ALTER COLUMN id SET DEFAULT nextval('app_user_id_seq');

-- 创建唯一索引
CREATE UNIQUE INDEX ix_app_user_email
    ON app_user (email);

-- 创建普通索引
CREATE INDEX ix_app_user_id
    ON app_user (id);

-- 插入一些测试数据（可选）
INSERT INTO app_user (email, hashed_password, status, is_active, points, nickname) VALUES

INSERT INTO product (sku_id, name, price, duration_seconds, description, status, created_at, updated_at) VALUES
  ('SINGLE_001', '单场面试', 5900, 2700, '基础流程（出题、评分、简评），极简报告（分数+3条建议），无附加服务，记录仅存7天。', 1, NOW(), NOW()),
  ('MONTHLY_001', '月度会员', 19900, 27000, '完整功能（简历抽取、岗位定制题、多维度评分、反馈拆解），标准版报告（分数、分项分析、10条建议），每月限10场，赠1次简历优化，专属客服12小时响应。', 1, NOW(), NOW()),
  ('LIFETIME_001', '终身会员', 79900, 237600, '全功能（自定义模板、深度岗位匹配、多轮归因、行业对标），深度报告（分数、行业对比、20条建议、成长轨迹），不限场次，每月1次人工顾问1v1，优先体验新功能，老带新各返现50元。', 1, NOW(), NOW());
