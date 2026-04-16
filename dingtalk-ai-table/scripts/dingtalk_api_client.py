#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉AI表格API调用客户端

封装了钉钉AI表格OpenAPI的调用，包括：
- access_token获取和管理
- 常用API接口的封装
- 错误处理和重试机制
- 自动获取operatorId(unionId)

凭证配置（三种方式任选其一）：
  1. 命令行参数: --app-key xxx --app-secret xxx（最灵活，无需配置）
  2. 消费者变量: DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET（配置一次，多次使用）
  3. JSON格式: COZE_DINGTALK_AI_TABLE_{skill_id}（环境变量方式）

使用示例：
  # 方式1: 命令行传入凭证
  python dingtalk_api_client.py show_fields \
    --app-key xxx --app-secret xxx \
    --base-id xxx --sheet-name xxx --operator-id xxx
  
  # 方式2: 已配置消费者变量
  python dingtalk_api_client.py show_fields \
    --base-id xxx --sheet-name xxx --operator-id xxx
  
  # 数据表操作
  python dingtalk_api_client.py get_sheets --base-id xxx --operator-id xxx
  python dingtalk_api_client.py show_fields --base-id xxx --sheet-name xxx --operator-id xxx
  
  # 记录操作
  python dingtalk_api_client.py list_records --base-id xxx --sheet-name xxx --operator-id xxx
  python dingtalk_api_client.py add_records --base-id xxx --sheet-name xxx --operator-id xxx \
    --records '[{"字段1": "值1"}]'
  
  # 获取operatorId(需要额外权限)
  python dingtalk_api_client.py get_operator_id --user-name "张三" --app-key xxx --app-secret xxx
"""

import os
import sys
import json
import argparse
import mimetypes
from typing import Optional, Dict, Any, List

# 优先尝试使用标准requests（支持外网访问）
# 如果需要使用coze_workload_identity，可以切换
try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# 尝试从coze_workload_identity导入（如果有网络代理限制则可能失败）
try:
    from coze_workload_identity import requests as _coze_requests
    _COZE_REQUESTS_AVAILABLE = True
except (ImportError, ValueError) as e:
    _COZE_REQUESTS_AVAILABLE = False
    _coze_requests = None

# 选择可用的requests
if _REQUESTS_AVAILABLE:
    requests = _requests
    print("使用标准requests库访问钉钉API")
elif _COZE_REQUESTS_AVAILABLE and _coze_requests:
    requests = _coze_requests
    print("使用coze_workload_identity访问钉钉API")
else:
    raise ImportError("无法加载requests库")


class DingTalkAIClient:
    """钉钉AI表格API客户端"""
    
    BASE_URL = "https://api.dingtalk.com"
    
    def __init__(self, app_key: str, app_secret: str):
        """
        初始化客户端
        
        Args:
            app_key: 钉钉应用的AppKey
            app_secret: 钉钉应用的AppSecret
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self._access_token: Optional[str] = None
    
    def _get_access_token(self) -> str:
        """
        获取access_token
        
        Returns:
            access_token字符串
        """
        if self._access_token:
            return self._access_token
        
        url = f"{self.BASE_URL}/v1.0/oauth2/accessToken"
        payload = {
            "appKey": self.app_key,
            "appSecret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "accessToken" not in data:
                raise ValueError(f"获取access_token失败: {data}")
            
            self._access_token = data["accessToken"]
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取access_token请求失败: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        
        Returns:
            包含access_token的请求头字典
        """
        return {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": self._get_access_token()
        }
    
    def _request(self, method: str, path: str, params: Optional[Dict] = None, 
                 data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            method: HTTP方法 (GET/POST/PUT/DELETE)
            path: API路径
            params: URL查询参数
            data: 请求体数据
            
        Returns:
            API响应数据
        """
        url = f"{self.BASE_URL}{path}"
        headers = self._get_headers()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, params=params, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
    
    # ========== 数据表操作 ==========
    
    def get_all_sheets(self, base_id: str, operator_id: str) -> List[Dict[str, Any]]:
        """
        获取AI表格中的所有数据表
        
        Args:
            base_id: AI表格ID
            operator_id: 操作人的unionId
            
        Returns:
            数据表列表
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets"
        params = {"operatorId": operator_id}
        return self._request("GET", path, params=params)
    
    def get_sheet(self, base_id: str, sheet_id_or_name: str, operator_id: str) -> Dict[str, Any]:
        """
        获取指定数据表信息
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            operator_id: 操作人的unionId
            
        Returns:
            数据表信息
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}"
        params = {"operatorId": operator_id}
        return self._request("GET", path, params=params)
    
    def create_sheet(self, base_id: str, operator_id: str, name: str, 
                     fields: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        创建数据表
        
        Args:
            base_id: AI表格ID
            operator_id: 操作人的unionId
            name: 数据表名称
            fields: 字段配置列表
            
        Returns:
            创建的数据表信息
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets"
        params = {"operatorId": operator_id}
        data = {"name": name}
        if fields:
            data["fields"] = fields
        return self._request("POST", path, params=params, data=data)
    
    # ========== 字段操作 ==========
    
    def get_all_fields(self, base_id: str, sheet_id_or_name: str, operator_id: str) -> List[Dict[str, Any]]:
        """
        获取数据表中的所有字段
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            operator_id: 操作人的unionId
            
        Returns:
            字段列表
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/fields"
        params = {"operatorId": operator_id}
        return self._request("GET", path, params=params)
    
    def create_field(self, base_id: str, sheet_id_or_name: str, operator_id: str,
                     name: str, field_type: str, property: Optional[Dict] = None) -> Dict[str, Any]:
        """
        创建字段
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            operator_id: 操作人的unionId
            name: 字段名称
            field_type: 字段类型
            property: 字段属性
            
        Returns:
            创建的字段信息
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/fields"
        params = {"operatorId": operator_id}
        data = {
            "name": name,
            "type": field_type
        }
        if property:
            data["property"] = property
        return self._request("POST", path, params=params, data=data)
    
    def update_field(self, base_id: str, sheet_id_or_name: str, field_id: str, 
                     operator_id: str, name: Optional[str] = None, 
                     property: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新字段
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            field_id: 字段ID
            operator_id: 操作人的unionId
            name: 新的字段名称
            property: 新的字段属性
            
        Returns:
            更新后的字段信息
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/fields/{field_id}"
        params = {"operatorId": operator_id}
        data = {}
        if name:
            data["name"] = name
        if property:
            data["property"] = property
        return self._request("PUT", path, params=params, data=data)
    
    def delete_field(self, base_id: str, sheet_id_or_name: str, field_id: str, 
                     operator_id: str) -> None:
        """
        删除字段
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            field_id: 字段ID
            operator_id: 操作人的unionId
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/fields/{field_id}"
        params = {"operatorId": operator_id}
        self._request("DELETE", path, params=params)
    
    def show_fields(self, base_id: str, sheet_id_or_name: str, operator_id: str) -> Dict[str, Any]:
        """
        获取并格式化展示数据表的所有字段信息
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            operator_id: 操作人的unionId
            
        Returns:
            格式化的字段信息，包含表格展示
        """
        fields = self.get_all_fields(base_id, sheet_id_or_name, operator_id)
        
        # 钉钉API返回的是 {"value": [...]} 格式
        field_list = fields.get("value", []) if isinstance(fields, dict) else fields
        
        # 格式化字段信息
        formatted_fields = []
        for idx, field in enumerate(field_list, 1):
            field_info = {
                "序号": idx,
                "字段名称": field.get("name", ""),
                "字段类型": field.get("type", ""),
                "字段ID": field.get("id", ""),
                "其他属性": ""
            }
            
            # 提取额外属性信息
            property_info = field.get("property", {})
            extra_attrs = []
            
            ftype = field.get("type", "")
            
            if ftype == "primaryDoc":
                extra_attrs.append("主字段")
            
            elif ftype in ["singleSelect", "multipleSelect"]:
                choices = property_info.get("choices", [])
                if choices:
                    choice_names = [c.get("name", "") for c in choices]
                    extra_attrs.append(f"选项:{','.join(choice_names)}")
            
            elif ftype == "number":
                formatter = property_info.get("formatter", "")
                if formatter:
                    extra_attrs.append(f"格式:{formatter}")
            
            elif ftype == "currency":
                formatter = property_info.get("formatter", "")
                currency_type = property_info.get("currencyType", "CNY")
                if formatter:
                    extra_attrs.append(f"格式:{formatter}")
                extra_attrs.append(f"货币:{currency_type}")
            
            elif ftype == "progress":
                formatter = property_info.get("formatter", "PERCENT")
                min_val = property_info.get("min", 0)
                max_val = property_info.get("max", 1)
                extra_attrs.append(f"类型:{formatter}, 范围:{min_val}-{max_val}")
            
            elif ftype == "rating":
                min_val = property_info.get("min", 1)
                max_val = property_info.get("max", 5)
                icon = property_info.get("icon", "star")
                extra_attrs.append(f"范围:{min_val}-{max_val}, 图标:{icon}")
            
            elif ftype == "url":
                extra_attrs.append("链接类型")
            
            elif ftype == "telephone":
                extra_attrs.append("电话号码")
            
            elif ftype == "email":
                extra_attrs.append("邮箱地址")
            
            elif ftype == "address":
                extra_attrs.append("行政区域")
            
            elif ftype == "barcode":
                extra_attrs.append("条码/二维码")
            
            elif ftype == "idCard":
                extra_attrs.append("身份证号码")
            
            elif ftype == "button":
                extra_attrs.append("按钮操作")
            
            elif ftype == "flow":
                options = property_info.get("options", [])
                if options:
                    option_names = [opt.get("name", "") for opt in options if opt.get("type") != "Deleted"]
                    extra_attrs.append(f"流程阶段:{','.join(option_names[:3])}...")
            
            elif ftype == "checkbox":
                extra_attrs.append("布尔勾选")
            
            elif ftype == "geolocation":
                extra_attrs.append("地理位置")
            
            elif ftype == "richText":
                extra_attrs.append("富文本格式")
            
            elif ftype in ["date", "createdTime", "lastModifiedTime"]:
                formatter = property_info.get("formatter", "")
                if formatter:
                    extra_attrs.append(f"格式:{formatter}")
                if ftype in ["createdTime", "lastModifiedTime"]:
                    extra_attrs.append("系统字段(只读)")
            
            elif ftype in ["user", "department", "group"]:
                multiple = property_info.get("multiple", True)
                if ftype == "user":
                    extra_attrs.append(f"人员选择, 多选:{'是' if multiple else '否'}")
                elif ftype == "department":
                    extra_attrs.append(f"部门选择, 多选:{'是' if multiple else '否'}")
                else:
                    extra_attrs.append(f"群组选择, 多选:{'是' if multiple else '否'}")
            
            elif ftype in ["creator", "lastModifier"]:
                extra_attrs.append("系统字段(只读)")
            
            elif ftype in ["unidirectionalLink", "bidirectionalLink"]:
                multiple = property_info.get("multiple", True)
                linked_sheet = property_info.get("linkedSheetId", "")
                extra_attrs.append(f"多选:{'是' if multiple else '否'}")
                if linked_sheet:
                    extra_attrs.append(f"关联表:{linked_sheet}")
                if ftype == "bidirectionalLink":
                    linked_field = property_info.get("linkedFieldId", "")
                    if linked_field:
                        extra_attrs.append(f"关联字段:{linked_field}")
            
            elif ftype == "attachment":
                extra_attrs.append("文件附件")
            
            field_info["其他属性"] = "; ".join(extra_attrs) if extra_attrs else "-"
            formatted_fields.append(field_info)
        
        return {
            "sheet_name": sheet_id_or_name,
            "total_fields": len(formatted_fields),
            "fields": formatted_fields
        }
    
    # ========== 用户查询（用于获取operatorId） ==========
    
    def search_user_by_name(self, query_word: str, full_match: bool = True) -> Dict[str, Any]:
        """
        根据姓名搜索用户userid
        
        需要权限：搜索企业通讯录权限(Contact.User.Search)
        
        Args:
            query_word: 搜索关键词（用户姓名）
            full_match: 是否精确匹配，默认为True
            
        Returns:
            用户userid列表
            {
                "hasMore": false,
                "totalCount": 1,
                "list": ["userid1", "userid2"]
            }
        """
        url = f"{self.BASE_URL}/v1.0/contact/users/search"
        headers = self._get_headers()
        
        data = {
            "queryWord": query_word,
            "offset": 0,
            "size": 10,
            "fullMatchField": 1 if full_match else 0
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"搜索用户失败: {str(e)}")
    
    def get_user_detail(self, userid: str) -> Dict[str, Any]:
        """
        查询用户详情，获取unionId
        
        使用旧版API（oapi.dingtalk.com），与钉钉开放平台调试工具一致
        需要权限：成员信息读权限(Contact.User.Read)
        注：精简权限模式下只返回基础信息（不包含手机号、邮箱等敏感字段）
        
        Args:
            userid: 用户userid
            
        Returns:
            用户详情，包含unionid字段
            {
                "errcode": 0,
                "errmsg": "ok",
                "result": {
                    "unionid": "xxxx",
                    "userid": "XXXX",
                    "name": "张三",
                    "title": "开发工程师",
                    "boss": false,
                    "admin": true,
                    "active": true,
                    ...
                },
                "request_id": "xxx"
            }
        """
        # 使用旧版API（与钉钉开放平台调试工具一致）
        # 旧版API需要将access_token作为URL参数
        access_token = self._get_access_token()
        url = f"https://oapi.dingtalk.com/topapi/v2/user/get?access_token={access_token}"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "userid": userid,
            "language": "zh_CN"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") != 0:
                raise Exception(f"查询用户详情失败: {result.get('errmsg', '未知错误')}")
            
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"查询用户详情失败: {str(e)}")
    
    def get_operator_id_by_name(self, user_name: str) -> Dict[str, Any]:
        """
        根据用户姓名自动获取operatorId(unionId)
        
        整合流程：
        1. 搜索用户获取userid
        2. 查询用户详情获取unionId
        
        需要权限：
        - 搜索企业通讯录权限(Contact.User.Search)
        - 成员信息读权限(Contact.User.Read) - 精简模式即可
        
        Args:
            user_name: 用户姓名全称
            
        Returns:
            {
                "success": true,
                "name": "郭智强",
                "userid": "03242700205636491693",
                "unionid": "gvS5hafxxxx",
                "title": "开发工程师"
            }
        """
        # 步骤1：搜索用户
        search_result = self.search_user_by_name(user_name, full_match=True)
        
        if not search_result.get("list"):
            raise ValueError(f"未找到姓名为「{user_name}」的用户，请检查姓名是否正确")
        
        user_list = search_result["list"]
        
        if len(user_list) > 1:
            return {
                "success": False,
                "message": f"找到多个姓名为「{user_name}」的用户",
                "users": user_list,
                "hint": "请提供userid指定具体用户"
            }
        
        userid = user_list[0]
        
        # 步骤2：查询用户详情
        detail_result = self.get_user_detail(userid)
        
        # 处理精简权限返回格式
        if "result" in detail_result:
            user_info = detail_result["result"]
        else:
            user_info = detail_result
        
        unionid = user_info.get("unionid", "")
        if not unionid:
            raise ValueError(f"获取unionid失败，用户详情: {user_info}")
        
        return {
            "success": True,
            "name": user_info.get("name", ""),
            "userid": userid,
            "unionid": unionid,
            "title": user_info.get("title", ""),
            "active": user_info.get("active", False),
            "admin": user_info.get("admin", False)
        }
    
    # ========== 记录操作 ==========
    
    def list_records(self, base_id: str, sheet_id_or_name: str, operator_id: str,
                     max_results: int = 100, next_token: Optional[str] = None,
                     filter_conditions: Optional[Dict] = None) -> Dict[str, Any]:
        """
        获取多行记录（支持分页和筛选）
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            operator_id: 操作人的unionId
            max_results: 每页返回记录数(1-100)
            next_token: 分页游标
            filter_conditions: 筛选条件
                {
                    "combination": "and" | "or",
                    "conditions": [
                        {"field": "字段名", "operator": "equal", "value": ["值"]}
                    ]
                }
            
        Returns:
            {
                "hasMore": bool,
                "nextToken": str,
                "records": [
                    {
                        "id": "记录ID",
                        "fields": {"字段名": "值"},
                        "createdTime": 时间戳,
                        "lastModifiedTime": 时间戳
                    }
                ]
            }
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/records/list"
        params = {"operatorId": operator_id}
        data = {"maxResults": max_results}
        if next_token:
            data["nextToken"] = next_token
        if filter_conditions:
            data["filter"] = filter_conditions
        return self._request("POST", path, params=params, data=data)
    
    def get_record(self, base_id: str, sheet_id_or_name: str, record_id: str, 
                   operator_id: str) -> Dict[str, Any]:
        """
        获取单行记录
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            record_id: 记录ID
            operator_id: 操作人的unionId
            
        Returns:
            记录详情
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/records/{record_id}"
        params = {"operatorId": operator_id}
        return self._request("GET", path, params=params)
    
    def add_records(self, base_id: str, sheet_id_or_name: str, operator_id: str,
                    records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        新增多条记录
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            operator_id: 操作人的unionId
            records: 记录列表，格式：[{"字段名": "值"}]
            
        Returns:
            新增的记录信息
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/records"
        params = {"operatorId": operator_id}
        data = {"records": [{"fields": r} for r in records]}
        return self._request("POST", path, params=params, data=data)
    
    def update_record(self, base_id: str, sheet_id_or_name: str, record_id: str,
                      operator_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新单条记录
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            record_id: 记录ID
            operator_id: 操作人的unionId
            fields: 要更新的字段值 {"字段名": "新值"}
            
        Returns:
            更新后的记录信息
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/records"
        params = {"operatorId": operator_id}
        data = {
            "records": [
                {
                    "id": record_id,
                    "fields": fields
                }
            ]
        }
        return self._request("PUT", path, params=params, data=data)
    
    def update_records(self, base_id: str, sheet_id_or_name: str,
                       operator_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量更新多条记录
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            operator_id: 操作人的unionId
            records: 记录列表，格式：[{"id": "记录ID", "fields": {"字段名": "新值"}}]
            
        Returns:
            更新的记录信息
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/records"
        params = {"operatorId": operator_id}
        data = {"records": records}
        return self._request("PUT", path, params=params, data=data)
    
    def delete_record(self, base_id: str, sheet_id_or_name: str, record_id: str,
                      operator_id: str) -> None:
        """
        删除单条记录
        
        Args:
            base_id: AI表格ID
            sheet_id_or_name: 数据表ID或名称
            record_id: 记录ID
            operator_id: 操作人的unionId
        """
        path = f"/v1.0/notable/bases/{base_id}/sheets/{sheet_id_or_name}/records/{record_id}"
        params = {"operatorId": operator_id}
        self._request("DELETE", path, params=params)
    
    # ========== 附件操作 ==========
    
    def get_attachment_upload_info(self, operator_id: str, resource_name: str, 
                                   media_type: str, size: int,
                                   parent_resource_id: Optional[str] = None,
                                   parent_node_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取附件上传信息
        
        步骤1：获取上传所需的resourceId、uploadUrl、resourceUrl
        
        Args:
            operator_id: 操作人的unionId
            resource_name: 资源名称（文件名）
            media_type: 媒体类型（MIME类型，如 image/jpeg, application/pdf）
            size: 文件大小（字节）
            parent_resource_id: 父资源ID（可选）
            parent_node_id: 父节点ID（可选）
            
        Returns:
            {
                "resourceId": "xxx",
                "resourceUrl": "/core/api/resources/...",
                "uploadUrl": "https://oss.aliyun.com/..."
            }
        """
        path = "/v1.0/notable/attachments/uploadInfos"
        params = {"operatorId": operator_id}
        
        data = {
            "resourceName": resource_name,
            "mediaType": media_type,
            "size": size
        }
        
        if parent_resource_id:
            data["parentResourceId"] = parent_resource_id
        if parent_node_id:
            data["parentNodeId"] = parent_node_id
            
        return self._request("POST", path, params=params, data=data)
    
    def upload_file_to_oss(self, upload_url: str, file_path: str, 
                          media_type: Optional[str] = None) -> bool:
        """
        上传文件到OSS
        
        步骤2：将文件上传到步骤1返回的uploadUrl
        
        Args:
            upload_url: 步骤1返回的uploadUrl
            file_path: 本地文件路径
            media_type: 媒体类型（如果不提供则自动推断）
            
        Returns:
            上传是否成功
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 自动推断MIME类型
        if not media_type:
            media_type, _ = mimetypes.guess_type(file_path)
            if not media_type:
                media_type = "application/octet-stream"
        
        headers = {
            "Content-Type": media_type
        }
        
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            response = requests.put(upload_url, data=file_data, headers=headers, timeout=120)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"上传文件到OSS失败: {str(e)}")
    
    def upload_attachment(self, operator_id: str, file_path: str) -> Dict[str, Any]:
        """
        完整的附件上传流程
        
        整合三个步骤：
        1. 获取上传信息
        2. 上传文件到OSS
        3. 返回attachment对象（用于写入记录）
        
        Args:
            operator_id: 操作人的unionId
            file_path: 本地文件路径
            
        Returns:
            attachment对象，可直接用于写入记录：
            {
                "filename": "xxx.jpg",
                "size": 1024,
                "type": "image/jpeg",
                "url": "/core/api/resources/...",
                "resourceId": "xxx"
            }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件信息
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # 推断MIME类型
        media_type, _ = mimetypes.guess_type(file_path)
        if not media_type:
            media_type = "application/octet-stream"
        
        # 步骤1：获取上传信息
        upload_info = self.get_attachment_upload_info(
            operator_id=operator_id,
            resource_name=file_name,
            media_type=media_type,
            size=file_size
        )
        
        # 步骤2：上传文件
        self.upload_file_to_oss(upload_info["uploadUrl"], file_path, media_type)
        
        # 步骤3：返回attachment对象
        return {
            "filename": file_name,
            "size": file_size,
            "type": media_type,
            "url": upload_info["resourceUrl"],
            "resourceId": upload_info["resourceId"]
        }
    
    def upload_attachments(self, operator_id: str, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量上传多个附件
        
        Args:
            operator_id: 操作人的unionId
            file_paths: 本地文件路径列表
            
        Returns:
            attachment对象列表
        """
        attachments = []
        for file_path in file_paths:
            try:
                attachment = self.upload_attachment(operator_id, file_path)
                attachments.append(attachment)
            except Exception as e:
                print(f"警告: 上传文件 {file_path} 失败: {str(e)}", file=sys.stderr)
                # 继续上传其他文件
        
        return attachments


def get_credentials(app_key: Optional[str] = None, app_secret: Optional[str] = None) -> Dict[str, str]:
    """
    获取钉钉应用凭证
    
    支持三种方式（优先级从高到低）：
    1. 命令行参数传入: --app-key 和 --app-secret
    2. 环境变量: DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
    3. JSON格式变量: COZE_DINGTALK_AI_TABLE_{skill_id}
    
    Args:
        app_key: 命令行传入的AppKey（可选）
        app_secret: 命令行传入的AppSecret（可选）
    
    Returns:
        包含app_key和app_secret的字典
    """
    # 方式1: 命令行参数传入（最高优先级）
    if app_key and app_secret:
        return {
            "app_key": app_key,
            "app_secret": app_secret
        }
    
    skill_id = "7611716228092264482"
    
    # 方式2: 检查独立的消费者变量
    env_app_key = os.getenv("DINGTALK_APP_KEY")
    env_app_secret = os.getenv("DINGTALK_APP_SECRET")
    
    if env_app_key and env_app_secret:
        return {
            "app_key": env_app_key,
            "app_secret": env_app_secret
        }
    
    # 方式3: 检查JSON格式的凭证变量
    credential_key = f"COZE_DINGTALK_AI_TABLE_{skill_id}"
    credential_str = os.getenv(credential_key)
    
    if not credential_str:
        credential_str = os.getenv(f"COZE_DINGTALK_CREDENTIALS_{skill_id}")
    
    if not credential_str:
        raise ValueError(
            f"缺少钉钉应用凭证。请通过以下任一方式提供：\n"
            f"\n方式1（推荐）- 命令行参数：\n"
            f"  --app-key 你的Client ID --app-secret 你的Client Secret\n"
            f"\n方式2 - 配置消费者变量：\n"
            f"  DINGTALK_APP_KEY=你的Client ID\n"
            f"  DINGTALK_APP_SECRET=你的Client Secret"
        )
    
    try:
        credential = json.loads(credential_str)
        return {
            "app_key": credential["app_key"],
            "app_secret": credential["app_secret"]
        }
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"凭证格式错误: {str(e)}。格式应为: {{\"app_key\": \"xxx\", \"app_secret\": \"xxx\"}}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="钉钉AI表格API客户端")
    subparsers = parser.add_subparsers(dest="operation", help="操作类型")
    
    # 通用参数（包含凭证参数）
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--app-key", help="钉钉应用Client ID（可选，也可通过环境变量配置）")
    parent_parser.add_argument("--app-secret", help="钉钉应用Client Secret（可选，也可通过环境变量配置）")
    parent_parser.add_argument("--base-id", required=True, help="AI表格ID")
    parent_parser.add_argument("--operator-id", required=True, help="操作人的unionId")
    
    # 获取所有数据表
    subparsers.add_parser("get_sheets", parents=[parent_parser], help="获取所有数据表")
    
    # 获取数据表
    get_sheet_parser = subparsers.add_parser("get_sheet", parents=[parent_parser], help="获取数据表")
    get_sheet_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    
    # 创建数据表
    create_sheet_parser = subparsers.add_parser("create_sheet", parents=[parent_parser], help="创建数据表")
    create_sheet_parser.add_argument("--name", required=True, help="数据表名称")
    create_sheet_parser.add_argument("--fields", help="字段配置JSON字符串")
    
    # 获取所有字段
    get_fields_parser = subparsers.add_parser("get_fields", parents=[parent_parser], help="获取所有字段")
    get_fields_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    
    # 获取记录列表
    list_records_parser = subparsers.add_parser("list_records", parents=[parent_parser], help="获取记录列表")
    list_records_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    list_records_parser.add_argument("--max-results", type=int, default=100, help="每页记录数(1-100)")
    list_records_parser.add_argument("--next-token", help="分页游标")
    list_records_parser.add_argument("--filter", help="筛选条件JSON字符串")
    
    # 获取单条记录
    get_record_parser = subparsers.add_parser("get_record", parents=[parent_parser], help="获取单条记录")
    get_record_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    get_record_parser.add_argument("--record-id", required=True, help="记录ID")
    
    # 新增记录
    add_records_parser = subparsers.add_parser("add_records", parents=[parent_parser], help="新增记录")
    add_records_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    add_records_parser.add_argument("--records", required=True, help="记录数据JSON字符串，格式：[{\"字段\":\"值\"}]")
    
    # 更新记录
    update_record_parser = subparsers.add_parser("update_record", parents=[parent_parser], help="更新记录")
    update_record_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    update_record_parser.add_argument("--record-id", required=True, help="记录ID")
    update_record_parser.add_argument("--fields", required=True, help="字段值JSON字符串，格式：{\"字段\":\"值\"}")
    
    # 删除记录
    delete_record_parser = subparsers.add_parser("delete_record", parents=[parent_parser], help="删除记录")
    delete_record_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    delete_record_parser.add_argument("--record-id", required=True, help="记录ID")
    
    # 展示字段结构（新增命令）
    show_fields_parser = subparsers.add_parser("show_fields", parents=[parent_parser], help="展示数据表字段结构")
    show_fields_parser.add_argument("--sheet-name", required=True, help="数据表名称或ID")
    
    # 附件上传（独立命令，不需要base-id，只需要operator-id）
    upload_attachment_parser = subparsers.add_parser("upload_attachment", help="上传附件文件")
    upload_attachment_parser.add_argument("--operator-id", required=True, help="操作人的unionId")
    upload_attachment_parser.add_argument("--file-path", required=True, help="本地文件路径")
    
    # 批量上传附件
    upload_attachments_parser = subparsers.add_parser("upload_attachments", help="批量上传附件文件")
    upload_attachments_parser.add_argument("--operator-id", required=True, help="操作人的unionId")
    upload_attachments_parser.add_argument("--file-paths", required=True, help="本地文件路径列表，分号分隔")
    
    # 获取operatorId（独立命令，不需要base-id和operator-id）
    get_operator_id_parser = subparsers.add_parser("get_operator_id", help="根据姓名获取operatorId(unionId)")
    get_operator_id_parser.add_argument("--user-name", required=True, help="用户姓名全称")
    
    args = parser.parse_args()
    
    if not args.operation:
        parser.print_help()
        sys.exit(1)
    
    # 特殊处理：不需要base-id的命令
    if args.operation in ["get_operator_id", "upload_attachment", "upload_attachments"]:
        try:
            credentials = get_credentials(getattr(args, 'app_key', None), getattr(args, 'app_secret', None))
            client = DingTalkAIClient(credentials["app_key"], credentials["app_secret"])
            
            if args.operation == "get_operator_id":
                result = client.get_operator_id_by_name(args.user_name)
                
            elif args.operation == "upload_attachment":
                result = client.upload_attachment(args.operator_id, args.file_path)
                
            elif args.operation == "upload_attachments":
                file_paths = [p.strip() for p in args.file_paths.split(";") if p.strip()]
                result = client.upload_attachments(args.operator_id, file_paths)
            
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
        return
    
    # 获取凭证并创建客户端
    credentials = get_credentials(getattr(args, 'app_key', None), getattr(args, 'app_secret', None))
    client = DingTalkAIClient(credentials["app_key"], credentials["app_secret"])
    
    try:
        # 执行操作
        if args.operation == "get_sheets":
            result = client.get_all_sheets(args.base_id, args.operator_id)
            
        elif args.operation == "get_sheet":
            result = client.get_sheet(args.base_id, args.sheet_name, args.operator_id)
            
        elif args.operation == "create_sheet":
            fields = json.loads(args.fields) if args.fields else None
            result = client.create_sheet(args.base_id, args.operator_id, args.name, fields)
            
        elif args.operation == "get_fields":
            result = client.get_all_fields(args.base_id, args.sheet_name, args.operator_id)
            
        elif args.operation == "list_records":
            filter_conditions = json.loads(args.filter) if args.filter else None
            result = client.list_records(
                args.base_id, args.sheet_name, args.operator_id,
                args.max_results, args.next_token, filter_conditions
            )
            
        elif args.operation == "get_record":
            result = client.get_record(args.base_id, args.sheet_name, args.record_id, args.operator_id)
            
        elif args.operation == "add_records":
            records = json.loads(args.records)
            result = client.add_records(args.base_id, args.sheet_name, args.operator_id, records)
            
        elif args.operation == "update_record":
            fields = json.loads(args.fields)
            result = client.update_record(args.base_id, args.sheet_name, args.record_id, args.operator_id, fields)
            
        elif args.operation == "delete_record":
            client.delete_record(args.base_id, args.sheet_name, args.record_id, args.operator_id)
            result = {"success": True, "message": "记录已删除"}
            
        elif args.operation == "show_fields":
            result = client.show_fields(args.base_id, args.sheet_name, args.operator_id)
            
        else:
            print(f"未知操作: {args.operation}", file=sys.stderr)
            sys.exit(1)
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
