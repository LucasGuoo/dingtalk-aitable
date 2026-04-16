# 案例：全字段创建钉钉AI表格记录

> 本案例演示如何创建包含所有字段类型的测试记录，基于测试表单(D0IyHvE)的真实API调用。

---

## 创建结果概览

| 类别 | 字段数 | 状态 |
|------|--------|------|
| 可写字段 | 22/27 | 成功创建 |
| 系统字段 | 4/4 | 自动维护 |
| **总计** | **26/31** | **成功** |

### 创建成功的字段（22个可写字段）

| 序号 | 字段名称 | 字段类型 | 状态 |
|-----|---------|---------|------|
| 1 | 标题文档字段 | primaryDoc | ✅ |
| 2 | 文本字段 | text | ✅ |
| 3 | 单选字段 | singleSelect | ✅ |
| 4 | 多选字段 | multipleSelect | ✅ |
| 5 | 日期字段 | date | ✅ |
| 6 | 数字字段 | number | ✅ |
| 7 | 货币字段 | currency | ✅ |
| 8 | 人员字段 | user | ✅ |
| 9 | 进度字段 | progress | ✅ |
| 10 | 链接字段 | url | ✅ |
| 11 | 勾选框字段 | checkbox | ✅ |
| 12 | 评分字段 | rating | ✅ |
| 13 | 电话字段 | telephone | ✅ |
| 14 | 部门字段 | department | ✅ |
| 15 | 群组字段 | group | ✅ |
| 16 | 邮箱字段 | email | ✅ |
| 17 | 行政区域字段 | address | ✅ |
| 18 | 条码字段 | barcode | ✅ |
| 19 | 富文本字段 | richText | ✅ |
| 20 | 单向关联字段 | unidirectionalLink | ✅ |
| 21 | 双向关联字段 | bidirectionalLink | ✅ |

### 系统自动维护字段（4个）

| 序号 | 字段名称 | 字段类型 | 说明 |
|-----|---------|---------|------|
| 22 | 创建人字段 | creator | 自动填充 |
| 23 | 更新人字段 | lastModifier | 自动填充 |
| 24 | 创建时间字段 | createdTime | 自动填充 |
| 25 | 最后更新时间字段 | lastModifiedTime | 自动填充 |

### 未创建的字段（6个，需特殊处理）

| 字段名称 | 字段类型 | 未创建原因 |
|---------|---------|-----------|
| 图片和附件字段 | attachment | 需先上传文件获取resourceId |
| 按钮字段 | button | 系统字段，通常只读或触发操作 |
| 流程字段 | flow | 需使用选项ID而非名称 |
| 身份证号字段 | idCard | 需符合真实身份证校验规则 |
| 手写签名字段 | attachment | 需特殊签名组件生成 |
| 地理位置字段 | geolocation | 需特定JSON格式 |

---

## 请求示例

### HTTP请求

```bash
curl -i 'https://api.dingtalk.com/v1.0/notable/bases/{base_id}/sheets/{sheet_id}/records?operatorId={operator_id}' \
  -X 'POST' \
  -H 'Content-Type: application/json' \
  -H 'x-acs-dingtalk-access-token: {access_token}' \
  -d '{
    "records": [
      {
        "fields": {
          "标题文档字段": "全字段测试记录-示例",
          "文本字段": "这是一个文本字段测试内容，用于测试文本类型",
          "单选字段": "选项1",
          "多选字段": ["多选1", "多选2"],
          "日期字段": 1772208000000,
          "数字字段": 123.45,
          "货币字段": 999.99,
          "人员字段": [{"unionId": "{operator_unionId}"}],
          "进度字段": 0.75,
          "链接字段": {"text": "测试链接文字", "link": "https://open.dingtalk.com"},
          "勾选框字段": true,
          "评分字段": 4,
          "电话字段": "13800138000",
          "部门字段": [{"deptId": "{dept_id}"}],
          "群组字段": [{"openConversationId": "cid/{conversation_id}"}],
          "邮箱字段": "test@example.com",
          "行政区域字段": "北京市海淀区",
          "条码字段": "TEST123456",
          "富文本字段": {"markdown": "# 富文本标题\n\n内容"},
          "单向关联字段": {"linkedRecordIds": ["{linked_record_id}"]},
          "双向关联字段": {"linkedRecordIds": ["{linked_record_id}"]}
        }
      }
    ]
  }'
```

### 使用Skill脚本

```bash
python3 scripts/dingtalk_api_client.py add_records \
  --base-id {base_id} \
  --sheet-name {sheet_name} \
  --operator-id {operator_id} \
  --records '[{"字段名": "值"}]'
```

---

## 各字段类型写入格式详解

### 1. 基础字段

#### 主文档字段 (primaryDoc)
```json
"标题文档字段": "全字段测试记录-示例"
```
- 格式：字符串
- 必填：是

#### 文本字段 (text)
```json
"文本字段": "这是一个文本字段测试内容"
```
- 格式：字符串

#### 富文本字段 (richText)
```json
"富文本字段": {
  "markdown": "# 富文本标题\n\n这是一个**富文本**测试内容。\n\n- 列表项1\n- 列表项2"
}
```
- 格式：对象，包含 `markdown` 字段
- 支持标准Markdown语法

### 2. 选择字段

#### 单选字段 (singleSelect)
```json
"单选字段": "选项1"
```
- 格式：选项名称字符串
- 值必须在预定义选项范围内

#### 多选字段 (multipleSelect)
```json
"多选字段": ["多选1", "多选2"]
```
- 格式：选项名称字符串数组
- 每个值必须在预定义选项范围内

#### 勾选框字段 (checkbox)
```json
"勾选框字段": true
```
- 格式：布尔值 (`true` 或 `false`)

### 3. 数值字段

#### 数字字段 (number)
```json
"数字字段": 123.45
```
- 格式：数字（整数或浮点数）

#### 货币字段 (currency)
```json
"货币字段": 999.99
```
- 格式：数字
- 自动应用货币格式（如CNY）

#### 进度字段 (progress)
```json
"进度字段": 0.75
```
- 格式：0-1之间的小数
- 显示为百分比（如75%）

#### 评分字段 (rating)
```json
"评分字段": 4
```
- 格式：整数
- 范围：根据字段配置（通常是1-5）

### 4. 日期时间字段

#### 日期字段 (date)
```json
"日期字段": 1772208000000
```
- 格式：毫秒级Unix时间戳
- 示例：1772208000000 = 2025-02-28 00:00:00 UTC

### 5. 人员组织字段

#### 人员字段 (user)
```json
"人员字段": [
  {"unionId": "{operator_unionId}"}
]
```
- 格式：对象数组，每个对象包含 `unionId`
- `multiple: true` 时支持多个

#### 部门字段 (department)
```json
"部门字段": [
  {"deptId": "{dept_id}"}
]
```
- 格式：对象数组，每个对象包含 `deptId`

#### 群组字段 (group)
```json
"群组字段": [
  {"openConversationId": "cid/{conversation_id}"}
]
```
- 格式：对象数组，每个对象包含 `openConversationId`

### 6. 联系信息字段

#### 电话字段 (telephone)
```json
"电话字段": "13800138000"
```
- 格式：字符串

#### 邮箱字段 (email)
```json
"邮箱字段": "test@example.com"
```
- 格式：字符串，需符合邮箱格式

### 7. 其他字段

#### 行政区域字段 (address)
```json
"行政区域字段": "北京市海淀区"
```
- 格式：字符串

#### 条码字段 (barcode)
```json
"条码字段": "TEST123456"
```
- 格式：字符串

#### 链接字段 (url)
```json
"链接字段": {
  "text": "测试链接文字",
  "link": "https://open.dingtalk.com"
}
```
- 格式：对象，包含 `text` 和 `link`

### 8. 关联字段

#### 单向关联字段 (unidirectionalLink)
```json
"单向关联字段": {
  "linkedRecordIds": ["{linked_record_id}"]
}
```
- 格式：对象，包含 `linkedRecordIds` 数组
- 值为目标数据表的记录ID

#### 双向关联字段 (bidirectionalLink)
```json
"双向关联字段": {
  "linkedRecordIds": ["{linked_record_id}"]
}
```
- 格式：同单向关联

---

## 成功响应示例

### 创建成功（200 OK）

```json
{
  "value": [
    {
      "id": "Ee2YoRSxMt"
    }
  ]
}
```

返回新创建记录的ID。

### 完整记录查询响应

```json
{
  "lastModifiedTime": 1772264223126,
  "createdBy": {
    "unionId": "{operator_unionId}"
  },
  "lastModifiedBy": {
    "unionId": "{operator_unionId}"
  },
  "createdTime": 1772264223126,
  "id": "Ee2YoRSxMt",
  "fields": {
    "标题文档字段": "全字段测试记录-1772264222",
    "文本字段": "这是一个文本字段测试内容，用于测试文本类型",
    "单选字段": {
      "name": "选项1",
      "id": "RlImDOkIzj"
    },
    "多选字段": [
      {"name": "多选1", "id": "UgSPN6LTtl"},
      {"name": "多选2", "id": "pukA9X1N7C"}
    ],
    "日期字段": 1772208000000,
    "数字字段": "123.45",
    "货币字段": "999.99",
    "人员字段": [
      {"unionId": "{operator_unionId}"}
    ],
    "进度字段": "0.75",
    "链接字段": {
      "link": "https://open.dingtalk.com",
      "text": "测试链接文字"
    },
    "勾选框字段": true,
    "评分字段": "4",
    "电话字段": "13800138000",
    "部门字段": [
      {"deptId": "{dept_id}"}
    ],
    "群组字段": [
      {"openConversationId": "cid/{conversation_id}"}
    ],
    "邮箱字段": "test@example.com",
    "行政区域字段": "北京市海淀区",
    "条码字段": "TEST123456",
    "富文本字段": {
      "markdown": "# 富文本标题\n\n这是一个**富文本**测试内容。\n\n- 列表项1\n- 列表项2"
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
    "最后跟新时间字段": 1772264223126
  }
}
```

---

## 特殊字段处理说明

### 1. 图片和附件字段 (attachment)

**创建方式**：
1. 先调用文件上传API获取 `resourceId`
2. 使用 `resourceId` 创建记录

```json
"图片和附件字段": [
  {"resourceId": "xxx-xxx-xxx"}
]
```

### 2. 流程字段 (flow)

**注意**：需要使用选项的 `id` 而非 `name`

```json
"流程字段": "gPzeWzEOD1"
```

### 3. 身份证号字段 (idCard)

**注意**：钉钉会进行严格的身份证格式校验（包括校验位）

### 4. 地理位置字段 (geolocation)

**推测格式**（需验证）：
```json
"地理位置字段": {
  "latitude": 39.9,
  "longitude": 116.4,
  "address": "北京市朝阳区"
}
```

---

## 常见问题与排查

### 问题1："xxx is invalid for field 'yyy'"

**原因**：字段值格式不正确

**解决**：
- 检查字段类型对应的正确格式
- 单选/多选字段使用选项名称而非ID
- 日期使用毫秒时间戳
- 人员/部门/群组使用对象数组格式

### 问题2："Missingrecords"

**原因**：请求体缺少 `records` 字段

**解决**：确保使用 `"records": [{"fields": {...}}]` 格式

### 问题3：系统字段被忽略

**原因**：`creator`, `lastModifier`, `createdTime`, `lastModifiedTime` 是系统字段

**解决**：这些字段会自动维护，创建时无需（也无法）传入

---

## 批量创建记录

支持一次创建多条记录：

```json
{
  "records": [
    {"fields": {...}},
    {"fields": {...}},
    {"fields": {...}}
  ]
}
```

---

## 最佳实践

1. **主文档字段必填**：每条记录必须包含主文档字段值
2. **选项字段校验**：单选/多选的值必须在预定义选项范围内
3. **时间戳格式**：日期字段使用毫秒级Unix时间戳
4. **人员字段**：使用 `unionId` 而非用户名称
5. **关联字段**：确保 `linkedRecordIds` 对应记录存在
6. **错误处理**：创建失败时检查具体字段错误信息

---

*案例生成时间: 2025-02-28*
*记录ID: Ee2YoRSxMt*
*测试表单: D0IyHvE*
