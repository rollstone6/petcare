#!/usr/bin/env python3
"""健康标签功能端到端测试"""
import requests
import json

BASE = "http://127.0.0.1:8000/api"

def test():
    print("=" * 60)
    print("🧪 健康标签功能测试")
    print("=" * 60)
    
    # 1. 登录
    print("\n1️⃣  登录获取 token...")
    r = requests.post(BASE + "/auth/login", json={"username": "testcat", "password": "test123"})
    if r.status_code != 200:
        print("   ❌ 登录失败:", r.text)
        return
    token = r.json()["data"]["token"]
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    print("   ✅ 登录成功")
    
    # 2. 获取品种列表
    print("\n2️⃣  获取猫品种...")
    r = requests.get(BASE + "/breeds", headers=headers)
    breeds = r.json()["data"]["items"]
    cat_breed = next((b for b in breeds if "猫" in b.get("species", "")), None)
    print("   ✅ 找到猫品种:", cat_breed["name"], "(ID=" + str(cat_breed["id"]) + ")")
    
    # 3. 创建宠物
    print("\n3️⃣  创建测试宠物...")
    r = requests.post(BASE + "/pets", headers=headers, json={
        "pet_name": "测试猫咪",
        "breed_id": cat_breed["id"],
        "gender": "母",
        "weight": 4.5,
        "body_condition": "chubby"
    })
    pet_data = r.json()["data"]
    pet_id = pet_data["id"]
    print("   ✅ 创建成功:", pet_data["pet_name"], "(ID=" + str(pet_id) + ")")
    
    # 4. 获取宠物列表
    print("\n4️⃣  获取宠物列表...")
    r = requests.get(BASE + "/pets", headers=headers)
    pets = r.json()["data"]["items"]
    print("   共", len(pets), "只宠物:")
    for p in pets:
        tags = p.get("health_tags", [])
        print("   -", p["pet_name"], "(ID=" + str(p["id"]) + ") 健康标签:", tags)
    
    # 5. 获取可用健康标签
    print("\n5️⃣  获取可用健康标签...")
    r = requests.get(BASE + "/health-tags", headers=headers)
    tags_data = r.json()["data"]
    all_tags = tags_data["tags"]
    categories = tags_data["categories"]
    print("   共", len(all_tags), "个标签，", len(categories), "个分类:")
    for cat, tags in categories.items():
        print("   -", cat + ":", len(tags), "个")
    
    # 6. 更新宠物的健康标签
    test_tags = ["obesity_mild", "stomach_sensitive", "allergy_chicken"]
    print("\n6️⃣  为宠物设置健康标签:", test_tags)
    r = requests.put(BASE + "/health-tags/pets/" + str(pet_id),
                     headers=headers,
                     json={"tags": test_tags})
    print("  ", r.json()["message"])
    
    # 7. 验证更新
    print("\n7️⃣  验证更新...")
    r = requests.get(BASE + "/pets", headers=headers)
    pets = r.json()["data"]["items"]
    updated_pet = [p for p in pets if p["id"] == pet_id][0]
    print("  ", updated_pet["pet_name"], "的健康标签:", updated_pet["health_tags"])
    
    # 8. 获取产品列表
    print("\n8️⃣  获取产品列表...")
    r = requests.get(BASE + "/products?limit=5", headers=headers)
    products = r.json()["data"]["items"]
    print("   前 5 个产品:")
    for prod in products:
        print("   -", prod["name"], "(ID=" + str(prod["id"]) + ", 类型=" + prod["type"] + ")")
    
    # 9. 检查产品警告
    if products:
        test_product = products[0]
        print("\n9️⃣  检查产品 [" + test_product["name"] + "] 的健康警告...")
        r = requests.post(BASE + "/health-tags/check/" + str(test_product["id"]), headers=headers)
        warnings = r.json()["data"]["warnings"]
        
        if warnings:
            print("   ⚠️  发现", len(warnings), "条警告:")
            severity_icons = {"high": "🚨", "medium": "⚠️", "low": "💡", "info": "✨"}
            for w in warnings:
                icon = severity_icons.get(w["severity"], "•")
                print("  ", icon, "[" + w["severity"] + "]", w["pet_name"] + ":", w["message"][:60] + "...")
        else:
            print("   ✅ 无警告")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test()
