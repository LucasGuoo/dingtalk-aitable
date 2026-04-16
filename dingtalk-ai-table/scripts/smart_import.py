#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
钉钉AI表格智能导入脚本

基于Excel模板实现智能导入功能：
- 字段类型自动推断
- 字段匹配与自动创建
- 特殊字段处理（人员、日期、选项、附件）
- 批量导入及错误处理

使用方法（方式1 - 命令行传入凭证，推荐）：
    python smart_import.py \
      --app-key "你的Client ID" \
      --app-secret "你的Client Secret" \
      --base-id xxx \
      --sheet-name xxx \
      --operator-id xxx \
      --excel-file ./data.xlsx

使用方法（方式2 - 已配置消费者变量）：
    python smart_import.py \
      --base-id xxx \
      --sheet-name xxx \
      --operator-id xxx \
      --excel-file ./data.xlsx

配置（可选）：
    如需配置消费者变量，设置 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
"""

import os
import sys
import json
import uuid
import argparse
import mimetypes
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dingtalk_api_client import DingTalkAIClient, get_credentials


# ========== 常量定义 ==========

IMPORT_ID_FIELD = "导入数据id"  # 唯一标识列
IMPORT_TAG_SUFFIX = "_导入"     # 导入标签后缀
BATCH_SIZE = 500                # 批量导入批次大小
ATTACHMENT_DELIMITER = ";"      # 多附件分隔符

# 字段类型推断规则
FIELD_TYPE_RULES = {
    "text": {
        "check": lambda series: True,  # 默认类型
        "dingtalk_type": "text"
    },
    "number": {
        "check": lambda series: pd.api.types.is_numeric_dtype(series),
        "dingtalk_type": "number"
    },
    "date": {
        "check": lambda series: False,  # 需要特殊检测
        "dingtalk_type": "date"
    },
    "user": {
        "check": lambda series: False,  # 需要特殊检测
        "dingtalk_type": "user"
    },
    "attachment": {
        "check": lambda series: series.astype(str).str.contains(r'\.(jpg|jpeg|png|gif|pdf|doc|docx|xls|xlsx)$', case=False, na=False).any(),
        "dingtalk_type": "attachment"
    },
    "singleSelect": {
        "check": lambda series: series.nunique() / len(series) < 0.1 if len(series) > 0 else False,
        "dingtalk_type": "singleSelect"
    }
}


class SmartImporter:
    """智能导入器"""
    
    def __init__(self, client: DingTalkAIClient, base_id: str, sheet_name: str, 
                 operator_id: str, path_mappings: Optional[Dict[str, str]] = None):
        """
        初始化智能导入器
        
        Args:
            client: 钉钉API客户端
            base_id: AI表格ID
            sheet_name: 数据表名称
            operator_id: 操作人的unionId
            path_mappings: 路径映射规则，用于转换Windows路径到Linux路径
                          格式: {"C:/Users/xxx/yyy": "/workspace/yyy", ...}
        """
        self.client = client
        self.base_id = base_id
        self.sheet_name = sheet_name
        self.operator_id = operator_id
        self.path_mappings = path_mappings or {}
        
        # 状态数据
        self.excel_df: Optional[pd.DataFrame] = None
        self.excel_columns: List[str] = []
        self.field_mapping: Dict[str, Dict] = {}  # 字段映射配置
        self.existing_fields: Dict[str, Dict] = {}  # 现有字段
        self.user_mapping: Dict[str, str] = {}  # 姓名 -> unionId
        self.option_mapping: Dict[str, Dict] = {}  # 字段 -> {值: 选项对象}
        self.import_session_id: str = str(uuid.uuid4())[:8]
        
        # 导入统计
        self.stats = {
            "total_rows": 0,
            "success_count": 0,
            "error_count": 0,
            "created_fields": [],
            "errors": []
        }
    
    # ========== 阶段1: Excel读取与预处理 ==========
    
    def load_excel(self, file_path: str) -> pd.DataFrame:
        """
        读取Excel文件并添加导入ID列
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            DataFrame
        """
        print(f"\n📖 读取Excel文件: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取Excel
        df = pd.read_excel(file_path)
        
        # 添加导入数据id列
        df[IMPORT_ID_FIELD] = [str(uuid.uuid4()) for _ in range(len(df))]
        
        self.excel_df = df
        self.excel_columns = df.columns.tolist()
        self.stats["total_rows"] = len(df)
        
        print(f"   ✅ 成功读取 {len(df)} 行数据，{len(df.columns)} 列")
        print(f"   📝 已添加「{IMPORT_ID_FIELD}」列用于唯一标识")
        
        return df
    
    # ========== 阶段2: 字段类型推断 ==========
    
    def infer_field_types(self) -> Dict[str, str]:
        """
        智能推断字段类型
        
        Returns:
            字段名 -> 推断类型的映射
        """
        print(f"\n🔍 智能推断字段类型...")
        
        inferred_types = {}
        sample_size = min(3, len(self.excel_df))
        
        for col in self.excel_columns:
            if col == IMPORT_ID_FIELD:
                continue
            
            series = self.excel_df[col]
            inferred_type = self._infer_single_field_type(series, col)
            inferred_types[col] = inferred_type
            
            # 显示推断结果
            sample_values = series.dropna().head(sample_size).tolist()
            print(f"   📌 {col}: {inferred_type}")
            print(f"      示例值: {sample_values}")
        
        return inferred_types
    
    def _infer_single_field_type(self, series: pd.Series, col_name: str) -> str:
        """推断单个字段的类型"""
        # 1. 检测人员字段（列名包含特定关键词）
        user_keywords = ["负责人", "处理人", "执行人", "指派给", "创建人", "owner", "assignee"]
        if any(kw in col_name.lower() for kw in user_keywords):
            return "user"
        
        # 2. 检测日期字段（列名包含特定关键词）
        date_keywords = ["日期", "时间", "date", "time", "截止", "开始", "结束"]
        if any(kw in col_name.lower() for kw in date_keywords):
            # 验证是否包含日期格式数据
            if self._is_date_series(series):
                return "date"
        
        # 3. 检测选项字段（列名包含特定关键词或小数据量去重）
        select_keywords = ["机构", "部门", "类型", "状态", "类别", "优先级", "所属"]
        has_select_keyword = any(kw in col_name.lower() for kw in select_keywords)
        is_low_cardinality = series.nunique() / len(series) < 0.5 if len(series) > 0 else False
        
        if has_select_keyword or (is_low_cardinality and series.nunique() <= 20):
            return "singleSelect"
        
        # 4. 检测附件字段
        if FIELD_TYPE_RULES["attachment"]["check"](series):
            return "attachment"
        
        # 5. 检测数字字段
        if FIELD_TYPE_RULES["number"]["check"](series):
            return "number"
        
        # 默认文本类型
        return "text"
    
    def _is_date_series(self, series: pd.Series) -> bool:
        """检测是否为日期类型数据"""
        try:
            # 尝试转换为日期
            pd.to_datetime(series.dropna().head(10), errors='raise')
            return True
        except:
            # 检查是否包含日期格式的字符串
            sample = series.dropna().astype(str).head(10)
            date_patterns = [
                r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # 2024-01-15, 2024/01/15
                r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # 15-01-2024
            ]
            for pattern in date_patterns:
                if sample.str.match(pattern).any():
                    return True
            return False
    
    # ========== 阶段3: 用户确认字段映射 ==========
    
    def confirm_field_mapping(self, inferred_types: Dict[str, str]) -> Dict[str, Dict]:
        """
        生成并确认字段映射配置
        
        Args:
            inferred_types: 推断的字段类型
            
        Returns:
            字段映射配置
        """
        print(f"\n📝 字段映射配置:")
        print("-" * 60)
        
        mapping = {}
        for col in self.excel_columns:
            if col == IMPORT_ID_FIELD:
                continue
            
            inferred = inferred_types.get(col, "text")
            
            # 对于特殊类型，创建双字段配置
            if inferred == "user":
                mapping[col] = {
                    "source_column": col,
                    "target_field": col,  # user类型字段
                    "target_field_import": f"{col}{IMPORT_TAG_SUFFIX}",  # text类型保留原始值
                    "type": "user",
                    "confirmed": True
                }
            elif inferred == "date":
                mapping[col] = {
                    "source_column": col,
                    "target_field": col,  # date类型字段
                    "target_field_original": f"{col}{IMPORT_TAG_SUFFIX}",  # text类型保留原始值
                    "type": "date",
                    "confirmed": True
                }
            elif inferred == "singleSelect":
                # 提取唯一值作为选项
                unique_values = self.excel_df[col].dropna().unique().tolist()
                mapping[col] = {
                    "source_column": col,
                    "target_field": col,
                    "type": "singleSelect",
                    "options": unique_values,
                    "confirmed": True
                }
            elif inferred == "attachment":
                mapping[col] = {
                    "source_column": col,
                    "target_field": col,
                    "type": "attachment",
                    "confirmed": True
                }
            else:
                mapping[col] = {
                    "source_column": col,
                    "target_field": col,
                    "type": inferred,
                    "confirmed": True
                }
            
            config = mapping[col]
            print(f"   📌 {col} -> {config['target_field']} ({config['type']})")
            if config['type'] == 'user':
                print(f"      └─ 保留原始值字段: {config['target_field_import']}")
            elif config['type'] == 'date':
                print(f"      └─ 保留原始值字段: {config['target_field_original']}")
            elif config['type'] == 'singleSelect':
                print(f"      └─ 选项数: {len(config['options'])}")
        
        self.field_mapping = mapping
        return mapping
    
    # ========== 阶段5: 获取现有字段 & 阶段6: 差异分析 ==========
    
    def load_existing_fields(self) -> Dict[str, Dict]:
        """
        获取数据表中现有字段
        
        Returns:
            字段名 -> 字段信息的映射
        """
        print(f"\n📂 获取数据表现有字段...")
        
        fields = self.client.get_all_fields(self.base_id, self.sheet_name, self.operator_id)
        
        # 处理返回格式
        field_list = fields.get("value", []) if isinstance(fields, dict) else fields
        
        self.existing_fields = {}
        self.field_id_map = {}  # 字段名 -> fieldId 映射
        self.field_id_to_name = {}  # fieldId -> 字段名 映射
        
        for field in field_list:
            name = field.get("name")
            field_id = field.get("id")
            if name:
                self.existing_fields[name] = field
                if field_id:
                    self.field_id_map[name] = field_id
                    self.field_id_to_name[field_id] = name
        
        print(f"   ✅ 获取到 {len(self.existing_fields)} 个现有字段")
        print(f"   📋 字段ID映射:")
        for name, fid in self.field_id_map.items():
            print(f"      {name} -> {fid}")
        
        return self.existing_fields
    
    def get_field_id(self, field_name: str) -> Optional[str]:
        """获取字段ID"""
        return self.field_id_map.get(field_name)
    
    def analyze_field_diff(self) -> Tuple[List[str], List[str]]:
        """
        分析字段差异，找出需要创建的字段
        
        Returns:
            (需要创建的字段列表, 已存在的字段列表)
        """
        print(f"\n🔍 分析字段差异...")
        
        to_create = []
        exists = []
        
        for col, config in self.field_mapping.items():
            target_field = config["target_field"]
            
            # 检查主字段
            if target_field not in self.existing_fields:
                to_create.append({
                    "excel_column": col,
                    "field_name": target_field,
                    "field_type": config["type"],
                    "config": config
                })
            else:
                exists.append(target_field)
            
            # 检查辅助字段（_导入）
            if config["type"] == "user":
                import_field = config.get("target_field_import")
                if import_field and import_field not in self.existing_fields:
                    to_create.append({
                        "excel_column": col,
                        "field_name": import_field,
                        "field_type": "text",
                        "config": config
                    })
            
            elif config["type"] == "date":
                original_field = config.get("target_field_original")
                if original_field and original_field not in self.existing_fields:
                    to_create.append({
                        "excel_column": col,
                        "field_name": original_field,
                        "field_type": "text",
                        "config": config
                    })
        
        print(f"   📊 分析结果:")
        print(f"      - 已存在字段: {len(exists)} 个")
        print(f"      - 需要创建: {len(to_create)} 个")
        
        return to_create, exists
    
    # ========== 阶段7: 建立映射表 ==========
    
    def build_user_mapping(self) -> Dict[str, str]:
        """
        建立姓名 -> unionId 映射表
        
        Returns:
            姓名 -> unionId 的映射
        """
        print(f"\n👥 建立人员映射表...")
        
        # 收集所有需要查找的人员姓名
        user_names = set()
        for col, config in self.field_mapping.items():
            if config["type"] == "user":
                names = self.excel_df[col].dropna().astype(str).unique()
                user_names.update(names)
        
        if not user_names:
            print("   ℹ️ 没有人员字段需要处理")
            return {}
        
        print(f"   🔍 需要查找 {len(user_names)} 个用户")
        
        # 查询每个用户
        success_count = 0
        for name in tqdm(user_names, desc="查询用户"):
            try:
                result = self.client.get_operator_id_by_name(name)
                if result.get("success"):
                    self.user_mapping[name] = result["unionid"]
                    success_count += 1
                else:
                    print(f"   ⚠️ 未找到用户: {name}")
            except Exception as e:
                print(f"   ⚠️ 查询用户 {name} 失败: {str(e)}")
        
        print(f"   ✅ 成功映射 {success_count}/{len(user_names)} 个用户")
        return self.user_mapping
    
    def build_option_mapping(self) -> Dict[str, Dict]:
        """
        建立选项映射表
        
        Returns:
            字段 -> {值: 选项对象} 的映射
        """
        print(f"\n📋 建立选项映射表...")
        
        for col, config in self.field_mapping.items():
            if config["type"] == "singleSelect":
                options = config.get("options", [])
                # 构造选项对象列表（钉钉格式）
                option_objects = []
                for i, opt in enumerate(options):
                    option_objects.append({
                        "name": str(opt),
                        "color": self._get_option_color(i)  # 分配颜色
                    })
                self.option_mapping[col] = {opt: obj for opt, obj in zip(options, option_objects)}
                print(f"   📌 {col}: {len(options)} 个选项")
        
        return self.option_mapping
    
    def _get_option_color(self, index: int) -> str:
        """为选项分配颜色"""
        colors = [
            "blue", "green", "yellow", "red", "purple",
            "cyan", "orange", "pink", "gray", "teal"
        ]
        return colors[index % len(colors)]
    
    # ========== 阶段8: 创建缺失字段 ==========
    
    def create_missing_fields(self, to_create: List[Dict]):
        """
        创建缺失的字段
        
        Args:
            to_create: 需要创建的字段列表
        """
        if not to_create:
            print(f"\n✅ 所有字段已存在，无需创建")
            return
        
        print(f"\n🔧 创建缺失字段 ({len(to_create)} 个)...")
        
        for field_info in tqdm(to_create, desc="创建字段"):
            try:
                field_name = field_info["field_name"]
                field_type = field_info["field_type"]
                config = field_info["config"]
                
                # 构造字段属性
                property = None
                
                if field_type == "singleSelect":
                    # 选项字段
                    options = config.get("options", [])
                    property = {
                        "choices": [
                            {"name": str(opt), "color": self._get_option_color(i)}
                            for i, opt in enumerate(options)
                        ]
                    }
                
                elif field_type == "user":
                    # 人员字段默认多选
                    property = {"multiple": True}
                
                elif field_type == "date":
                    # 日期字段格式
                    property = {"formatter": "yyyy-MM-dd"}
                
                # 创建字段
                result = self.client.create_field(
                    self.base_id, self.sheet_name, self.operator_id,
                    field_name, field_type, property
                )
                
                self.stats["created_fields"].append(field_name)
                
            except Exception as e:
                error_msg = f"创建字段 {field_info['field_name']} 失败: {str(e)}"
                print(f"   ❌ {error_msg}")
                self.stats["errors"].append({
                    "type": "create_field",
                    "field": field_info["field_name"],
                    "error": str(e)
                })
        
        print(f"   ✅ 成功创建 {len(self.stats['created_fields'])} 个字段")
    
    # ========== 阶段9: 数据转换与导入 ==========
    
    def transform_and_import(self):
        """数据转换并批量导入"""
        print(f"\n🚀 开始数据导入...")
        print(f"   总数据量: {self.stats['total_rows']} 行")
        print(f"   批次大小: {BATCH_SIZE} 行")
        
        total_batches = (self.stats["total_rows"] + BATCH_SIZE - 1) // BATCH_SIZE
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min((batch_idx + 1) * BATCH_SIZE, self.stats["total_rows"])
            
            print(f"\n   📦 批次 {batch_idx + 1}/{total_batches} (行 {start_idx + 1}-{end_idx})")
            
            batch_df = self.excel_df.iloc[start_idx:end_idx]
            records = []
            
            for _, row in batch_df.iterrows():
                record = self._transform_single_record(row)
                records.append(record)
            
            # 批量导入
            try:
                result = self.client.add_records(
                    self.base_id, self.sheet_name, self.operator_id, records
                )
                self.stats["success_count"] += len(records)
                print(f"   ✅ 成功导入 {len(records)} 条记录")
                
            except Exception as e:
                error_msg = f"批次 {batch_idx + 1} 导入失败: {str(e)}"
                print(f"   ❌ {error_msg}")
                self.stats["error_count"] += len(records)
                self.stats["errors"].append({
                    "type": "import",
                    "batch": batch_idx + 1,
                    "range": f"{start_idx + 1}-{end_idx}",
                    "error": str(e)
                })
        
        print(f"\n📊 导入完成:")
        print(f"   ✅ 成功: {self.stats['success_count']} 条")
        print(f"   ❌ 失败: {self.stats['error_count']} 条")
    
    def _transform_single_record(self, row: pd.Series) -> Dict[str, Any]:
        """转换单行记录"""
        record = {}
        
        for col, config in self.field_mapping.items():
            value = row.get(col)
            
            if pd.isna(value):
                continue
            
            field_type = config["type"]
            target_field = config["target_field"]
            
            if field_type == "user":
                # 人员字段：转换姓名 -> unionId对象
                user_names = str(value).split(",")  # 支持多个人员
                user_objects = []
                for name in user_names:
                    name = name.strip()
                    unionid = self.user_mapping.get(name)
                    if unionid:
                        user_objects.append({"unionId": unionid})
                
                if user_objects:
                    record[target_field] = user_objects
                
                # 保留原始值
                import_field = config.get("target_field_import")
                if import_field:
                    record[import_field] = str(value)
            
            elif field_type == "date":
                # 日期字段：转换为时间戳
                try:
                    dt = pd.to_datetime(value)
                    timestamp = int(dt.timestamp() * 1000)  # 毫秒时间戳
                    record[target_field] = timestamp
                except:
                    pass
                
                # 保留原始值
                original_field = config.get("target_field_original")
                if original_field:
                    record[original_field] = str(value)
            
            elif field_type == "singleSelect":
                # 选项字段：直接使用选项名称字符串（钉钉API格式）
                # 也可以使用选项ID字符串，但名称更直观
                record[target_field] = str(value)
            
            elif field_type == "attachment":
                # 附件字段：上传文件并转换
                # 先进行路径映射转换
                file_paths_str = str(value)
                for win_path, linux_path in self.path_mappings.items():
                    file_paths_str = file_paths_str.replace(win_path, linux_path)
                
                file_paths = file_paths_str.split(ATTACHMENT_DELIMITER)
                attachments = []
                
                for file_path in file_paths:
                    file_path = file_path.strip()
                    if os.path.exists(file_path):
                        try:
                            attachment = self.client.upload_attachment(
                                self.operator_id, file_path
                            )
                            attachments.append(attachment)
                        except Exception as e:
                            print(f"   ⚠️ 上传附件失败 {file_path}: {str(e)}")
                    else:
                        print(f"   ⚠️ 附件文件不存在: {file_path}")
                
                if attachments:
                    record[target_field] = attachments
            
            else:
                # 其他类型：直接使用原值
                record[target_field] = value
        
        # 添加导入ID
        record[IMPORT_ID_FIELD] = row.get(IMPORT_ID_FIELD)
        
        return record
    
    def _convert_path(self, windows_path: str) -> str:
        """
        转换Windows路径为Linux路径
        
        示例:
            C:/Users/xxx/file.jpg -> /workspace/attachments/file.jpg
        """
        linux_path = windows_path
        for win_prefix, linux_prefix in self.path_mappings.items():
            linux_path = linux_path.replace(win_prefix, linux_prefix)
        return linux_path
    
    # ========== 阶段10: 生成报告 ==========
    
    def generate_report(self, output_dir: str = "."):
        """
        生成导入报告
        
        Args:
            output_dir: 报告输出目录
        """
        print(f"\n📝 生成导入报告...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存映射表
        mapping_file = os.path.join(output_dir, f"mapping_{self.import_session_id}_{timestamp}.json")
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump({
                "session_id": self.import_session_id,
                "field_mapping": self.field_mapping,
                "user_mapping": self.user_mapping,
                "option_mapping": self.option_mapping
            }, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 映射表已保存: {mapping_file}")
        
        # 2. 保存错误报告（如果有）
        if self.stats["errors"]:
            error_file = os.path.join(output_dir, f"errors_{self.import_session_id}_{timestamp}.json")
            with open(error_file, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": self.import_session_id,
                    "stats": self.stats,
                    "errors": self.stats["errors"]
                }, f, ensure_ascii=False, indent=2)
            print(f"   ⚠️ 错误报告已保存: {error_file}")
        
        # 3. 打印总结
        print(f"\n{'='*60}")
        print(f"📊 导入总结")
        print('='*60)
        print(f"   会话ID: {self.import_session_id}")
        print(f"   总数据: {self.stats['total_rows']} 行")
        print(f"   成功: {self.stats['success_count']} 行")
        print(f"   失败: {self.stats['error_count']} 行")
        print(f"   新建字段: {len(self.stats['created_fields'])} 个")
        print('='*60)


def main():
    parser = argparse.ArgumentParser(description="钉钉AI表格智能导入")
    parser.add_argument("--app-key", help="钉钉应用Client ID（可选，也可通过环境变量配置）")
    parser.add_argument("--app-secret", help="钉钉应用Client Secret（可选，也可通过环境变量配置）")
    parser.add_argument("--base-id", required=True, help="AI表格ID")
    parser.add_argument("--sheet-name", required=True, help="数据表名称")
    parser.add_argument("--operator-id", required=True, help="操作人的unionId")
    parser.add_argument("--excel-file", required=True, help="Excel文件路径")
    parser.add_argument("--output-dir", default=".", help="报告输出目录")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式（不实际导入）")
    parser.add_argument("--path-mappings", help="路径映射规则，JSON格式，如：{\"C:/Users/xxx\":\"/workspace/xxx\"}")
    
    args = parser.parse_args()
    
    # 解析路径映射
    path_mappings = {}
    if args.path_mappings:
        try:
            path_mappings = json.loads(args.path_mappings)
            print(f"✅ 路径映射规则已加载: {path_mappings}")
        except json.JSONDecodeError as e:
            print(f"⚠️ 路径映射解析失败: {str(e)}")
    
    # 获取凭证并创建客户端
    try:
        credentials = get_credentials(args.app_key, args.app_secret)
        client = DingTalkAIClient(credentials["app_key"], credentials["app_secret"])
        print(f"✅ 客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {str(e)}")
        sys.exit(1)
    
    # 创建导入器
    importer = SmartImporter(client, args.base_id, args.sheet_name, args.operator_id, path_mappings)
    
    try:
        # 阶段1: 读取Excel
        importer.load_excel(args.excel_file)
        
        # 阶段2: 推断字段类型
        inferred_types = importer.infer_field_types()
        
        # 阶段3: 确认字段映射
        importer.confirm_field_mapping(inferred_types)
        
        # 阶段5: 获取现有字段
        importer.load_existing_fields()
        
        # 阶段6: 分析字段差异
        to_create, _ = importer.analyze_field_diff()
        
        # 阶段7: 建立映射表
        importer.build_user_mapping()
        importer.build_option_mapping()
        
        if args.dry_run:
            print("\n🚧 试运行模式，跳过实际导入")
            return
        
        # 阶段8: 创建缺失字段
        importer.create_missing_fields(to_create)
        
        # 阶段9: 数据转换与导入
        importer.transform_and_import()
        
        # 阶段10: 生成报告
        importer.generate_report(args.output_dir)
        
        print("\n✅ 智能导入完成!")
        
    except Exception as e:
        print(f"\n❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
