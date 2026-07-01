"""智能提醒规则引擎 - 根据宠物品种和年龄自动生成日程提醒"""
from datetime import date, datetime
from typing import List, Dict, Optional
from enum import Enum


class AgeCategory(str, Enum):
    """宠物年龄分类"""
    BABY = "幼崽"  # 0-6个月
    YOUNG = "幼年"  # 6-12个月
    ADULT = "成年"  # 1-7岁
    SENIOR = "老年"  # 7岁以上


class Species(str, Enum):
    """宠物品类"""
    DOG = "狗"
    CAT = "猫"


def calculate_age_months(birthday: date) -> int:
    """计算宠物的月龄"""
    today = date.today()
    months = (today.year - birthday.year) * 12 + (today.month - birthday.month)
    # 如果还没到本月生日，减1个月
    if today.day < birthday.day:
        months -= 1
    return max(0, months)


def get_age_category(birthday: date, species: str = Species.DOG) -> AgeCategory:
    """根据生日和品种判断年龄分类"""
    months = calculate_age_months(birthday)
    
    if months < 6:
        return AgeCategory.BABY
    elif months < 12:
        return AgeCategory.YOUNG
    elif months < 84:  # 7岁
        return AgeCategory.ADULT
    else:
        return AgeCategory.SENIOR


def generate_default_reminders(
    pet_name: str,
    birthday: Optional[date],
    species: str,
    age: Optional[str] = None
) -> List[Dict]:
    """
    根据宠物信息生成默认提醒列表
    
    返回格式: [{"schedule_type": str, "title": str, "interval_days": int, "note": str}, ...]
    """
    reminders = []
    
    # 如果没有生日，尝试从 age 字段解析
    if not birthday and age:
        # 尝试解析 "2岁" 或 "3个月" 格式
        age_lower = age.lower().strip()
        if "岁" in age_lower:
            try:
                years = int(age_lower.replace("岁", ""))
                # 估算生日为 years 年前的今天
                today = date.today()
                birthday = date(today.year - years, today.month, today.day)
            except:
                pass
        elif "月" in age_lower:
            try:
                months = int(age_lower.replace("个月", "").replace("月", ""))
                # 估算生日
                today = date.today()
                if today.month > months:
                    birthday = date(today.year, today.month - months, today.day)
                else:
                    birthday = date(today.year - 1, 12 + today.month - months, today.day)
            except:
                pass
    
    # 如果还是没有生日，使用默认的成年犬/猫提醒
    if not birthday:
        return _generate_adult_reminders(pet_name, species)
    
    # 根据年龄分类生成提醒
    category = get_age_category(birthday, species)
    age_months = calculate_age_months(birthday)
    
    if category == AgeCategory.BABY:
        reminders = _generate_baby_reminders(pet_name, species, age_months)
    elif category == AgeCategory.YOUNG:
        reminders = _generate_young_reminders(pet_name, species, age_months)
    elif category == AgeCategory.ADULT:
        reminders = _generate_adult_reminders(pet_name, species)
    else:
        reminders = _generate_senior_reminders(pet_name, species)
    
    return reminders


def _generate_baby_reminders(pet_name: str, species: str, age_months: int) -> List[Dict]:
    """幼崽提醒 (0-6个月)"""
    reminders = []
    
    if species == Species.DOG or species == "狗":
        # 疫苗 - 幼犬需要多剂
        reminders.append({
            "schedule_type": "疫苗",
            "title": "犬四联疫苗 #1",
            "interval_days": 28,  # 4周后第二针
            "note": "首次接种，4周后需要第二针"
        })
        
        # 驱虫
        reminders.append({
            "schedule_type": "体内驱虫",
            "title": "体内驱虫",
            "interval_days": 14,  # 幼犬每2周一次
            "note": "幼犬期每2周一次，6个月后改为每月一次"
        })
        reminders.append({
            "schedule_type": "体外驱虫",
            "title": "体外驱虫",
            "interval_days": 30,
            "note": "每月一次，滴剂/喷剂"
        })
        
        # 体检
        reminders.append({
            "schedule_type": "体检",
            "title": "幼犬健康检查",
            "interval_days": 30,  # 每月一次
            "note": "幼犬期每月检查发育情况"
        })
        
    else:  # CAT
        reminders.append({
            "schedule_type": "疫苗",
            "title": "猫三联疫苗 #1",
            "interval_days": 28,
            "note": "首次接种，4周后需要第二针"
        })
        
        reminders.append({
            "schedule_type": "体内驱虫",
            "title": "体内驱虫",
            "interval_days": 14,
            "note": "幼猫期每2周一次，6个月后改为每月一次"
        })
        reminders.append({
            "schedule_type": "体外驱虫",
            "title": "体外驱虫",
            "interval_days": 30,
            "note": "每月一次，滴剂/喷剂"
        })
        
        reminders.append({
            "schedule_type": "体检",
            "title": "幼猫健康检查",
            "interval_days": 30,
            "note": "幼猫期每月检查发育情况"
        })
    
    return reminders


def _generate_young_reminders(pet_name: str, species: str, age_months: int) -> List[Dict]:
    """幼年提醒 (6-12个月)"""
    reminders = []
    
    if species == Species.DOG or species == "狗":
        # 疫苗加强针
        reminders.append({
            "schedule_type": "疫苗",
            "title": "疫苗加强针",
            "interval_days": 28,  # 可能需要第二针加强
            "note": "幼年阶段疫苗加强针"
        })
        
        # 驱虫
        reminders.append({
            "schedule_type": "体内驱虫",
            "title": "体内驱虫",
            "interval_days": 30,  # 过渡期每月一次
            "note": "幼年阶段每月一次，1岁后改为每3个月"
        })
        reminders.append({
            "schedule_type": "体外驱虫",
            "title": "体外驱虫",
            "interval_days": 30,
            "note": "每月一次"
        })
        
        # 体检
        reminders.append({
            "schedule_type": "体检",
            "title": "健康检查",
            "interval_days": 90,  # 每3个月
            "note": "幼年阶段每3个月检查一次"
        })
        
    else:  # CAT
        reminders.append({
            "schedule_type": "疫苗",
            "title": "疫苗加强针",
            "interval_days": 28,
            "note": "幼年阶段疫苗加强针"
        })
        
        reminders.append({
            "schedule_type": "体内驱虫",
            "title": "体内驱虫",
            "interval_days": 30,
            "note": "幼年阶段每月一次，1岁后改为每3个月"
        })
        reminders.append({
            "schedule_type": "体外驱虫",
            "title": "体外驱虫",
            "interval_days": 30,
            "note": "每月一次"
        })
        
        reminders.append({
            "schedule_type": "体检",
            "title": "健康检查",
            "interval_days": 90,
            "note": "幼年阶段每3个月检查一次"
        })
    
    return reminders


def _generate_adult_reminders(pet_name: str, species: str) -> List[Dict]:
    """成年提醒 (1-7岁)"""
    reminders = []
    
    # 疫苗 - 成年期每年一次
    reminders.append({
        "schedule_type": "疫苗",
        "title": "年度疫苗接种",
        "interval_days": 365,
        "note": "每年一次，建议提前预约"
    })
    
    # 驱虫
    reminders.append({
        "schedule_type": "体内驱虫",
        "title": "体内驱虫",
        "interval_days": 90,  # 每3个月
        "note": "成年期每3个月一次"
    })
    reminders.append({
        "schedule_type": "体外驱虫",
        "title": "体外驱虫",
        "interval_days": 30,
        "note": "每月一次，滴剂/喷剂"
    })
    
    # 体检
    reminders.append({
        "schedule_type": "体检",
        "title": "年度体检",
        "interval_days": 180,  # 每6个月
        "note": "成年期每半年一次，血常规+生化"
    })
    
    return reminders


def _generate_senior_reminders(pet_name: str, species: str) -> List[Dict]:
    """老年提醒 (7岁以上)"""
    reminders = []
    
    # 疫苗 - 老年期可能需要调整
    reminders.append({
        "schedule_type": "疫苗",
        "title": "年度疫苗接种",
        "interval_days": 365,
        "note": "老年期每年一次，可根据兽医建议调整"
    })
    
    # 驱虫
    reminders.append({
        "schedule_type": "体内驱虫",
        "title": "体内驱虫",
        "interval_days": 90,
        "note": "老年期每3个月一次"
    })
    reminders.append({
        "schedule_type": "体外驱虫",
        "title": "体外驱虫",
        "interval_days": 30,
        "note": "每月一次"
    })
    
    # 体检 - 老年期需要更频繁
    reminders.append({
        "schedule_type": "体检",
        "title": "老年健康体检",
        "interval_days": 90,  # 每3个月
        "note": "老年期每3个月一次，重点关注心肝肾功能和关节"
    })
    
    # 牙齿护理 - 老年期特别重要
    reminders.append({
        "schedule_type": "牙齿护理",
        "title": "牙齿检查与清洁",
        "interval_days": 180,  # 每6个月
        "note": "老年期易患牙周病，建议每半年检查一次"
    })
    
    return reminders


def get_age_category_display(birthday: Optional[date], species: str = "狗") -> Optional[str]:
    """获取年龄分类的显示文本"""
    if not birthday:
        return None
    category = get_age_category(birthday, species)
    return category.value
