# 案例：全字段修改钉钉AI表格记录

> 本案例演示如何修改记录的所有字段，基于测试表单(D0IyHvE)的真实API调用。
> 记录ID: `Ee2YoRSxMt`

---

## 修改结果概览

| 类别 | 字段数 | 状态 |
|------|--------|------|
| 可修改字段 | 16/22 | 成功更新 |
| 系统字段 | 2/4 | 自动更新 |
| **总计更新** | **18** | **成功** |

### 成功更新的字段（16个）

| 序号 | 字段名称 | 字段类型 | 原值 | 更新后 | 状态 |
|-----|---------|---------|------|--------|------|
| 1 | 标题文档字段 | primaryDoc | 全字段测试记录-xxx | 全字段修改测试-已更新 | ✅ |
| 2 | 文本字段 | text | 这是一个文本字段测试内容... | 这是修改后的文本内容... | ✅ |
| 3 | 单选字段 | singleSelect | 选项1 | 选项2 | ✅ |
| 4 | 多选字段 | multipleSelect | [多选1, 多选2] | [多选2] | ✅ |
| 5 | 日期字段 | date | 2025-02-28 | 2025-03-01 | ✅ |
| 6 | 数字字段 | number | 123.45 | 999.99 | ✅ |
| 7 | 货币字段 | currency | 999.99 | 5000.00 | ✅ |
| 8 | 进度字段 | progress | 75% | 95% | ✅ |
| 9 | 链接字段 | url | 原链接 | 修改后的链接 | ✅ |
| 10 | 勾选框字段 | checkbox | true | false | ✅ |
| 11 | 评分字段 | rating | 4星 | 5星 | ✅ |
| 12 | 电话字段 | telephone | 13800138000 | 13900139000 | ✅ |
| 13 | 邮箱字段 | email | test@example.com | updated@example.com | ✅ |
| 14 | 行政区域字段 | address | 北京市海淀区 | 上海市浦东新区 | ✅ |
| 15 | 条码字段 | barcode | TEST123456 | UPDATED456 | ✅ |
| 16 | 富文本字段 | richText | 原内容 | 修改后的富文本 | ✅ |

### 系统字段变化（2个自动更新）

| 字段 | 变化说明 |
|------|---------|
| lastModifiedTime | 从 1772264223126 更新为 1772265230156 |
| lastModifiedBy | 保持当前操作用户 |

### 未修改字段（6个）

| 字段名称 | 原因 |
|---------|------|
| 人员字段 | 保持原值（人员未变） |
| 部门字段 | 保持原值（部门未变） |
| 群组字段 | 保持原值（群组未变） |
| 单向关联字段 | 保持原值（关联未变） |
| 双向关联字段 | 保持原值（关联未变） |
| 创建人/创建时间 | 系统字段，不可修改 |

---

## 请求示例

### HTTP请求

```bash
curl -i 'https://api.dingtalk.com/v1.0/notable/bases/{base_id}/sheets/{sheet_id}/records?operatorId={operator_id}' \
  -X 'PUT' \
  -H 'Content-Type: application/json' \
  -H 'x-acs-dingtalk-access-token: {access_token}' \
  -d '{
    "records": [
      {
        "id": "Ee2YoRSxMt",
        "fields": {
          "标题文档字段": "全字段修改测试-已更新",
          "文本字段": "这是修改后的文本内容，用于测试更新功能",
          "单选字段": "选项2",
          "多选字段": ["多选2"],
          "日期字段": 1772294400000,
          "数字字段": 999.99,
          "货币字段": 5000.00,
          "进度字段": 0.95,
          "链接字段": {"text": "修改后的链接", "link": "https://www.dingtalk.com"},
          "勾选框字段": false,
          "评分字段": 5,
          "电话字段": "13900139000",
          "邮箱字段": "updated@example.com",
          "行政区域字段": "上海市浦东新区",
          "条码字段": "UPDATED456",
          "富文本字段": {"markdown": "# 修改后的富文本\n\n这是**更新后**的内容。\n\n1. 有序列表1\n2. 有序列表2"}
        }
      }
    ]
  }'
```

### 关键说明

- **HTTP方法**: `PUT`（不是POST或PATCH）
- **URL**: `/v1.0/notable/bases/{baseId}/sheets/{sheetId}/records?operatorId={operatorId}`
- **请求体**: 包含 `records` 数组，每个记录必须有 `id` 和 `fields`

---

## 成功响应

```json
{
  "value": [
    {
      "id": "Ee2YoRSxMt"
    }
  ]
}
```

返回被更新记录的ID列表。

---

## 更新后的完整记录

```json
{
  "lastModifiedTime": 1772265230156,
  "createdBy": {
    "unionId": "{operator_unionId}"
  },
  "lastModifiedBy": {
    "unionId": "{operator_unionId}"
  },
  "createdTime": 1772264223126,
  "id": "Ee2YoRSxMt",
  "fields": {
    "标题文档字段": "全字段修改测试-已更新",
    "文本字段": "这是修改后的文本内容，用于测试更新功能",
    "单选字段": {
      "name": "选项2",
      "id": "XsGMYc13PG"
    },
    "多选字段": [
      {"name": "多选2", "id": "pukA9X1N7C"}
    ],
    "日期字段": 1772294400000,
    "数字字段": "999.99",
    "货币字段": "5000",
    "人员字段": [
      {"unionId": "{operator_unionId}"}
    ],
    "进度字段": "0.95",
    "链接字段": {
      "link": "https://www.dingtalk.com",
      "text": "修改后的链接"
    },
    "勾选框字段": false,
    "评分字段": "5",
    "电话字段": "13900139000",
    "部门字段": [
      {"deptId": "{dept_id}"}
    ],
    "群组字段": [
      {"openConversationId": "cid/{conversation_id}"}
    ],
    "邮箱字段": "updated@example.com",
    "行政区域字段": "上海市浦东新区",
    "条码字段": "UPDATED456",
    "富文本字段": {
      "markdown": "# 修改后的富文本\n\n这是**更新后**的内容。\n\n1. 有序列表1\n2. 有序列表2"
    },
    "单向关联字段": {
      "linkedRecordIds": ["7Gtfo83ZWU"]
    },
    "双向关联字段": {
      "linkedRecordIds": ["7Gtfo83ZWU"]
    },
    "创建人字段": {
      "unionId": "{operator_unionId}"
    },
    "更新人字段": {
      "unionId": "{operator_unionId}"
    },
    "创建时间字段": 1772264223126,
    "最后跟新时间字段": 1772265230156
  }
}
```

---

## 各字段类型更新格式

### 1. 基础字段

#### 主文档字段 (primaryDoc)
```json
"标题文档字段": "新的标题内容"
```

#### 文本字段 (text)
```json
"文本字段": "新的文本内容"
```

#### 富文本字段 (richText)
```json
"富文本字段": {
  "markdown": "# 新标题\n\n**加粗内容**"
}
```

### 2. 选择字段

#### 单选字段 (singleSelect)
```json
"单选字段": "选项2"
```
- 使用选项名称（不是ID）

#### 多选字段 (multipleSelect)
```json
"多选字段": ["多选2"]
```
- 使用选项名称数组

#### 勾选框字段 (checkbox)
```json
"勾选框字段": false
```
- 布尔值：`true` 或 `false`

### 3. 数值字段

#### 数字字段 (number)
```json
"数字字段": 999.99
```

#### 货币字段 (currency)
```json
"货币字段": 5000.00
```

#### 进度字段 (progress)
```json
"进度字段": 0.95
```
- 范围：0-1之间的小数

#### 评分字段 (rating)
```json
"评分字段": 5
```
- 整数，根据字段配置的范围

### 4. 日期时间字段

#### 日期字段 (date)
```json
"日期字段": 1772294400000
```
- 毫秒级Unix时间戳

### 5. 联系信息字段

#### 电话字段 (telephone)
```json
"电话字段": "13900139000"
```

#### 邮箱字段 (email)
```json
"邮箱字段": "updated@example.com"
```

#### 行政区域字段 (address)
```json
"行政区域字段": "上海市浦东新区"
```

### 6. 其他字段

#### 条码字段 (barcode)
```json
"条码字段": "UPDATED456"
```

#### 链接字段 (url)
```json
"链接字段": {
  "text": "链接文字",
  "link": "https://www.dingtalk.com"
}
```

---

## 批量更新记录

支持一次更新多条记录：

```bash
curl -i 'https://api.dingtalk.com/v1.0/notable/bases/{base_id}/sheets/{sheet_id}/records?operatorId={operator_id}' \
  -X 'PUT' \
  -H 'Content-Type: application/json' \
  -H 'x-acs-dingtalk-access-token: {access_token}' \
  -d '{
    "records": [
      {
        "id": "记录ID1",
        "fields": {
          "字段1": "新值1",
          "字段2": "新值2"
        }
      },
      {
        "id": "记录ID2",
        "fields": {
          "字段1": "新值1",
          "字段2": "新值2"
        }
      }
    ]
  }'
```

---

## 注意事项

### 1. 不可修改的字段

以下字段**不支持**通过API修改：

| 字段 | 说明 |
|------|------|
| 创建人字段 (creator) | 系统字段，自动维护 |
| 更新人字段 (lastModifier) | 系统自动更新为当前用户 |
| 创建时间字段 (createdTime) | 系统字段，不可修改 |
| 最后更新时间字段 (lastModifiedTime) | 系统自动更新 |

### 2. 部分字段暂不支持更新

根据钉钉官方文档，以下字段类型**暂不支持**更新：

- 人员字段 (user)
- 部门字段 (department)
- 群组字段 (group)
- 附件字段 (attachment)
- 流程字段 (flow)
- 地理位置字段 (geolocation)
- 身份证字段 (idCard)

### 3. 更新限制

- 主文档字段（primaryDoc）可以更新
- 单选/多选字段使用**选项名称**而非ID
- 日期字段使用时间戳（毫秒）
- 更新后系统会自动更新 `lastModifiedTime` 和 `lastModifiedBy`

---

## 常见问题

### Q1: 更新返回成功，但字段值未改变？

**可能原因**：
- 该字段类型暂不支持更新（如人员、附件等）
- 字段值格式不正确

**排查方法**：
```bash
# 更新后立即查询验证
curl -s 'https://api.dingtalk.com/v1.0/notable/bases/{base_id}/sheets/{sheet_id}/records/{record_id}?operatorId={operator_id}' \
  -H 'x-acs-dingtalk-access-token: {token}'
```

### Q2: 如何批量更新多条记录？

在 `records` 数组中添加多个记录对象：

```json
{
  "records": [
    {"id": "id1", "fields": {...}},
    {"id": "id2", "fields": {...}},
    {"id": "id3", "fields": {...}}
  ]
}
```

### Q3: 更新时如何清空字段值？

对于支持清空的字段，传入 `null` 或空值：

```json
"文本字段": null
"多选字段": []
```

---

## 最佳实践

1. **先查询后更新**：更新前先获取记录当前值，避免误改
2. **增量更新**：只更新需要修改的字段，减少数据传输
3. **批量更新**：多条记录更新时使用批量接口，提高效率
4. **错误处理**：更新后查询验证，确保数据正确
5. **字段白名单**：只更新业务需要的字段，避免修改系统字段

---

## 与创建记录的对比

| 对比项 | 创建记录 | 更新记录 |
|--------|---------|---------|
| HTTP方法 | POST | PUT |
| 请求体 | `{"records": [{"fields": {...}}]}` | `{"records": [{"id": "xxx", "fields": {...}}]}` |
| 必须字段 | fields | id + fields |
| 返回 | 新记录ID列表 | 更新记录ID列表 |
| 系统字段 | 自动填充 | lastModifiedTime/By 自动更新 |

---

*案例生成时间: 2025-02-28*
*记录ID: Ee2YoRSxMt*
*测试表单: D0IyHvE*
