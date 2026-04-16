# 对接案例模板

## 案例编号
CASE-YYYYMMDD-001

## 场景描述
简要描述本次对接的业务场景和需求背景。

## 对接信息

### 基础信息
- 对接日期: YYYY-MM-DD
- 对接人员: xxx
- 应用名称: xxx

### 表格信息
- baseId: xxx
- 数据表名称: xxx
- 涉及字段: 
  - 字段1(类型)
  - 字段2(类型)

## 调用的接口

| 序号 | 接口 | 用途 |
|------|------|------|
| 1 | /v1.0/notable/bases/{baseId}/sheets | 获取数据表 |
| 2 | ... | ... |

## 请求示例

### 请求1：获取数据表列表

```bash
curl -X GET "https://api.dingtalk.com/v1.0/notable/bases/{baseId}/sheets?operatorId={operatorId}" \
  -H "x-acs-dingtalk-access-token: {access_token}"
```

### 请求2：新增记录

```bash
curl -X POST "https://api.dingtalk.com/v1.0/notable/bases/{baseId}/sheets/{sheetId}/records?operatorId={operatorId}" \
  -H "Content-Type: application/json" \
  -H "x-acs-dingtalk-access-token: {access_token}" \
  -d '{
    "records": [
      {
        "fields": {
          "字段1": "值1",
          "字段2": "值2"
        }
      }
    ]
  }'
```

## 遇到的问题

### 问题1：xxx

**现象**: xxx

**原因**: xxx

**解决方案**: xxx

## 优化建议

- 建议1
- 建议2

## 经验总结

- 经验1
- 经验2

---

*创建时间: YYYY-MM-DD HH:MM*
