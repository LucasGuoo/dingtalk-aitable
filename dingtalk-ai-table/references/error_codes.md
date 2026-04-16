# 钉钉AI表格API错误码对照表

## 概述

本文档汇总了钉钉AI表格API可能返回的错误码，帮助开发者快速定位和解决问题。

---

## 通用错误码

### HTTP状态码

| HTTP Code | 说明 | 处理建议 |
|-----------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式和值是否正确 |
| 401 | 未授权 | 检查access_token是否有效或已过期 |
| 403 | 权限不足 | 检查应用是否已申请所需权限 |
| 404 | 资源不存在 | 检查baseId/sheetId/recordId等是否正确 |
| 429 | 请求过于频繁 | 降低请求频率，添加限流机制 |
| 500 | 服务器内部错误 | 稍后重试，如持续报错联系钉钉支持 |
| 503 | 服务暂时不可用 | 稍后重试 |
| 504 | 请求超时 | 检查网络状况，稍后重试 |

---

## 业务错误码

### 访问凭证相关

| 错误码 | 错误信息 | 说明 | 解决方案 |
|--------|----------|------|----------|
| invalid.client | invalid.client | ClientID或ClientSecret无效 | 检查AppKey和AppSecret是否正确 |
| unauthorized.client | unauthorized.client | 应用未被授权 | 检查应用是否已在企业内启用 |
| unsupported.grant.type | unsupported.grant.type | 不支持的授权类型 | 检查grant_type参数 |

### 文档/数据表相关

| 错误码 | 错误信息 | 说明 | 解决方案 |
|--------|----------|------|----------|
| invalidRequest.document.notFound | Fail to find the requested resource by the given baseId... | 文档不存在 | 检查baseId是否正确，确认操作人有权限访问 |
| invalidRequest.document.typeIllegal | %s | 不支持的文档类型 | 检查baseId对应的文档类型是否为AI表格 |
| invalidRequest.document.stillInitializing | The document is under initialization... | 文档初始化中 | 稍后重试，文档正在初始化 |
| invalidRequest.document.broken | The document is broken... | 文档已损坏 | 联系钉钉支持修复文档 |
| invalidRequest.resource.notFound | %s | 资源不存在 | 检查sheetId/fieldId/recordId是否正确 |

### 参数相关

| 错误码 | 错误信息 | 说明 | 解决方案 |
|--------|----------|------|----------|
| invalidRequest.inputArgs.invalid | %s | 请求参数不合法 | 根据错误信息检查参数格式和值 |
| invalidRequest.field.notFound | Field not found | 字段不存在 | 检查字段ID或字段名是否正确 |
| invalidRequest.field.typeIllegal | Field type is not supported | 不支持的字段类型 | 检查字段类型是否在支持列表中 |
| invalidRequest.record.notFound | Record not found | 记录不存在 | 检查recordId是否正确 |

### 权限相关

| 错误码 | 错误信息 | 说明 | 解决方案 |
|--------|----------|------|----------|
| forbidden.operationIllegal | %s | 无权限执行操作 | 检查应用是否已申请AI表格读写权限 |
| forbidden.userNoPermission | User has no permission | 用户无权限 | 检查operatorId是否正确，用户是否有权限访问该表格 |
| forbidden.appNoPermission | App has no permission | 应用无权限 | 在钉钉开发者后台为应用添加相应权限 |

### 系统错误

| 错误码 | 错误信息 | 说明 | 解决方案 |
|--------|----------|------|----------|
| internalError | The server encountered an internal error... | 服务器内部错误 | 稍后重试 |
| unknownError | Unknown Error | 未知错误 | 稍后重试，如持续报错联系钉钉支持 |
| service.timeout | The server is busy... | 请求超时 | 稍后重试 |
| service.rateLimit | Rate limit exceeded | 触发限流 | 降低请求频率 |

---

## 常见问题排查

### 1. access_token获取失败

**症状**: 调用获取access_token接口返回401或400错误

**排查步骤**:
1. 检查AppKey和AppSecret是否正确（注意区分大小写）
2. 确认应用是"企业内部应用"类型
3. 确认应用已在企业内启用
4. 检查网络是否可以访问api.dingtalk.com

### 2. 调用AI表格API返回403

**症状**: API返回403 forbidden.operationIllegal

**排查步骤**:
1. 登录钉钉开发者后台
2. 进入应用详情 -> 权限管理
3. 确认已添加以下权限：
   - AI表格应用读权限
   - AI表格应用写权限
4. 如权限已添加，等待5-10分钟后重试（权限生效有延迟）

### 3. 找不到文档/数据表

**症状**: API返回404 invalidRequest.document.notFound

**排查步骤**:
1. 检查baseId是否正确
   - 从AI表格URL中提取
   - 从文档信息面板查看
2. 确认操作人(operatorId)有权限访问该文档
3. 确认文档未被删除或移动

### 4. 字段值格式错误

**症状**: 新增/更新记录返回400错误

**排查步骤**:
1. 检查字段类型和值的匹配：
   - 文本字段：字符串
   - 数字字段：数字或字符串
   - 单选字段：选项名称字符串
   - 多选字段：选项名称字符串数组
   - 日期字段：时间戳或ISO 8601字符串
   - 人员字段：`[{unionId: "xxx"}]`
   - 部门字段：`[{deptId: "xxx"}]`
2. 检查必填字段是否已提供
3. 检查字段名是否正确（区分大小写）

### 5. 更新记录失败

**症状**: 部分字段更新后值未改变

**排查步骤**:
1. 确认字段类型支持API更新（以下类型不支持）：
   - 公式字段
   - 自动编号
   - 单向关联（目标端）
   - 双向关联
2. 检查是否有数据验证规则限制
3. 检查是否触发了工作流限制

### 6. 分页获取数据不完整

**症状**: 获取的记录数量少于预期

**排查步骤**:
1. 检查hasMore字段，确认是否还有更多数据
2. 使用nextToken继续获取下一页
3. 检查maxResults参数设置（最大100）
4. 如需获取全部数据，使用循环分页获取

---

## 调试技巧

### 使用API Explorer

1. 访问钉钉开放平台API Explorer
2. 选择对应接口进行调试
3. 确认参数正确后再集成到代码中

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 验证请求格式

```bash
# 使用curl测试API
curl -X POST "https://api.dingtalk.com/v1.0/notable/bases/{baseId}/sheets/{sheetId}/records/list?operatorId={operatorId}" \
  -H "Content-Type: application/json" \
  -H "x-acs-dingtalk-access-token: {access_token}" \
  -d '{"maxResults": 10}'
```

---

## 最佳实践

### 错误处理建议

```python
def handle_api_error(response):
    if response.status_code == 401:
        # Token过期，重新获取
        refresh_access_token()
    elif response.status_code == 429:
        # 触发限流，等待后重试
        time.sleep(5)
        retry_request()
    elif response.status_code >= 500:
        # 服务器错误，指数退避重试
        exponential_backoff_retry()
    else:
        # 其他错误，记录日志
        log_error(response.json())
```

### 权限检查清单

- [ ] 应用已创建并启用
- [ ] 已添加AI表格读权限
- [ ] 已添加AI表格写权限
- [ ] 操作人有权限访问目标文档
- [ ] access_token正确且未过期

### 参数验证建议

在调用API前，验证以下参数：
- baseId: 非空，长度合理
- operatorId: 有效的unionId格式
- sheetIdOrName: 非空
- 字段值: 与字段类型匹配
