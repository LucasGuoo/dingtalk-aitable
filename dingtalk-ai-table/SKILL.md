---
name: dingtalk-ai-table
description: 调用钉钉AI表格OpenAPI实现增删改查对接，支持Excel智能导入；当用户需要对接钉钉AI表格、实现数据同步、批量导入Excel数据或系统集成时使用
dependency:
  python:
    - pandas>=2.0.0
    - openpyxl>=3.1.0
    - tqdm>=4.65.0
    - requests>=2.31.0
  system: []
---

# 钉钉AI表格OpenAPI对接集成

## 任务目标

本Skill用于帮助用户完成钉钉AI表格的OpenAPI对接集成，实现数据的增删改查操作。

**适用场景：**
- 企业内部系统与钉钉AI表格的数据同步
- 自动化数据录入和更新流程
- 批量数据处理和管理
- Excel数据智能导入
- 系统集成中的表格数据对接

---

## 前置准备

### 步骤1：确认企业应用配置

钉钉AI表格API仅支持**企业内部应用**方式调用。

**首次使用需完成：**
1. 登录 [钉钉开发者后台](https://open.dingtalk.com/)
2. 进入「应用开发」→「企业内部应用」
3. 创建应用并记录 **Client ID** 和 **Client Secret**

### 步骤2：申请API权限

在应用详情页的「权限管理」中，添加以下权限：

**必需权限：**
- ✅ `AI表格应用读权限`
- ✅ `AI表格应用写权限`

**可选权限**（如需自动获取operatorId）：
- ✅ `成员信息读权限`（精简模式即可）
- ✅ `搜索企业通讯录权限`

### 步骤3：配置凭证（三种方式，任选其一）

**⚠️ 重要：使用本Skill时需要提供钉钉应用凭证。**

**方式1 - 命令行参数（推荐，最灵活，无需配置）**

每次调用命令时直接传入凭证：

```bash
python scripts/dingtalk_api_client.py show_fields \
  --app-key "你的Client ID" \
  --app-secret "你的Client Secret" \
  --base-id {base_id} \
  --sheet-name {sheet_name} \
  --operator-id {operator_id}
```

**方式2 - 消费者变量（配置一次，多次使用）**

在对话中配置（仅需一次）：

```
配置消费者变量 DINGTALK_APP_KEY=你的Client ID
配置消费者变量 DINGTALK_APP_SECRET=你的Client Secret
```

配置后可直接使用，无需每次传入凭证参数。

**方式3 - JSON格式环境变量**

```bash
export COZE_DINGTALK_AI_TABLE_7611716228092264482='{"app_key": "你的Client ID", "app_secret": "你的Client Secret"}'
```

---

## 消费者变量（可选）

| 变量名 | 说明 | 必填 | 获取方式 |
|-------|------|------|---------|
| `DINGTALK_APP_KEY` | 钉钉应用的Client ID | 否（可用参数代替） | 钉钉开发者后台 |
| `DINGTALK_APP_SECRET` | 钉钉应用的Client Secret | 否（可用参数代替） | 钉钉开发者后台 |
| `DINGTALK_OPERATOR_ID` | 操作人的unionId | 否 | 钉钉后台获取或自动查询 |

配置完成后，可以通过以下命令验证：

```bash
python scripts/dingtalk_api_client.py show_fields --base-id {你的baseId} --sheet-name {表名} --operator-id {operatorId}
```

---

## 核心概念

### 数据结构层级

```
Base (AI表格) → Sheet (数据表) → Field (字段) → Record (记录)
   {base_id}        {sheet_id}       {field_id}      {record_id}
```

### 关键参数

| 参数 | 说明 | 示例 |
|------|------|------|
| baseId | AI表格唯一标识 | 从表格URL获取 |
| sheetId | 数据表ID | 从表格URL获取 |
| fieldId | 字段ID | 通过API获取 |
| recordId | 记录ID | 通过API获取 |
| operatorId | 操作人unionId | 从钉钉后台获取 |

---

## 使用指南

**关于凭证参数：** 以下示例假设你已配置消费者变量。如果未配置，请在每个命令中添加 `--app-key "你的Client ID" --app-secret "你的Client Secret"`。

### 1. 获取数据表字段

```bash
python scripts/dingtalk_api_client.py show_fields \
  --base-id {base_id} \
  --sheet-name {sheet_name} \
  --operator-id {operator_id}
```

### 2. 获取operatorId（自动）

```bash
python scripts/dingtalk_api_client.py get_operator_id \
  --user-name "张三"
```

### 3. 查询记录

```bash
python scripts/dingtalk_api_client.py list_records \
  --base-id {base_id} \
  --sheet-name {sheet_name} \
  --operator-id {operator_id} \
  --max-results 10
```

### 4. 新增记录

```bash
python scripts/dingtalk_api_client.py add_records \
  --base-id {base_id} \
  --sheet-name {sheet_name} \
  --operator-id {operator_id} \
  --records '[{"标题": "测试", "金额": 100}]'
```

### 5. Excel智能导入

```bash
python scripts/smart_import.py \
  --base-id {base_id} \
  --sheet-name {sheet_name} \
  --operator-id {operator_id} \
  --excel-file ./data.xlsx
```

---

## 字段类型格式

### 基础字段

```json
// 主文档字段 (primaryDoc)
"标题": "文本内容"

// 文本字段 (text)
"描述": "文本内容"

// 数字字段 (number)
"金额": 123.45

// 日期字段 (date) - 毫秒时间戳
"日期": 1772208000000
```

### 选择字段

```json
// 单选字段 (singleSelect) - 使用选项名称
"状态": "进行中"

// 多选字段 (multipleSelect)
"标签": ["标签1", "标签2"]

// 勾选框字段 (checkbox)
"已完成": true
```

### 人员组织字段

```json
// 人员字段 (user) - unionId数组
"负责人": [{"unionId": "{union_id}"}]

// 部门字段 (department)
"部门": [{"deptId": "{dept_id}"}]

// 群组字段 (group)
"群组": [{"openConversationId": "cid/{conversation_id}"}]
```

### 高级字段

```json
// 链接字段 (url)
"链接": {"text": "显示文字", "link": "https://..."}

// 富文本字段 (richText)
"内容": {"markdown": "# 标题\n\n正文"}

// 关联字段 (unidirectionalLink/bidirectionalLink)
"关联记录": {"linkedRecordIds": ["{record_id}"]}
```

---

## 资源索引

### 核心脚本

- [scripts/dingtalk_api_client.py](scripts/dingtalk_api_client.py) - API客户端
  - 封装access_token获取、API请求、错误处理
  - 支持命令行调用

- [scripts/smart_import.py](scripts/smart_import.py) - Excel智能导入
  - 字段类型自动推断
  - 自动创建缺失字段
  - 支持人员、日期、附件等特殊字段

- [scripts/test_attachment_upload.py](scripts/test_attachment_upload.py) - 附件上传测试

### 参考资料

- [references/api_endpoints.md](references/api_endpoints.md) - API端点汇总
- [references/field_types.md](references/field_types.md) - 字段类型详解
- [references/error_codes.md](references/error_codes.md) - 错误码对照表
- [references/security_guidelines.md](references/security_guidelines.md) - 安全使用规范
- [references/smart_import_guide.md](references/smart_import_guide.md) - 智能导入完整指南
- [references/integration_cases/](references/integration_cases/) - 使用案例

---

## 常见问题

### Q: 配置消费者变量后仍然提示缺少凭证？

**A:** 请检查：
1. 变量名是否正确（区分大小写）
2. 变量值是否包含多余空格
3. 是否已重新加载Skill

### Q: 如何获取operatorId？

**A:** 两种方式：
1. **自动获取**（需通讯录权限）：`python scripts/dingtalk_api_client.py get_operator_id --user-name "姓名"`
2. **手动获取**：从钉钉后台 → 通讯录 → 成员详情页获取unionId

### Q: 长期计划中使用本Skill需要注意什么？

**A:** 
1. 确保消费者变量已正确配置（配置一次即可）
2. 如果Skill被重新加载，可能需要重新确认变量
3. 建议将常用参数（baseId、sheetName）保存到长期计划的上下文中

---

## 注意事项

1. **敏感信息保护**
   - 凭证必须配置为消费者变量，禁止硬编码
   - ID信息使用占位符，真实值运行时传入

2. **权限要求**
   - 确保已申请AI表格读写权限
   - 人员相关操作需通讯录权限

3. **数据格式**
   - 日期使用毫秒时间戳
   - 单选字段使用选项名称（不是ID）
   - 人员字段使用unionId对象数组

4. **智能导入**
   - 批次大小：500条/批
   - 多附件分隔符：分号 `;`
   - 字段标签后缀：`_导入`
