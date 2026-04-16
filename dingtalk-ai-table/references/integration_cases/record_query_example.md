# 案例：查询钉钉AI表格记录

> 本案例基于测试表单(D0IyHvE)的真实API返回数据，已进行脱敏处理。
> 用于参考API返回格式和各字段类型的数据结构。

---

## 请求示例

### HTTP请求

```bash
curl -i 'https://api.dingtalk.com/v1.0/notable/bases/{base_id}/sheets/{sheet_id}/records/list?operatorId={operator_id}' \
  -X 'POST' \
  -H 'Content-Type: application/json' \
  -H 'x-acs-dingtalk-access-token: {access_token}' \
  -d '{
    "maxResults": 3
  }'
```

### 使用Skill脚本

```bash
python3 scripts/dingtalk_api_client.py list_records \
  --base-id {base_id} \
  --sheet-name {sheet_name} \
  --operator-id {operator_id} \
  --max-results 5
```

---

## 响应示例

### 成功响应（200 OK）

```json
{
  "records": [
    {
      "lastModifiedTime": 1772257575000,
      "createdBy": {
        "unionId": "{operator_unionId}"
      },
      "lastModifiedBy": {
        "unionId": "{operator_unionId}"
      },
      "createdTime": 1772247376000,
      "id": "byxMG0uBm8",
      "fields": {
        "富文本字段": {
          "markdown": "# **测试**\n\n* 测试哈哈\n"
        },
        "多选字段": [
          {"name": "多选1", "id": "UgSPN6LTtl"},
          {"name": "多选2", "id": "pukA9X1N7C"}
        ],
        "更新人字段": {
          "unionId": "{operator_unionId}"
        },
        "最后跟新时间字段": 1772257575000,
        "评星字段": "3",
        "创建时间字段": 1772247376000,
        "人员字段": [
          {"unionId": "{operator_unionId}"}
        ],
        "标题文档字段": "测试文档",
        "勾选框字段": true,
        "数字字段": "110",
        "单选字段": {
          "name": "选项1",
          "id": "RlImDOkIzj"
        },
        "链接字段": {
          "link": "https://example.com/document",
          "text": "测试链接"
        },
        "邮箱字段": "example@example.com",
        "部门字段": [
          {"deptId": "{dept_id}"}
        ],
        "电话字段": "15911110000",
        "货币字段": "110",
        "图片和附件字段": [
          {
            "resourceId": "509072d8-xxxx-xxxx-xxxx-29548a6fe928",
            "filename": "CRM测试用例.xlsx",
            "size": 11641,
            "resourceUrl": "/core/api/resources/{resource_id}/detail",
            "type": "xls",
            "url": "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/{path}"
          },
          {
            "resourceId": "2df13dd2-xxxx-xxxx-xxxx-87617a899096",
            "filename": "Vibe Coding之道.docx",
            "size": 51413,
            "type": "doc"
          },
          {
            "resourceId": "0d2e0f7f-xxxx-xxxx-xxxx-3faf5f3c0c95",
            "filename": "信息系统安全.pdf",
            "size": 3732207,
            "type": "pdf"
          },
          {
            "isLink": true,
            "filename": "无标题文档(1)",
            "type": "adoc",
            "url": "https://alidocs.dingtalk.com/i/nodes/xxxxxx"
          },
          {
            "resourceId": "8a06308d-xxxx-xxxx-xxxx-f754b39d7092",
            "filename": "发票1.png",
            "size": 153922,
            "type": "image"
          }
        ],
        "条码字段": "88888",
        "群组字段": [
          {"openConversationId": "cid/{conversation_id}"}
        ],
        "双向关联字段": {
          "linkedRecordIds": ["{linked_record_id}"]
        },
        "文本字段": "测试文本",
        "日期字段": 1772208000000,
        "进度字段": "0.26",
        "创建人字段": {
          "unionId": "{operator_unionId}"
        },
        "单向关联字段": {
          "linkedRecordIds": ["{linked_record_id}"]
        }
      }
    },
    {
      "lastModifiedTime": 1772261683000,
      "createdBy": {
        "unionId": "{operator_unionId}"
      },
      "lastModifiedBy": {
        "unionId": "{operator_unionId}"
      },
      "createdTime": 1772261673000,
      "id": "lPEBMQ2rRt",
      "fields": {
        "标题文档字段": "ceshi",
        "更新人字段": {
          "unionId": "{operator_unionId}"
        },
        "最后跟新时间字段": 1772261683000,
        "创建人字段": {
          "unionId": "{operator_unionId}"
        },
        "创建时间字段": 1772261673000
      }
    }
  ],
  "nextToken": "",
  "hasMore": false
}
```

---

## 字段类型数据结构详解

### 1. 基础字段

#### 主文档字段 (primaryDoc)
```json
"标题文档字段": "测试文档"
```

#### 文本字段 (text)
```json
"文本字段": "测试文本"
```

#### 富文本字段 (richText)
```json
"富文本字段": {
  "markdown": "# **标题**\n\n* 列表项\n"
}
```

### 2. 选择字段

#### 单选字段 (singleSelect)
```json
"单选字段": {
  "name": "选项1",
  "id": "RlImDOkIzj"
}
```

#### 多选字段 (multipleSelect)
```json
"多选字段": [
  {"name": "多选1", "id": "UgSPN6LTtl"},
  {"name": "多选2", "id": "pukA9X1N7C"}
]
```

#### 勾选框字段 (checkbox)
```json
"勾选框字段": true
```

### 3. 数值字段

#### 数字字段 (number)
```json
"数字字段": "110"
```

#### 货币字段 (currency)
```json
"货币字段": "110"
```

#### 进度字段 (progress)
```json
"进度字段": "0.26"
```

#### 评星字段 (rating)
```json
"评星字段": "3"
```

### 4. 日期时间字段

#### 日期字段 (date)
```json
"日期字段": 1772208000000
```
- 时间戳格式：毫秒级Unix时间戳

#### 创建时间字段 (createdTime)
```json
"创建时间字段": 1772247376000
```
- 系统字段，自动维护

#### 最后更新时间字段 (lastModifiedTime)
```json
"最后跟新时间字段": 1772257575000
```
- 系统字段，自动维护

### 5. 人员组织字段

#### 人员字段 (user)
```json
"人员字段": [
  {"unionId": "{operator_unionId}"}
]
```
- `multiple: true` 时返回数组

#### 部门字段 (department)
```json
"部门字段": [
  {"deptId": "{dept_id}"}
]
```

#### 群组字段 (group)
```json
"群组字段": [
  {"openConversationId": "cid/{conversation_id}"}
]
```

#### 创建人字段 (creator)
```json
"创建人字段": {
  "unionId": "{operator_unionId}"
}
```
- 系统字段，只读

#### 更新人字段 (lastModifier)
```json
"更新人字段": {
  "unionId": "{operator_unionId}"
}
```
- 系统字段，只读

### 6. 联系信息字段

#### 电话字段 (telephone)
```json
"电话字段": "15911110000"
```

#### 邮箱字段 (email)
```json
"邮箱字段": "example@example.com"
```

### 7. 媒体附件字段

#### 附件字段 (attachment)
```json
"图片和附件字段": [
  {
    "resourceId": "uuid-string",
    "filename": "文件名.xlsx",
    "size": 11641,
    "resourceUrl": "/core/api/resources/{id}/detail",
    "type": "xls",
    "url": "https://oss-url"
  },
  {
    "resourceId": "uuid-string",
    "filename": "图片.png",
    "size": 153922,
    "type": "image"
  },
  {
    "isLink": true,
    "filename": "在线文档",
    "type": "adoc",
    "url": "https://alidocs.dingtalk.com/..."
  }
]
```
- `type` 可选值：`xls`, `doc`, `pdf`, `image`, `adoc`等
- `isLink: true` 表示在线文档链接

### 8. 关联字段

#### 单向关联字段 (unidirectionalLink)
```json
"单向关联字段": {
  "linkedRecordIds": ["7Gtfo83ZWU"]
}
```

#### 双向关联字段 (bidirectionalLink)
```json
"双向关联字段": {
  "linkedRecordIds": ["7Gtfo83ZWU"]
}
```

### 9. 其他字段

#### 链接字段 (url)
```json
"链接字段": {
  "link": "https://example.com",
  "text": "链接文字"
}
```

#### 条码字段 (barcode)
```json
"条码字段": "88888"
```

---

## 系统字段说明

以下字段由系统自动维护，API调用时**不可写入**：

| 字段 | 位置 | 说明 |
|------|------|------|
| `id` | 根级 | 记录唯一标识 |
| `createdTime` | 根级 | 创建时间（毫秒时间戳） |
| `lastModifiedTime` | 根级 | 最后更新时间（毫秒时间戳） |
| `createdBy` | 根级 | 创建人信息 `{unionId: xxx}` |
| `lastModifiedBy` | 根级 | 最后更新人信息 `{unionId: xxx}` |
| `创建人字段` | fields内 | 创建人（系统字段） |
| `更新人字段` | fields内 | 更新人（系统字段） |
| `创建时间字段` | fields内 | 创建时间（系统字段） |
| `最后跟新时间字段` | fields内 | 更新时间（系统字段） |

---

## 分页说明

当数据量较大时，响应会包含分页信息：

```json
{
  "records": [...],
  "nextToken": "xxx",      // 下一页token，空字符串表示没有更多数据
  "hasMore": true/false    // 是否还有更多数据
}
```

### 分页请求

```bash
curl -i 'https://api.dingtalk.com/v1.0/notable/bases/{base_id}/sheets/{sheet_id}/records/list?operatorId={operator_id}' \
  -X 'POST' \
  -H 'Content-Type: application/json' \
  -H 'x-acs-dingtalk-access-token: {access_token}' \
  -d '{
    "maxResults": 100,
    "nextToken": "xxx"    // 上一页返回的nextToken
  }'
```

---

## 注意事项

1. **时间戳格式**：所有时间字段均为毫秒级Unix时间戳
2. **系统字段**：`createdTime`, `lastModifiedTime`, `createdBy`, `lastModifiedBy` 由系统自动维护
3. **人员字段**：返回的是 `unionId`，不是用户名称
4. **附件URL**：有有效期限制，建议及时使用
5. **空值处理**：未填写的字段可能不返回或返回空值

---

*案例生成时间: 2025-02-28*
*数据来源: 测试表单(D0IyHvE)*
