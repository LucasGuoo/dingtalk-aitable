# 钉钉AI表格字段类型说明

## 概述

本文档详细说明钉钉AI表格支持的字段类型、属性配置以及数据格式。

---

## 支持的字段类型

| 字段类型 | type值 | 说明 |
|---------|--------|------|
| 主文档 | primaryDoc | 数据表的主字段，每表必须有且只有一个 |
| 文本 | text | 单行或多行文本 |
| 富文本 | richText | 支持格式的富文本内容 |
| 数字 | number | 支持多种格式的数值 |
| 单选 | singleSelect | 从预定义选项中选择一项 |
| 多选 | multipleSelect | 从预定义选项中选择多项 |
| 日期 | date | 日期和时间 |
| 创建时间 | createdTime | 系统字段，记录创建时间 |
| 人员 | user | 选择企业成员 |
| 部门 | department | 选择企业部门 |
| 附件 | attachment | 文件附件 |
| 单向关联 | unidirectionalLink | 关联其他数据表的记录 |
| 双向关联 | bidirectionalLink | 双向关联其他数据表 |

---

## 各字段类型详细说明

### 1. 主文档 (primaryDoc)

数据表的主字段，每个数据表必须有且只有一个主字段。

- **特点**：
  - 系统自动创建，不可删除
  - 通常作为记录的标题或主要标识
  - 支持文本输入
- **属性配置** (`property`): 无
- **新增/更新时格式**: 字符串
  ```json
  "标题": "这是标题内容"
  ```
- **返回格式**: 字符串
  ```json
  "标题": "这是标题内容"
  ```

### 2. 文本 (text)

纯文本字段，支持单行或多行文本输入。

- **属性配置** (`property`): 无
- **新增/更新时格式**: 字符串
  ```json
  "字段名": "文本内容"
  ```
- **返回格式**: 字符串
  ```json
  "字段名": "文本内容"
  ```

### 3. 富文本 (richText)

支持格式的富文本内容字段。

- **特点**：支持文本格式化（加粗、斜体、链接等）
- **属性配置** (`property`): 无
- **新增/更新时格式**: HTML格式字符串
  ```json
  "简讯内容": "<p>这是<b>富文本</b>内容</p>"
  ```
- **返回格式**: HTML格式字符串
  ```json
  "简讯内容": "<p>这是<b>富文本</b>内容</p>"
  ```

### 4. 数字 (number)

数值字段，支持多种显示格式。

- **属性配置** (`property`):
  ```json
  {
    "formatter": "INT"
  }
  ```
  - `formatter` 可选值:
    - `INT`: 整数
    - `FLOAT_1`: 保留1位小数
    - `FLOAT_2`: 保留2位小数
    - `FLOAT_3`: 保留3位小数
    - `FLOAT_4`: 保留4位小数
    - `THOUSAND`: 千分位
    - `THOUSAND_FLOAT`: 千分位（小数点）
    - `PRESENT`: 百分比
    - `PRESENT_FLOAT`: 百分比（小数点）
    - `CNY`: 人民币
    - `CNY_FLOAT`: 人民币（小数点）
    - `HKD`: 港元
    - `HKD_FLOAT`: 港元（小数点）
    - `USD`: 美元
    - `USD_FLOAT`: 美元（小数点）
    - `EUR`: 欧元
    - `EUR_FLOAT`: 欧元（小数点）
    - `JPY`: 日元
    - `JPY_FLOAT`: 日元（小数点）

- **新增/更新时格式**: 数字或字符串
  ```json
  "字段名": 123
  ```

- **返回格式**: 字符串
  ```json
  "字段名": "123"
  ```

### 3. 单选 (singleSelect)

从预定义选项中选择一项。

- **属性配置** (`property`):
  ```json
  {
    "choices": [
      {"name": "选项1"},
      {"name": "选项2"},
      {"name": "选项3"}
    ]
  }
  ```

- **新增/更新时格式**: 选项名称字符串
  ```json
  "字段名": "选项1"
  ```

- **返回格式**: 包含id和name的对象
  ```json
  "字段名": {
    "id": "optxxx",
    "name": "选项1"
  }
  ```

### 4. 多选 (multipleSelect)

从预定义选项中选择多项。

- **属性配置** (`property`): 同单选

- **新增/更新时格式**: 选项名称字符串数组
  ```json
  "字段名": ["选项1", "选项2"]
  ```

- **返回格式**: 包含id和name的对象数组
  ```json
  "字段名": [
    {"id": "optxxx", "name": "选项1"},
    {"id": "optyyy", "name": "选项2"}
  ]
  ```

### 5. 日期 (date)

日期和时间字段。

- **属性配置** (`property`):
  ```json
  {
    "formatter": "YYYY-MM-DD"
  }
  ```
  - `formatter` 可选值:
    - `YYYY-MM-DD`: 2023-12-31
    - `YYYY-MM-DD HH:mm`: 2023-12-31 09:00
    - `YYYY/MM/DD`: 2023/12/31
    - `YYYY/MM/DD HH:mm`: 2023/12/31 09:00

- **新增/更新时格式**: 时间戳(毫秒)或ISO 8601字符串
  ```json
  "字段名": 1704067200000
  ```
  或
  ```json
  "字段名": "2024-01-01T00:00:00.000Z"
  ```

- **返回格式**: 时间戳(毫秒)
  ```json
  "字段名": 1704067200000
  ```

### 6. 创建时间 (createdTime)

系统字段，自动记录记录的创建时间。

- **特点**：
  - 系统自动维护，不可手动修改
  - 只读字段，API不支持写入
- **属性配置** (`property`):
  ```json
  {
    "formatter": "YYYY-MM-DD"
  }
  ```
  - `formatter` 可选值:
    - `YYYY-MM-DD`: 2023-12-31
    - `YYYY-MM-DD HH:mm`: 2023-12-31 09:00
- **新增/更新时格式**: 不支持（系统自动生成）
- **返回格式**: 时间戳(毫秒)
  ```json
  "创建时间": 1704067200000
  ```

### 7. 人员 (user)

选择企业成员。

- **属性配置** (`property`):
  ```json
  {
    "multiple": true
  }
  ```
  - `multiple`: 是否支持多选，默认true

- **新增/更新时格式**: 包含unionId的对象数组
  ```json
  "字段名": [
    {"unionId": "用户unionId1"},
    {"unionId": "用户unionId2"}
  ]
  ```

- **返回格式**: 包含unionId的对象数组
  ```json
  "字段名": [
    {"unionId": "用户unionId1"},
    {"unionId": "用户unionId2"}
  ]
  ```

### 7. 部门 (department)

选择企业部门。

- **属性配置** (`property`):
  ```json
  {
    "multiple": true
  }
  ```
  - `multiple`: 是否支持多选，默认true

- **新增/更新时格式**: 包含deptId的对象数组
  ```json
  "字段名": [
    {"deptId": "部门ID1"},
    {"deptId": "部门ID2"}
  ]
  ```

- **返回格式**: 包含deptId的对象数组
  ```json
  "字段名": [
    {"deptId": "部门ID1"},
    {"deptId": "部门ID2"}
  ]
  ```

### 8. 附件 (attachment)

文件附件字段。

- **属性配置** (`property`): 无

- **新增/更新时格式**: 先调用上传附件接口，使用返回的url
  ```json
  "字段名": [
    {
      "filename": "example.xlsx",
      "size": 92250,
      "type": "xls",
      "url": "https://xxx"
    }
  ]
  ```

- **返回格式**: 同输入格式
  ```json
  "字段名": [
    {
      "filename": "example.xlsx",
      "size": 92250,
      "type": "xls",
      "url": "https://xxx"
    }
  ]
  ```

- **说明**: 
  - 在线文档的url没有访问时效
  - 其他文件的url有访问时效

### 9. 单向关联 (unidirectionalLink)

关联其他数据表的记录。

- **属性配置** (`property`):
  ```json
  {
    "multiple": true,
    "targetSheetId": "目标数据表ID"
  }
  ```
  - `multiple`: 是否支持多选
  - `targetSheetId`: 目标数据表ID

- **新增/更新时格式**: 包含recordId的对象数组
  ```json
  "字段名": [
    {"recordId": "recxxx"},
    {"recordId": "recyyy"}
  ]
  ```

- **返回格式**: 包含recordId的对象数组
  ```json
  "字段名": [
    {"recordId": "recxxx"},
    {"recordId": "recyyy"}
  ]
  ```

### 10. 双向关联 (bidirectionalLink)

双向关联其他数据表的记录。

- **属性配置** (`property`): 类似单向关联

- **新增/更新时格式**: 同单向关联

- **返回格式**: 同单向关联

---

## 完整示例

### 创建带多种字段类型的数据表

```json
{
  "name": "示例数据表",
  "fields": [
    {
      "name": "任务名称",
      "type": "text"
    },
    {
      "name": "优先级",
      "type": "singleSelect",
      "property": {
        "choices": [
          {"name": "高"},
          {"name": "中"},
          {"name": "低"}
        ]
      }
    },
    {
      "name": "负责人",
      "type": "user",
      "property": {
        "multiple": false
      }
    },
    {
      "name": "截止日期",
      "type": "date",
      "property": {
        "formatter": "YYYY-MM-DD"
      }
    },
    {
      "name": "进度",
      "type": "number",
      "property": {
        "formatter": "PRESENT"
      }
    },
    {
      "name": "附件",
      "type": "attachment"
    }
  ]
}
```

### 新增记录示例

```json
{
  "records": [
    {
      "fields": {
        "任务名称": "完成API对接",
        "优先级": "高",
        "负责人": [{"unionId": "用户unionId"}],
        "截止日期": 1704067200000,
        "进度": 0.5,
        "附件": [
          {
            "filename": "需求文档.pdf",
            "size": 102400,
            "type": "pdf",
            "url": "https://xxx"
          }
        ]
      }
    }
  ]
}
```

---

## 注意事项

1. **主字段限制**: 数据表的第一列是"主字段"，仅支持特定字段类型，且不可删除
2. **类型匹配**: 新增/更新记录时，字段值格式必须与字段类型严格匹配
3. **只读字段**: 部分字段类型（如公式、自动编号）不支持通过API更新
4. **关联字段**: 使用关联字段时，确保目标记录存在且有权访问
5. **批量限制**: 新增/更新记录有批量限制，单次建议不超过100条


---

## 测试表单字段结构示例

以下表格基于实际测试表单(D0IyHvE)生成，展示了钉钉AI表格支持的所有字段类型：

| 序号 | 字段名称 | 字段类型 | 字段ID | 说明 |
|-----|---------|---------|-------|------|
| 1 | 标题文档字段 | primaryDoc | 3gnDKrl | 主文档字段 |
| 2 | 文本字段 | text | uAv5w23 | 单行/多行文本 |
| 3 | 单选字段 | singleSelect | M8kRy8s | 选项:选项1/选项2 |
| 4 | 多选字段 | multipleSelect | T0PyWYv | 选项:多选1/多选2 |
| 5 | 日期字段 | date | 7mZpFj8 | 格式:YYYY-MM-DD |
| 6 | 数字字段 | number | AUhUUFn | 格式:FLOAT_2 |
| 7 | 货币字段 | currency | cp4aYxc | CNY, FLOAT_2 |
| 8 | 人员字段 | user | hty8jR8 | 多选:是 |
| 9 | 图片和附件字段 | attachment | TDYeDEo | 文件附件 |
| 10 | 进度字段 | progress | 3hFuOlq | PERCENT, 0-1 |
| 11 | 链接字段 | url | Ej1Br1D | URL链接 |
| 12 | 按钮字段 | button | 7dhRbVD | 按钮操作 |
| 13 | 流程字段 | flow | RmpLs7f | 多阶段流程 |
| 14 | 勾选框字段 | checkbox | jlZRFoX | 布尔勾选 |
| 15 | 评星字段 | rating | ep3wJW2 | 1-5星评分 |
| 16 | 电话字段 | telephone | FJdh4l3 | 电话号码 |
| 17 | 部门字段 | department | l625j6Q | 多选:是 |
| 18 | 群组字段 | group | ZcZg8xv | 多选:是 |
| 19 | 邮箱字段 | email | PqJldEU | 邮箱地址 |
| 20 | 行政区域字段 | address | G8tpGWY | 地址信息 |
| 21 | 条码字段 | barcode | gh95ouN | 条码/二维码 |
| 22 | 身份证号字段 | idCard | VQHv7pV | 身份证 |
| 23 | 手写签名字段 | attachment | 4u5gRtt | 签名附件 |
| 24 | 地理位置字段 | geolocation | ew4kuKC | 定位信息 |
| 25 | 富文本字段 | richText | QGgdm0j | 富文本内容 |
| 26 | 单向关联字段 | unidirectionalLink | RqNt9Sf | 关联:hERWDMS |
| 27 | 双向关联字段 | bidirectionalLink | RzIWrTN | 关联:hERWDMS |
| 28 | 创建人字段 | creator | lCtIdKt | 系统字段(只读) |
| 29 | 更新人字段 | lastModifier | FNKKUjL | 系统字段(只读) |
| 30 | 创建时间字段 | createdTime | n7lgxvx | 系统字段(只读) |
| 31 | 最后跟新时间字段 | lastModifiedTime | YLCUpsN | 系统字段(只读) |

### 系统字段说明

以下字段由系统自动维护，**不支持通过API写入**：

| 字段类型 | 说明 |
|---------|------|
| creator | 创建人 |
| lastModifier | 更新人 |
| createdTime | 创建时间 |
| lastModifiedTime | 最后更新时间 |

---

*字段参考基于测试表单生成于 2025-02-28*
