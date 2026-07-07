#!/usr/bin/env python3
"""
测试 VLM 配料表解析器

用法：
    python3 test_vlm_parser.py [sku_id]

示例：
    python3 test_vlm_parser.py 100012043978
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# 添加 backend 到 Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.crawler.jd_vlm_ingredient_parser import IngredientProcessor


async def test_single_product(sku_id: str):
    """测试单个商品的 VLM 解析"""
    print(f"\n{'='*60}")
    print(f"测试商品: {sku_id}")
    print(f"{'='*60}\n")
    
    # API key 自动从 ~/.hermes/config.yaml 或 ARK_API_KEY 环境变量加载
    # 无需手动设置
    
    # 创建处理器
    processor = IngredientProcessor()
    
    # 处理商品
    try:
        result = await processor.process_product(sku_id)
        
        if result:
            print(f"\n✅ 解析成功！")
            print(f"\n📦 配料表数据:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 统计
            ingredients = result.get("ingredients", [])
            additives = result.get("additives", [])
            analysis = result.get("guaranteed_analysis", {})
            
            print(f"\n📊 统计:")
            print(f"   原料数量: {len(ingredients)}")
            print(f"   添加剂数量: {len(additives)}")
            print(f"   营养分析字段: {len(analysis)}")
            
            if ingredients:
                print(f"\n🥩 主要原料 (前5个):")
                for i, name in enumerate(ingredients[:5], 1):
                    print(f"   {i}. {name}")
            
            return result
        else:
            print(f"\n❌ 解析失败: 未能从图片中提取配料表")
            return None
            
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_batch_from_database():
    """从数据库中获取商品列表进行批量测试"""
    from app.database import SessionLocal
    from app import models
    
    db = SessionLocal()
    
    # 获取浙大动物医院的产品（之前导入的138个）
    products = db.query(models.Product).filter(
        models.Product.approval_number.like("JD:%")
    ).limit(10).all()
    
    print(f"\n📦 从数据库获取 {len(products)} 个商品进行测试")
    
    success_count = 0
    results = []
    
    for product in products:
        sku_id = product.approval_number.replace("JD:", "")
        print(f"\n[{success_count+1}/{len(products)}] {product.name} (SKU: {sku_id})")
        
        result = await test_single_product(sku_id)
        if result:
            success_count += 1
            results.append({
                "product_id": product.id,
                "sku_id": sku_id,
                "name": product.name,
                "data": result
            })
    
    db.close()
    
    print(f"\n{'='*60}")
    print(f"📊 批量测试完成: {success_count}/{len(products)} 成功")
    print(f"{'='*60}")
    
    # 保存结果
    if results:
        output_file = Path("/root/workspace/petcare/data/vlm_test_results.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存到: {output_file}")
    
    return results


async def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 测试单个商品
        sku_id = sys.argv[1]
        await test_single_product(sku_id)
    else:
        # 批量测试
        await test_batch_from_database()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    
    asyncio.run(main())
