"""宠物宝 (PetCare) — 宠物健康计算器 API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import urllib.request, json, os, yaml

router = APIRouter(prefix="/health", tags=["健康计算器"])


class HealthRequest(BaseModel):
    breed: str           # 品种名
    species: str         # 猫/狗
    size: Optional[str] = "中型"  # 小型/中型/大型
    age_months: int      # 月龄
    weight_kg: float     # 当前体重(kg)
    food_brand: Optional[str] = ""   # 主粮品牌
    food_protein: Optional[float] = 0  # 主粮蛋白质%
    food_calcium: Optional[float] = 0  # 主粮钙含量%


# ── 推荐算法 ──

def calc_calcium_needs(weight_kg, age_months, size, species):
    """计算每日钙推荐摄入量 (mg)"""
    # 基础需求 (mg/kg/day) — 参考 NRC 犬猫营养标准
    if species == "狗":
        if age_months < 6:
            base = 320  # 幼犬高速生长期
        elif age_months < 12:
            base = 250
        elif age_months < 24:
            base = 150  # 大型犬生长期更长
        else:
            base = 100  # 成年维持
    else:  # 猫
        if age_months < 6:
            base = 260
        elif age_months < 12:
            base = 200
        else:
            base = 120

    # 体型系数
    if size == "大型":
        base *= 1.2
    elif size == "小型":
        base *= 0.9

    return round(base * weight_kg, 0)


def calc_joint_needs(weight_kg, age_months, size, species, breed=""):
    """计算关节保护成分推荐摄入量"""
    needs = {
        "glucosamine_mg": 0,
        "chondroitin_mg": 0,
        "priority": "none",  # none/low/medium/high/critical
    }

    # 仅对犬做关节推荐（猫关节问题较少）
    if species == "猫" and size != "大型":
        return needs

    # 基础剂量 (mg/kg/day)
    if size == "大型":
        base_gluco = 30
        base_chon = 15
    elif size == "中型":
        base_gluco = 20
        base_chon = 10
    else:
        base_gluco = 15
        base_chon = 8

    needs["glucosamine_mg"] = round(base_gluco * weight_kg, 0)
    needs["chondroitin_mg"] = round(base_chon * weight_kg, 0)

    # 优先级判定
    if size == "大型" and age_months > 60:
        needs["priority"] = "critical"  # 大型犬老年
    elif size == "大型" and age_months > 36:
        needs["priority"] = "high"
    elif size in ("大型", "中型") and age_months > 24:
        needs["priority"] = "medium"
    elif size == "大型":
        needs["priority"] = "medium"  # 大型犬任何年龄都建议
    else:
        needs["priority"] = "low"

    # 短腿犬（柯基、腊肠、巴吉度等）额外提升
    short_leg_breeds = ["柯基", "腊肠", "巴吉度", "法斗", "英斗", "贵宾", "泰迪", "博美", "吉娃娃"]
    if breed and any(b in breed for b in short_leg_breeds):
        needs["priority"] = "high" if needs["priority"] in ("none", "low", "medium") else "critical"
        needs["glucosamine_mg"] = round(needs["glucosamine_mg"] * 1.3, 0)
        needs["chondroitin_mg"] = round(needs["chondroitin_mg"] * 1.3, 0)

    return needs


def calc_growth_curve(weight_kg, age_months, size, species):
    """生成体重成长曲线数据点"""
    points = []

    # 估算成年体重
    if size == "大型":
        adult_weight = weight_kg * 2.5 if age_months < 12 else weight_kg * 1.3
    elif size == "中型":
        adult_weight = weight_kg * 1.8 if age_months < 12 else weight_kg * 1.1
    else:
        adult_weight = weight_kg * 1.3 if age_months < 8 else weight_kg * 1.05

    adult_weight = round(adult_weight, 1)

    # 生成从出生到 24 个月的曲线
    max_months = 24 if species == "狗" else 18
    for m in range(0, max_months + 1, 1):
        if m == 0:
            w = adult_weight * 0.05  # 出生体重约成年 5%
        elif m <= age_months:
            # 已过去的时间：线性插值
            progress = m / max(age_months, 1)
            # 生长曲线：前期快后期慢（logistic 近似）
            w = adult_weight * (1 / (1 + 4 * (2.718 ** (-0.3 * m))))
            # 调整到当前体重匹配
            if m == age_months:
                w = weight_kg
        else:
            # 未来预测
            w = adult_weight * (1 / (1 + 4 * (2.718 ** (-0.3 * m))))

        points.append({
            "month": m,
            "weight": round(w, 2),
            "is_current": m == age_months,
            "is_future": m > age_months,
        })

    return {
        "points": points,
        "estimated_adult_weight": adult_weight,
    }


# ── AI 推荐 ──

def get_ark_key():
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config.get("model", {}).get("api_key", "")
    except Exception:
        return ""


def ai_recommend(breed, species, age_months, weight_kg, size, calcium, joint):
    """调用 AI 生成个性化推荐"""
    key = get_ark_key()
    if not key:
        return None

    prompt = f"""你是宠物营养专家。根据以下信息给出个性化建议：

品种：{breed}（{species}，{size}型）
月龄：{age_months}个月
体重：{weight_kg}kg
推荐每日钙摄入：{calcium}mg
关节保护需求：{joint['priority']}（葡萄糖胺{joint['glucosamine_mg']}mg/软骨素{joint['chondroitin_mg']}mg）

请用中文简洁回答（200字以内）：
1. 当前阶段的核心营养建议
2. 钙和关节保护补充的注意事项
3. 适合的主粮类型推荐"""

    body = json.dumps({
        "model": "deepseek-v4-flash-260425",
        "messages": [
            {"role": "system", "content": "你是宠物营养专家，回答简洁实用。"},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.7,
    }).encode()

    try:
        r = urllib.request.Request(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(r, timeout=20) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception:
        return None


# ── API 端点 ──

@router.post("/calculate")
async def calculate(req: HealthRequest):
    if req.age_months < 0 or req.weight_kg <= 0:
        raise HTTPException(400, "月龄和体重必须大于0")

    calcium = calc_calcium_needs(req.weight_kg, req.age_months, req.size, req.species)
    joint = calc_joint_needs(req.weight_kg, req.age_months, req.size, req.species, req.breed)
    growth = calc_growth_curve(req.weight_kg, req.age_months, req.size, req.species)

    # AI 推荐
    ai_advice = ai_recommend(
        req.breed, req.species, req.age_months,
        req.weight_kg, req.size, calcium, joint
    )

    return {
        "code": 0,
        "data": {
            "calcium_mg_per_day": calcium,
            "joint": joint,
            "growth_curve": growth,
            "ai_advice": ai_advice,
        },
    }
