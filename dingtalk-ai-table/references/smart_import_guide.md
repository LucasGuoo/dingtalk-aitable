# 钉钉AI表格智能导入功能

基于Excel模板实现智能数据导入，支持字段类型自动推断、自动创建字段、特殊字段处理等功能。

## 快速开始

### 配置凭证（两种方式）

**方式A：独立变量（推荐，更安全）**
```bash
export DINGTALK_APP_KEY="你的Client ID"
export DINGTALK_APP_SECRET="你的Client Secret"
```

**方式B：JSON格式**
```bash
export COZE_DINGTALK_AI_TABLE_7611716228092264482='{"app_key": "你的Client ID", "app_secret": "你的Client Secret"}'
```

### 执行导入

```bash
python scripts/smart_import.py \
  --base-id YOUR_BASE_ID \
  --sheet-name YOUR_SHEET_NAME \
  --operator-id YOUR_OPERATOR_ID \
  --excel-file ./your_data.xlsx
```

## 功能特性

### 智能字段推断
自动分析Excel数据，推断字段类型：
- **文本** (text) - 默认类型
- **数字** (number) - 数值类型
- **日期** (date) - 日期时间类型
- **人员** (user) - 根据列名关键词识别（负责人、处理人等）
- **选项** (singleSelect) - 去重后数量较少的字段
- **附件** (attachment) - 根据文件扩展名识别

### 特殊字段处理

#### 人员字段
- 创建两个字段：`{字段名}` (user类型) 和 `{字段名}_导入` (text类型)
- 自动调用通讯录API将姓名转换为unionId
- 保留原始姓名到`_导入`字段

#### 日期字段
- 创建两个字段：`{字段名}` (date类型) 和 `{字段名}_导入` (text类型)
- 自动识别多种日期格式（2024-01-15、2024/1/15等）
- 转换为钉钉API所需的时间戳格式
- 保留原始字符串到`_导入`字段

#### 选项字段
- 自动提取Excel中的唯一值作为选项列表
- 为选项分配颜色

#### 附件字段
- 支持多附件上传（使用分号 `;` 分隔）
- 自动上传本地文件到钉钉OSS
- 生成attachment对象写入记录

### 批量导入
- 分批处理，每批500条记录
- 带进度条显示
- 错误记录继续执行

### 导入报告
- 生成字段映射表（JSON格式）
- 生成错误报告（如有）
- 统计导入成功/失败数量

## 使用方法

### 基本用法

```bash
python scripts/smart_import.py \
  --base-id YOUR_BASE_ID \
  --sheet-name YOUR_SHEET_NAME \
  --operator-id YOUR_OPERATOR_ID \
  --excel-file ./your_data.xlsx
```

### 参数说明

| 参数 | 说明 | 必填 |
|-----|------|------|
| `--base-id` | AI表格ID | 是 |
| `--sheet-name` | 数据表名称 | 是 |
| `--operator-id` | 操作人的unionId | 是 |
| `--excel-file` | Excel文件路径 | 是 |
| `--output-dir` | 报告输出目录（默认当前目录） | 否 |
| `--dry-run` | 试运行模式（不实际导入） | 否 |

### 试运行模式

在正式导入前，可以使用试运行模式查看字段映射关系：

```bash
python scripts/smart_import.py \
  --base-id xxx \
  --sheet-name xxx \
  --operator-id xxx \
  --excel-file ./data.xlsx \
  --dry-run
```

## Excel模板要求

### 基础格式
- 第一行为列标题
- 每列对应数据表中的一个字段
- 自动添加 `导入数据id` 列作为唯一标识

### 人员字段
- Excel中填写人员姓名（如"张三"）
- 支持多个人员，使用逗号分隔（如"张三,李四"）
- 列名建议包含"负责人"、"处理人"等关键词以便自动识别

### 日期字段
- 支持多种格式：2024-01-15、2024/1/15、15-01-2024等
- 列名建议包含"日期"、"时间"等关键词以便自动识别

### 附件字段
- 填写本地文件的完整路径
- 多附件使用分号 `;` 分隔
- 示例：`/path/to/file1.jpg;/path/to/file2.pdf`

### 选项字段
- Excel中的值将作为选项值
- 自动去重并生成选项列表

## 导入流程

```
1. 读取Excel文件
   └─ 添加【导入数据id】列（UUID）

2. 智能推断字段类型
   └─ 分析每列数据特征

3. 用户确认字段映射
   └─ 展示推断结果

4. 获取现有字段
   └─ 从数据表获取字段列表

5. 分析字段差异
   └─ 标记需要创建的字段

6. 建立映射表
   ├─ 人员：姓名 → unionId
   └─ 选项：值 → 选项对象

7. 创建缺失字段
   └─ 自动创建字段（带进度条）

8. 数据转换与导入
   ├─ 分批处理（每批500条）
   ├─ 转换特殊字段格式
   └─ 批量调用API

9. 生成导入报告
   ├─ 保存字段映射表
   ├─ 保存错误报告（如有）
   └─ 统计导入结果
```

## 示例

### 示例Excel结构

| 任务名称 | 负责人 | 截止日期 | 优先级 | 附件文件 |
|---------|-------|---------|-------|---------|
| 任务A | 张三 | 2024-01-15 | 高 | /path/file1.jpg |
| 任务B | 李四,王五 | 2024/02/01 | 中 | /path/file2.pdf;/path/file3.docx |

### 导入后数据表结构

| 字段名 | 类型 | 说明 |
|-------|------|------|
| 任务名称 | text | 原文本 |
| 负责人 | user | 转换为unionId |
| 负责人_导入 | text | 保留"张三" |
| 截止日期 | date | 转换为时间戳 |
| 截止日期_导入 | text | 保留"2024-01-15" |
| 优先级 | singleSelect | 选项：高/中/低 |
| 附件文件 | attachment | 上传后的附件对象 |
| 导入数据id | text | 自动生成的UUID |

## 注意事项

1. **凭证配置**：需提前配置环境变量 `COZE_DINGTALK_AI_TABLE_7611716228092264482`
2. **权限要求**：需开通AI表格读写权限、通讯录查询权限（用于人员字段转换）
3. **人员匹配**：人员姓名必须在企业通讯录中唯一匹配
4. **附件路径**：附件路径必须是脚本可访问的本地路径
5. **批次大小**：每批500条记录，大量数据会自动分批处理
6. **错误处理**：单条记录失败会记录错误，继续处理后续记录

## 测试附件上传

使用测试脚本验证附件上传功能：

```bash
# 测试单文件上传
python scripts/test_attachment_upload.py \
  --operator-id xxx \
  --file-path ./test.jpg \
  --create-test-files

# 测试批量上传
python scripts/test_attachment_upload.py \
  --operator-id xxx \
  --file-paths "./file1.jpg;./file2.pdf" \
  --base-id xxx \
  --sheet-name xxx \
  --test-write-record
```
