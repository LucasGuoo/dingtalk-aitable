#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
附件上传功能测试脚本

测试钉钉AI表格附件上传的完整流程：
1. 获取上传信息
2. 上传文件到OSS
3. 将附件关联到记录

使用方法:
    python test_attachment_upload.py --base-id xxx --sheet-name xxx --operator-id xxx --file-path ./test.jpg

配置:
    需要设置环境变量 COZE_DINGTALK_AI_TABLE_7611716228092264482
    格式: {"app_key": "xxx", "app_secret": "xxx"}
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dingtalk_api_client import DingTalkAIClient, get_credentials


def test_single_upload(client: DingTalkAIClient, operator_id: str, file_path: str):
    """测试单文件上传"""
    print(f"\n{'='*60}")
    print(f"测试单文件上传: {file_path}")
    print('='*60)
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    try:
        print(f"文件大小: {os.path.getsize(file_path)} bytes")
        print("开始上传...")
        
        attachment = client.upload_attachment(operator_id, file_path)
        
        print(f"✅ 上传成功!")
        print(f"   文件名: {attachment['filename']}")
        print(f"   文件大小: {attachment['size']} bytes")
        print(f"   文件类型: {attachment['type']}")
        print(f"   ResourceId: {attachment['resourceId']}")
        print(f"   ResourceUrl: {attachment['url']}")
        
        return attachment
        
    except Exception as e:
        print(f"❌ 上传失败: {str(e)}")
        return None


def test_batch_upload(client: DingTalkAIClient, operator_id: str, file_paths: list):
    """测试批量上传"""
    print(f"\n{'='*60}")
    print(f"测试批量上传: {len(file_paths)} 个文件")
    print('='*60)
    
    valid_paths = [p for p in file_paths if os.path.exists(p)]
    invalid_paths = [p for p in file_paths if not os.path.exists(p)]
    
    if invalid_paths:
        print(f"⚠️ 以下文件不存在，将跳过: {invalid_paths}")
    
    if not valid_paths:
        print("❌ 没有有效的文件可上传")
        return []
    
    try:
        print(f"开始上传 {len(valid_paths)} 个文件...")
        attachments = client.upload_attachments(operator_id, valid_paths)
        
        print(f"✅ 批量上传完成!")
        print(f"   成功: {len(attachments)}/{len(valid_paths)}")
        
        for i, att in enumerate(attachments, 1):
            print(f"   [{i}] {att['filename']} ({att['size']} bytes)")
        
        return attachments
        
    except Exception as e:
        print(f"❌ 批量上传失败: {str(e)}")
        return []


def test_create_record_with_attachment(client: DingTalkAIClient, base_id: str, 
                                       sheet_name: str, operator_id: str,
                                       attachment: dict):
    """测试创建带附件的记录"""
    print(f"\n{'='*60}")
    print(f"测试创建带附件的记录")
    print('='*60)
    
    # 构造记录数据
    record_data = {
        "标题": f"附件测试-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "附件字段": [attachment]  # 附件必须是数组
    }
    
    try:
        print(f"记录数据: {json.dumps(record_data, ensure_ascii=False, indent=2)}")
        print("创建记录...")
        
        result = client.add_records(base_id, sheet_name, operator_id, [record_data])
        
        print(f"✅ 记录创建成功!")
        print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"❌ 创建记录失败: {str(e)}")
        return None


def test_create_record_with_multiple_attachments(client: DingTalkAIClient, base_id: str,
                                                 sheet_name: str, operator_id: str,
                                                 attachments: list):
    """测试创建带多个附件的记录"""
    print(f"\n{'='*60}")
    print(f"测试创建带多个附件的记录 ({len(attachments)} 个附件)")
    print('='*60)
    
    record_data = {
        "标题": f"多附件测试-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "附件字段": attachments  # 多个附件
    }
    
    try:
        print(f"记录数据: {json.dumps(record_data, ensure_ascii=False, indent=2)}")
        print("创建记录...")
        
        result = client.add_records(base_id, sheet_name, operator_id, [record_data])
        
        print(f"✅ 记录创建成功!")
        print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"❌ 创建记录失败: {str(e)}")
        return None


def create_test_files():
    """创建测试文件"""
    test_files = []
    
    # 创建测试文本文件
    txt_path = "/tmp/test_attachment.txt"
    with open(txt_path, "w") as f:
        f.write("这是附件上传测试文件\n生成时间: " + datetime.now().isoformat())
    test_files.append(txt_path)
    print(f"✅ 创建测试文件: {txt_path}")
    
    # 创建测试JSON文件
    json_path = "/tmp/test_attachment.json"
    with open(json_path, "w") as f:
        json.dump({"test": True, "timestamp": datetime.now().isoformat()}, f)
    test_files.append(json_path)
    print(f"✅ 创建测试文件: {json_path}")
    
    return test_files


def main():
    parser = argparse.ArgumentParser(description="附件上传功能测试")
    parser.add_argument("--base-id", help="AI表格ID（测试写入记录时需要）")
    parser.add_argument("--sheet-name", help="数据表名称（测试写入记录时需要）")
    parser.add_argument("--operator-id", required=True, help="操作人的unionId")
    parser.add_argument("--file-path", help="单个测试文件路径")
    parser.add_argument("--file-paths", help="多个测试文件路径，分号分隔")
    parser.add_argument("--create-test-files", action="store_true", help="自动创建测试文件")
    parser.add_argument("--test-write-record", action="store_true", help="测试写入记录")
    
    args = parser.parse_args()
    
    # 获取凭证并创建客户端
    try:
        credentials = get_credentials()
        client = DingTalkAIClient(credentials["app_key"], credentials["app_secret"])
        print(f"✅ 客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {str(e)}")
        sys.exit(1)
    
    # 准备测试文件
    test_files = []
    
    if args.create_test_files:
        test_files = create_test_files()
    
    if args.file_path:
        test_files.append(args.file_path)
    
    if args.file_paths:
        test_files.extend([p.strip() for p in args.file_paths.split(";") if p.strip()])
    
    if not test_files:
        print("⚠️ 没有指定测试文件，使用 --create-test-files 自动创建或使用 --file-path 指定")
        sys.exit(1)
    
    print(f"\n📋 测试文件列表:")
    for i, f in enumerate(test_files, 1):
        exists = "✅" if os.path.exists(f) else "❌"
        print(f"   [{i}] {exists} {f}")
    
    # 执行测试
    uploaded_attachments = []
    
    # 测试1：单文件上传
    if len(test_files) == 1:
        attachment = test_single_upload(client, args.operator_id, test_files[0])
        if attachment:
            uploaded_attachments.append(attachment)
    
    # 测试2：批量上传
    else:
        attachments = test_batch_upload(client, args.operator_id, test_files)
        uploaded_attachments.extend(attachments)
    
    # 测试3：写入记录（如果提供了base-id和sheet-name）
    if args.test_write_record and args.base_id and args.sheet_name:
        if len(uploaded_attachments) == 1:
            test_create_record_with_attachment(
                client, args.base_id, args.sheet_name, 
                args.operator_id, uploaded_attachments[0]
            )
        elif len(uploaded_attachments) > 1:
            test_create_record_with_multiple_attachments(
                client, args.base_id, args.sheet_name,
                args.operator_id, uploaded_attachments
            )
    elif args.test_write_record:
        print("\n⚠️ 测试写入记录需要提供 --base-id 和 --sheet-name")
    
    # 清理测试文件
    if args.create_test_files:
        print(f"\n🧹 清理测试文件...")
        for f in test_files:
            try:
                os.remove(f)
                print(f"   已删除: {f}")
            except:
                pass
    
    print(f"\n{'='*60}")
    print("测试完成!")
    print('='*60)


if __name__ == "__main__":
    main()
