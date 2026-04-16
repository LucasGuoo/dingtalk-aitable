# 钉钉AI表格API端点汇总

## 概述

本文档汇总了钉钉AI表格（多维表）OpenAPI的所有端点信息，包括请求方法、路径、参数说明等。

**基础信息**
- 基础URL: `https://api.dingtalk.com`
- 认证方式: 通过Header `x-acs-dingtalk-access-token` 传递access_token
- 权限要求: 需要申请"AI表格应用读权限"和"AI表格应用写权限"

---

## 访问凭证接口

### 获取企业内部应用的accessToken

获取调用API所需的访问凭证。

- **方法**: POST
- **路径**: `/v1.0/oauth2/accessToken`
- **请求体**:
  ```json
  {
    "appKey": "应用的AppKey",
    "appSecret": "应用的AppSecret"
  }
  ```
- **响应**:
  ```json
  {
    "accessToken": "2bf******9be361a5084f1e2b8",
    "expireIn": 7200
  }
  ```
- **注意**: accessToken有效期7200秒，需要缓存并自动续期

---

## 数据表接口

### 获取所有数据表

获取AI表格中的所有数据表列表。

- **方法**: GET
- **路径**: `/v1.0/notable/bases/{baseId}/sheets`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **响应示例**:
  ```json
  {
    "sheets": [
      {
        "id": "stxxx",
        "name": "数据表1"
      }
    ]
  }
  ```

### 获取数据表

获取指定数据表的详细信息。

- **方法**: GET
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **响应示例**:
  ```json
  {
    "id": "stxxx",
    "name": "数据表1"
  }
  ```

### 创建数据表

在AI表格中创建新的数据表。

- **方法**: POST
- **路径**: `/v1.0/notable/bases/{baseId}/sheets`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **请求体**:
  ```json
  {
    "name": "数据表名称",
    "fields": [
      {
        "name": "字段名",
        "type": "text",
        "property": {}
      }
    ]
  }
  ```
- **响应示例**:
  ```json
  {
    "id": "stxxx",
    "name": "数据表名称"
  }
  ```

---

## 字段接口

### 获取所有字段

获取数据表中的所有字段列表。

- **方法**: GET
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **响应示例**:
  ```json
  {
    "fields": [
      {
        "id": "fdxxx",
        "name": "文本字段",
        "type": "text",
        "property": {}
      }
    ]
  }
  ```

### 创建字段

在数据表中创建新字段。

- **方法**: POST
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **请求体**:
  ```json
  {
    "name": "字段名",
    "type": "text",
    "property": {}
  }
  ```
- **响应示例**:
  ```json
  {
    "id": "fdxxx",
    "name": "字段名",
    "type": "text"
  }
  ```

### 更新字段

更新指定字段的配置。

- **方法**: PUT
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields/{fieldId}`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
  - `fieldId` (string, 必填): 字段ID
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **请求体**:
  ```json
  {
    "name": "新字段名",
    "property": {}
  }
  ```

### 删除字段

删除指定字段。

- **方法**: DELETE
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields/{fieldId}`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
  - `fieldId` (string, 必填): 字段ID
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId

---

## 记录接口

### 获取多行记录

获取数据表中的多条记录，支持分页和筛选。

- **方法**: POST
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/list`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **请求体**:
  ```json
  {
    "maxResults": 100,
    "nextToken": "分页游标",
    "filter": {
      "combination": "and",
      "conditions": [
        {
          "field": "字段名",
          "operator": "equal",
          "value": ["值"]
        }
      ]
    }
  }
  ```
- **请求参数说明**:
  - `maxResults` (integer, 可选): 每页记录数，默认100，范围1-100
  - `nextToken` (string, 可选): 分页游标，首次查询不传
  - `filter` (object, 可选): 筛选条件
    - `combination` (string): 条件组合方式，"and"(同时满足)或"or"(满足任一)
    - `conditions` (array): 条件数组
      - `field` (string): 字段ID或字段名
      - `operator` (string): 条件类型，可选值：
        - `equal`: 等于
        - `notEqual`: 不等于
        - `greater`: 大于
        - `greaterEqual`: 大于等于
        - `less`: 小于
        - `lessEqual`: 小于等于
        - `contain`: 包含
        - `notContain`: 不包含
        - `empty`: 为空
        - `notEmpty`: 不为空
      - `value` (array): 条件值数组
- **响应示例**:
  ```json
  {
    "hasMore": true,
    "nextToken": "tuvxxx",
    "records": [
      {
        "id": "recxxx",
        "fields": {
          "文本字段": "字段值",
          "数字字段": "123"
        },
        "createdBy": {"unionId": "xxx"},
        "lastModifiedBy": {"unionId": "xxx"},
        "createdTime": 1728644688000,
        "lastModifiedTime": 1728644688000
      }
    ]
  }
  ```

### 获取单行记录

获取单条记录的详细信息。

- **方法**: GET
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/{recordId}`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
  - `recordId` (string, 必填): 记录ID
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **响应示例**:
  ```json
  {
    "id": "recxxx",
    "fields": {
      "文本字段": "字段值"
    },
    "createdTime": 1728644688000,
    "lastModifiedTime": 1728644688000
  }
  ```

### 新增记录

在数据表中新增一条或多条记录。

- **方法**: POST
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **请求体**:
  ```json
  {
    "records": [
      {
        "fields": {
          "字段1": "值1",
          "字段2": "值2"
        }
      }
    ]
  }
  ```
- **响应示例**:
  ```json
  {
    "records": [
      {
        "id": "recxxx",
        "fields": {
          "字段1": "值1"
        },
        "createdTime": 1728644688000
      }
    ]
  }
  ```

### 更新记录

更新单条记录的字段值。

- **方法**: PUT
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/{recordId}`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
  - `recordId` (string, 必填): 记录ID
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId
- **请求体**:
  ```json
  {
    "fields": {
      "字段名": "新值"
    }
  }
  ```
- **注意**: 只支持更新部分字段类型，详见字段类型文档

### 删除记录

删除单条记录。

- **方法**: DELETE
- **路径**: `/v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/{recordId}`
- **路径参数**:
  - `baseId` (string, 必填): AI表格ID
  - `sheetIdOrName` (string, 必填): 数据表ID或名称
  - `recordId` (string, 必填): 记录ID
- **查询参数**:
  - `operatorId` (string, 必填): 操作人的unionId

---

## 附件接口

### 上传附件

上传文件作为附件使用。

- **方法**: POST
- **路径**: `/v1.0/notable/attachments`
- **请求头**:
  - `Content-Type`: multipart/form-data
  - `x-acs-dingtalk-access-token`: access_token
- **请求参数**:
  - `file` (file, 必填): 要上传的文件
- **响应示例**:
  ```json
  {
    "filename": "example.xlsx",
    "size": 92250,
    "type": "xls",
    "url": "https://xxx"
  }
  ```
- **使用说明**: 上传成功后，将返回的url用于新增/更新记录时的附件字段值

---

## 接口调用汇总表

| 操作类型 | 接口 | 方法 |
|---------|------|------|
| **访问凭证** | | |
| 获取access_token | /v1.0/oauth2/accessToken | POST |
| **数据表** | | |
| 获取所有数据表 | /v1.0/notable/bases/{baseId}/sheets | GET |
| 获取数据表 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName} | GET |
| 创建数据表 | /v1.0/notable/bases/{baseId}/sheets | POST |
| **字段** | | |
| 获取所有字段 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields | GET |
| 创建字段 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields | POST |
| 更新字段 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields/{fieldId} | PUT |
| 删除字段 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/fields/{fieldId} | DELETE |
| **记录** | | |
| 获取多行记录 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/list | POST |
| 获取单行记录 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/{recordId} | GET |
| 新增记录 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records | POST |
| 更新记录 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/{recordId} | PUT |
| 删除记录 | /v1.0/notable/bases/{baseId}/sheets/{sheetIdOrName}/records/{recordId} | DELETE |
| **附件** | | |
| 上传附件 | /v1.0/notable/attachments | POST |
