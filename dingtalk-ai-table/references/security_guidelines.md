# 钉钉AI表格API安全使用指南

> 本文档说明如何安全地使用钉钉AI表格API，保护敏感信息不被泄露。

---

## 一、敏感信息分类

### 1.1 高敏感信息（必须加密存储）

| 信息类型 | 说明 | 存储方式 |
|---------|------|---------|
| `app_key` / `Client ID` | 应用唯一标识 | 消费者变量（加密） |
| `app_secret` / `Client Secret` | 应用密钥 | 消费者变量（加密） |
| `access_token` | API访问令牌 | 内存缓存，禁止持久化 |

### 1.2 中敏感信息（需要脱敏处理）

| 信息类型 | 说明 | 处理方式 |
|---------|------|---------|
| `unionId` | 用户唯一标识 | 案例中使用 `{operator_unionId}` 占位符 |
| `deptId` | 部门ID | 案例中使用 `{dept_id}` 占位符 |
| `openConversationId` | 群组ID | 案例中使用 `{conversation_id}` 占位符 |
| `baseId` | AI表格ID | 案例中使用 `{base_id}` 占位符 |
| `sheetId` | 数据表ID | 案例中使用 `{sheet_id}` 占位符 |
| `recordId` | 记录ID | 案例中使用 `{record_id}` 占位符 |

---

## 二、安全使用实践

### 2.1 凭证配置

**正确做法** ✅
```bash
# 配置为消费者变量（自动加密）
DINGTALK_APP_KEY=your_client_id
DINGTALK_APP_SECRET=your_client_secret
```

**错误做法** ❌
```bash
# 禁止硬编码凭证
curl -H "x-acs-dingtalk-access-token: e9161828xxxx"  # 泄露风险
```

### 2.2 API调用示例（安全版本）

```bash
# 使用占位符替代真实ID
curl -i 'https://api.dingtalk.com/v1.0/notable/bases/{base_id}/sheets/{sheet_id}/records/list?operatorId={operator_id}' \
  -X 'POST' \
  -H 'Content-Type: application/json' \
  -H 'x-acs-dingtalk-access-token: {access_token}' \
  -d '{
    "maxResults": 3
  }'
```

运行时由系统自动替换：
- `{base_id}` → 用户提供的真实baseId
- `{sheet_id}` → 用户提供的真实sheetId
- `{operator_id}` → 用户提供的真实unionId
- `{access_token}` → 动态获取的access_token

### 2.3 脚本调用（安全版本）

```bash
# 使用环境变量传入凭证
python3 scripts/dingtalk_api_client.py list_records \
  --base-id "$BASE_ID" \
  --sheet-name "$SHEET_NAME" \
  --operator-id "$OPERATOR_ID"
```

---

## 三、案例文档中的占位符说明

所有案例文档使用以下占位符替代真实值：

| 占位符 | 代表含义 | 示例值格式 |
|-------|---------|-----------|
| `{base_id}` | AI表格ID | `XPwkYGxZV3jQMgZQUvzd0mLeWAgozOKL` |
| `{sheet_id}` | 数据表ID | `D0IyHvE` |
| `{sheet_name}` | 数据表名称 | `测试` |
| `{record_id}` | 记录ID | `Ee2YoRSxMt` |
| `{operator_id}` / `{operator_unionId}` | 操作人unionId | `gvS5hafRgqmJAEiSPLL18HgiEiE` |
| `{dept_id}` | 部门ID | `1043947145` |
| `{conversation_id}` | 群组会话ID | `Q2AaQsB7dKB31XiaWhW` |
| `{linked_record_id}` | 关联记录ID | `7Gtfo83ZWU` |
| `{access_token}` | 访问令牌 | `e9161828637f322e91332bdc2caabdb9` |
| `{app_key}` | 应用Key | `dingxxxxxx` |
| `{app_secret}` | 应用密钥 | `xxxxxxxx` |

**注意**：所有示例中的ID均为占位符，实际使用时需替换为用户的真实值。

---

## 四、敏感信息泄露风险点

### 4.1 常见风险

1. **URL参数泄露**
   ```
   # 风险：access_token可能被记录到服务器日志
   GET /api?access_token=xxx
   ```

2. **代码提交泄露**
   ```python
   # 风险：凭证随代码一起提交到版本控制
   ACCESS_TOKEN = "e9161828xxxx"
   ```

3. **日志输出泄露**
   ```python
   # 风险：敏感信息被记录到日志文件
   print(f"Request: {request_body}")  # 可能包含敏感字段
   ```

### 4.2 防范措施

1. **使用Header传递凭证**
   ```
   x-acs-dingtalk-access-token: {access_token}
   ```

2. **环境变量管理凭证**
   ```python
   import os
   app_key = os.getenv("DINGTALK_APP_KEY")
   ```

3. **日志脱敏**
   ```python
   # 输出前移除敏感字段
   safe_log = {k: v for k, v in data.items() if k not in ["unionId", "access_token"]}
   ```

---

## 五、应急响应

### 5.1 凭证泄露处理

如果发现凭证泄露：

1. **立即重置凭证**
   - 登录钉钉开发者后台
   - 进入应用详情 → 凭证与基础信息
   - 重置 `app_secret`

2. **吊销Access Token**
   - 联系钉钉技术支持
   - 提供泄露的token，请求吊销

3. **更新配置**
   - 更新消费者变量中的凭证
   - 检查近期异常调用日志

### 5.2 数据泄露处理

如果发现敏感数据泄露：

1. **评估影响范围**
   - 确认泄露的数据类型和数量
   - 评估对企业的影响

2. **限制访问**
   - 调整应用可见范围
   - 限制敏感数据表的API权限

3. **通知相关方**
   - 通知企业安全团队
   - 按企业安全流程处理

---

## 六、合规建议

1. **最小权限原则**
   - 只申请必需的API权限
   - 定期审查权限使用情况

2. **数据分类分级**
   - 识别敏感数据字段
   - 对敏感数据进行加密或脱敏

3. **审计日志**
   - 记录API调用日志
   - 定期审查异常访问

4. **安全培训**
   - 对使用人员进行安全意识培训
   - 明确安全责任

---

*本文档为安全使用指南，与Skill功能文档配合使用。*
