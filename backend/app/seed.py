"""宠物宝 (PetCare) — 种子数据脚本"""
from app.database import SessionLocal, engine, Base
from app import models

# 重建所有表
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ============================================================
# 1. 品牌
# ============================================================
brands_data = [
    ("硕腾 (Zoetis)", "美国", "全球最大动物保健公司"),
    ("勃林格殷格翰 (Boehringer Ingelheim)", "德国", "全球动保领导者"),
    ("默沙东 (MSD Animal Health)", "美国", "知名动物保健企业"),
    ("拜耳 (Bayer)", "德国", "动保领域知名品牌"),
    ("海正动保", "中国", "国内领先动保企业"),
    ("瑞普生物", "中国", "兽用生物制品龙头"),
    ("普莱柯", "中国", "宠物疫苗研发企业"),
    ("皇家 (Royal Canin)", "法国", "全球知名宠物食品品牌"),
    ("冠能 (Pro Plan)", "美国", "雀巢旗下高端宠粮"),
    ("渴望 (Orijen)", "加拿大", "高端天然宠粮"),
    ("爱肯拿 (Acana)", "加拿大", "天然宠粮品牌"),
    ("麦富迪", "中国", "国内知名宠粮品牌"),
    ("卫仕", "中国", "宠物营养品品牌"),
    ("红狗 (RedDog)", "中国", "宠物营养膏品牌"),
    ("麦德氏", "中国", "宠物保健品品牌"),
]
for name, country, desc in brands_data:
    db.add(models.Brand(name=name, country=country, description=desc))

# ============================================================
# 2. 品类
# ============================================================
categories_data = [
    # 药品
    ("驱虫药", None, "药品"),
    ("疫苗", None, "药品"),
    ("皮肤病药", None, "药品"),
    ("抗生素", None, "药品"),
    ("心脏/肾脏用药", None, "药品"),
    ("眼耳用药", None, "药品"),
    ("消化系统用药", None, "药品"),
    # 食品
    ("猫粮", None, "食品"),
    ("狗粮", None, "食品"),
    ("猫零食", None, "食品"),
    ("狗零食", None, "食品"),
    ("处方粮", None, "食品"),
    # 保健品
    ("关节保护", None, "保健品"),
    ("营养膏", None, "保健品"),
    ("益生菌", None, "保健品"),
    ("化毛膏", None, "保健品"),
    ("美毛护肤", None, "保健品"),
    ("综合营养", None, "保健品"),
]
for name, parent, ctype in categories_data:
    db.add(models.Category(name=name, parent_id=parent, type=ctype))

# ============================================================
# 3. 成分
# ============================================================
ingredients_data = [
    # 驱虫成分
    ("塞拉菌素 (Selamectin)", "大宠爱", "驱虫", 4, "广谱体内外驱虫成分，对心丝虫、跳蚤、耳螨等有效", "体内外驱虫"),
    ("非泼罗尼 (Fipronil)", "福来恩", "驱虫", 4, "体外驱虫成分，针对跳蚤和蜱虫", "体外驱虫"),
    ("米尔贝肟 (Milbemycin oxime)", "海乐妙", "驱虫", 4, "体内驱虫成分，预防心丝虫、钩虫、蛔虫", "体内驱虫"),
    ("吡喹酮 (Praziquantel)", "拜宠清", "驱虫", 4, "广谱抗绦虫成分", "驱绦虫"),
    ("伊维菌素 (Ivermectin)", "犬心保", "驱虫", 3, "广谱驱虫成分，柯利犬慎用", "体内外驱虫"),
    ("阿福拉纳 (Afoxolaner)", "尼可信", "驱虫", 4, "新型体外驱虫成分，针对跳蚤和蜱虫", "体外驱虫"),
    ("莫昔克丁 (Moxidectin)", "拜宠清", "驱虫", 4, "长效体内外驱虫成分", "体内外驱虫"),
    # 疫苗成分
    ("犬瘟热病毒抗原 (CDV)", "", "疫苗", 5, "预防犬瘟热的核心疫苗成分", "疫苗免疫"),
    ("犬细小病毒抗原 (CPV)", "", "疫苗", 5, "预防犬细小病毒的核心疫苗成分", "疫苗免疫"),
    ("狂犬病病毒抗原 (Rabies)", "", "疫苗", 5, "预防狂犬病的法定疫苗成分", "疫苗免疫"),
    ("猫泛白细胞减少症病毒抗原 (FPV)", "", "疫苗", 5, "预防猫瘟的核心疫苗成分", "疫苗免疫"),
    ("猫疱疹病毒抗原 (FHV-1)", "", "疫苗", 5, "预防猫鼻支的疫苗成分", "疫苗免疫"),
    ("猫杯状病毒抗原 (FCV)", "", "疫苗", 5, "预防猫杯状病毒的疫苗成分", "疫苗免疫"),
    # 抗生素/抗炎
    ("阿莫西林克拉维酸钾", "速诺", "抗生素", 4, "广谱抗生素，用于细菌感染", "抗菌消炎"),
    ("恩诺沙星 (Enrofloxacin)", "拜有利", "抗生素", 3, "氟喹诺酮类抗生素", "抗菌"),
    ("头孢氨苄 (Cephalexin)", "", "抗生素", 4, "第一代头孢菌素，用于皮肤和尿路感染", "抗菌"),
    ("美洛昔康 (Meloxicam)", "", "抗炎", 3, "非甾体抗炎药，用于镇痛抗炎", "镇痛抗炎"),
    # 皮肤病
    ("特比萘芬 (Terbinafine)", "", "皮肤病", 4, "抗真菌成分，用于皮肤真菌感染", "抗真菌"),
    ("酮康唑 (Ketoconazole)", "", "皮肤病", 3, "抗真菌成分，用于马拉色菌等", "抗真菌"),
    ("莫匹罗星 (Mupirocin)", "", "皮肤病", 4, "外用抗生素，用于皮肤细菌感染", "抗菌"),
    ("泼尼松龙 (Prednisolone)", "", "皮肤病", 2, "糖皮质激素，用于严重过敏和炎症", "抗炎止痒"),
    # 心脏
    ("匹莫苯丹 (Pimobendan)", "", "心脏", 4, "用于犬充血性心力衰竭", "强心"),
    ("贝那普利 (Benazepril)", "", "心脏", 4, "ACE抑制剂，用于高血压和心衰", "降压护心"),
    # 关节
    ("葡萄糖胺 (Glucosamine)", "", "关节", 5, "关节软骨保护成分", "关节保护"),
    ("硫酸软骨素 (Chondroitin)", "", "关节", 5, "关节润滑和保护成分", "关节保护"),
    ("绿唇贻贝提取物", "", "关节", 5, "天然抗炎和关节保护成分", "关节保护"),
    # 营养
    ("Omega-3 脂肪酸", "", "营养", 5, "美毛护肤、抗炎、心血管保护", "美毛护肤"),
    ("牛磺酸 (Taurine)", "", "营养", 5, "猫必需氨基酸，保护心脏和视力", "心脏视力"),
    ("益生菌 (Probiotics)", "", "营养", 5, "调节肠道菌群，改善消化", "肠道健康"),
    ("维生素E", "", "营养", 5, "抗氧化，保护细胞膜", "抗氧化"),
    ("赖氨酸 (Lysine)", "", "营养", 5, "抑制猫疱疹病毒复制", "抗病毒"),
]
for name, alias, cat, safety, desc, func in ingredients_data:
    db.add(models.Ingredient(
        name=name, alias=alias, category=cat,
        safety_level=safety, description=desc, function=func
    ))

# ============================================================
# 4. 品种
# ============================================================
breeds_data = [
    # 狗 — 大型
    ("金毛寻回犬", "狗", "大型", "髋关节发育不良、肘关节发育不良、肥胖、癌症", "温顺友善的家庭犬"),
    ("拉布拉多寻回犬", "狗", "大型", "髋关节发育不良、肥胖、食物过敏", "最受欢迎的家庭犬之一"),
    ("德国牧羊犬", "狗", "大型", "髋关节发育不良、退行性脊髓病、胃扭转", "聪明忠诚的工作犬"),
    ("哈士奇", "狗", "大型", "角膜营养不良、髋关节发育不良、锌缺乏", "活泼好动的雪橇犬"),
    ("阿拉斯加雪橇犬", "狗", "大型", "髋关节发育不良、甲状腺功能减退、胃扭转", "强壮耐寒的工作犬"),
    # 狗 — 中型
    ("柯基犬", "狗", "中型", "椎间盘疾病(IVDD)、髋关节发育不良、肥胖", "短腿活泼的牧牛犬"),
    ("柴犬", "狗", "中型", "过敏、髋关节发育不良、青光眼", "独立忠诚的日本犬"),
    ("边境牧羊犬", "狗", "中型", "髋关节发育不良、癫痫、进行性视网膜萎缩", "最聪明的犬种"),
    ("法国斗牛犬", "狗", "中型", "短头综合征、皮肤病(褶皱皮炎)、椎间盘疾病", "温顺可爱的伴侣犬"),
    # 狗 — 小型
    ("贵宾犬(泰迪)", "狗", "小型", "髌骨脱位、泪痕、牙周病、癫痫", "聪明不掉毛的伴侣犬"),
    ("比熊犬", "狗", "小型", "髌骨脱位、过敏、牙周病", "活泼可爱的白色小狗"),
    ("博美犬", "狗", "小型", "气管塌陷、髌骨脱位、牙齿问题", "小巧机警的玩具犬"),
    ("吉娃娃", "狗", "小型", "髌骨脱位、气管塌陷、脑积水", "世界上最小的犬种"),
    ("约克夏梗", "狗", "小型", "气管塌陷、髌骨脱位、牙周病", "勇敢自信的长毛玩具犬"),
    # 猫 — 短毛
    ("英国短毛猫", "猫", "中型", "多囊肾病(PKD)、肥厚性心肌病(HCM)、泪溢", "圆脸温顺的猫咪"),
    ("美国短毛猫", "猫", "中型", "肥厚性心肌病、口腔疾病", "健康活泼的工作猫"),
    ("异国短毛猫(加菲)", "猫", "中型", "多囊肾病、泪管阻塞、呼吸道问题", "扁脸可爱的波斯近亲"),
    ("暹罗猫", "猫", "中型", "哮喘、口腔疾病、肾淀粉样变性", "聪明话多的东方猫"),
    # 猫 — 长毛
    ("布偶猫", "猫", "大型", "肥厚性心肌病(HCM)、膀胱结石", "温柔粘人的仙女猫"),
    ("波斯猫", "猫", "中型", "多囊肾病、泪管阻塞、皮肤病", "优雅高贵的扁脸猫"),
    ("缅因猫", "猫", "大型", "髋关节发育不良、脊柱肌肉萎缩(SMA)、肥厚性心肌病", "体型最大的家猫"),
    ("挪威森林猫", "猫", "大型", "糖原贮积症IV型、髋关节发育不良", "强壮耐寒的北欧猫"),
    # 猫 — 其他
    ("中华田园猫(橘猫)", "猫", "中型", "相对健康，易患下泌尿道综合征", "中国本土家猫"),
    ("斯芬克斯猫(无毛)", "猫", "中型", "皮肤病、体温调节困难、心脏病", "独特无毛的猫咪"),
]
for name, species, size, issues, desc in breeds_data:
    db.add(models.PetBreed(
        name=name, species=species, size=size,
        common_issues=issues, description=desc,
        image_url=f"/avatars/{name.replace('(', '_').replace(')', '').replace(' ', '_')}.webp"
    ))

db.flush()

# ============================================================
# 5. 产品
# ============================================================
# 辅助函数
def get_brand(name):
    return db.query(models.Brand).filter(models.Brand.name == name).first()

def get_category(name):
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_ingredient(name):
    return db.query(models.Ingredient).filter(models.Ingredient.name.like(f"%{name}%")).first()

products_data = [
    # ── 驱虫药 ──
    {
        "name": "大宠爱 (Revolution)",
        "brand": "硕腾 (Zoetis)",
        "category": "驱虫药",
        "type": "药品",
        "desc": "广谱体内外驱虫滴剂，含塞拉菌素，每月一次，用于预防心丝虫病、杀灭跳蚤、治疗耳螨等。适用于6周龄以上的犬猫。",
        "approval": "兽药字(2015)140012069",
        "score": 4.5,
        "usage": "每月一次，滴于肩胛骨间皮肤。根据体重选择规格。",
        "species": "猫狗",
        "ingredients": ["塞拉菌素 (Selamectin)"],
    },
    {
        "name": "福来恩 (Frontline)",
        "brand": "勃林格殷格翰 (Boehringer Ingelheim)",
        "category": "驱虫药",
        "type": "药品",
        "desc": "体外驱虫滴剂/喷剂，含非泼罗尼，有效杀灭跳蚤和蜱虫。滴剂每月一次，喷剂可用于幼龄动物。",
        "approval": "兽药字(2015)140022069",
        "score": 4.5,
        "usage": "每月一次，滴于肩胛骨间皮肤。喷剂可用于全身喷洒。",
        "species": "猫狗",
        "ingredients": ["非泼罗尼 (Fipronil)"],
    },
    {
        "name": "海乐妙 (Milbemax)",
        "brand": "海正动保",
        "category": "驱虫药",
        "type": "药品",
        "desc": "体内驱虫片，含米尔贝肟和吡喹酮，广谱驱除蛔虫、钩虫、绦虫，预防心丝虫。国产高性价比驱虫药。",
        "approval": "兽药字170802069",
        "score": 4.5,
        "usage": "每3个月一次，根据体重口服。",
        "species": "猫狗",
        "ingredients": ["米尔贝肟 (Milbemycin oxime)", "吡喹酮 (Praziquantel)"],
    },
    {
        "name": "拜宠清 (Drontal)",
        "brand": "拜耳 (Bayer)",
        "category": "驱虫药",
        "type": "药品",
        "desc": "体内驱虫片，含吡喹酮等成分，广谱驱除绦虫、蛔虫、钩虫。",
        "approval": "兽药字(2015)140052069",
        "score": 4.0,
        "usage": "每3个月一次，根据体重口服。",
        "species": "猫狗",
        "ingredients": ["吡喹酮 (Praziquantel)"],
    },
    {
        "name": "犬心保 (Heartgard)",
        "brand": "默沙东 (MSD Animal Health)",
        "category": "驱虫药",
        "type": "药品",
        "desc": "犬用心丝虫预防咀嚼片，含伊维菌素和吡喹酮，每月一次。注意：柯利犬慎用。",
        "approval": "兽药字(2015)140032069",
        "score": 4.0,
        "usage": "每月一次，根据体重口服。柯利犬禁用。",
        "species": "狗",
        "ingredients": ["伊维菌素 (Ivermectin)", "吡喹酮 (Praziquantel)"],
    },
    {
        "name": "尼可信 (NexGard)",
        "brand": "勃林格殷格翰 (Boehringer Ingelheim)",
        "category": "驱虫药",
        "type": "药品",
        "desc": "犬用口服体外驱虫咀嚼片，含阿福拉纳，每月一次，有效杀灭跳蚤和蜱虫。",
        "approval": "兽药字(2015)140062069",
        "score": 4.5,
        "usage": "每月一次，根据体重口服。",
        "species": "狗",
        "ingredients": ["阿福拉纳 (Afoxolaner)"],
    },
    # ── 疫苗 ──
    {
        "name": "卫佳伍 (Vanguard Plus 5)",
        "brand": "硕腾 (Zoetis)",
        "category": "疫苗",
        "type": "药品",
        "desc": "犬五联疫苗，预防犬瘟热、细小病毒、腺病毒2型、副流感。幼犬首免6-8周龄开始。",
        "approval": "兽药生字(2015)140011012",
        "score": 5.0,
        "usage": "幼犬6-8周龄首免，间隔3-4周加强，成年后每年加强一次。",
        "species": "狗",
        "ingredients": ["犬瘟热病毒抗原 (CDV)", "犬细小病毒抗原 (CPV)"],
    },
    {
        "name": "妙三多 (Nobivac Tricat)",
        "brand": "默沙东 (MSD Animal Health)",
        "category": "疫苗",
        "type": "药品",
        "desc": "猫三联疫苗，预防猫瘟(泛白细胞减少症)、猫鼻支(疱疹病毒)、猫杯状病毒。",
        "approval": "兽药生字(2015)140031012",
        "score": 5.0,
        "usage": "幼猫8周龄首免，间隔3-4周加强，成年后每年加强一次。",
        "species": "猫",
        "ingredients": ["猫泛白细胞减少症病毒抗原 (FPV)", "猫疱疹病毒抗原 (FHV-1)", "猫杯状病毒抗原 (FCV)"],
    },
    # ── 抗生素 ──
    {
        "name": "速诺 (Synulox)",
        "brand": "硕腾 (Zoetis)",
        "category": "抗生素",
        "type": "药品",
        "desc": "广谱抗生素，含阿莫西林克拉维酸钾，用于犬猫细菌感染（皮肤、尿路、呼吸道等）。",
        "approval": "兽药字(2015)140017069",
        "score": 4.0,
        "usage": "根据体重口服，每日两次，连用5-7天。需兽医处方。",
        "species": "猫狗",
        "ingredients": ["阿莫西林克拉维酸钾"],
    },
    {
        "name": "拜有利 (Baytril)",
        "brand": "拜耳 (Bayer)",
        "category": "抗生素",
        "type": "药品",
        "desc": "氟喹诺酮类抗生素，含恩诺沙星，用于犬猫细菌感染。注意：幼龄动物慎用。",
        "approval": "兽药字(2015)140057069",
        "score": 3.5,
        "usage": "根据体重口服或注射，每日一次。需兽医处方。",
        "species": "猫狗",
        "ingredients": ["恩诺沙星 (Enrofloxacin)"],
    },
    # ── 猫粮 ──
    {
        "name": "皇家室内成猫粮 (Royal Canin Indoor)",
        "brand": "皇家 (Royal Canin)",
        "category": "猫粮",
        "type": "食品",
        "desc": "专为室内成猫设计，含易消化蛋白和特殊纤维，帮助减少毛球和粪便异味。",
        "approval": "",
        "score": 4.0,
        "usage": "根据体重和活动量喂食，保证充足饮水。",
        "species": "猫",
        "ingredients": ["Omega-3 脂肪酸", "维生素E"],
    },
    {
        "name": "渴望六种鱼 (Orijen Six Fish)",
        "brand": "渴望 (Orijen)",
        "category": "猫粮",
        "type": "食品",
        "desc": "高蛋白无谷猫粮，含六种野生鱼类，85%动物成分，适合全阶段猫咪。",
        "approval": "",
        "score": 4.5,
        "usage": "根据体重和活动量喂食。高蛋白配方，换粮需逐步过渡。",
        "species": "猫",
        "ingredients": ["Omega-3 脂肪酸", "牛磺酸 (Taurine)", "维生素E"],
    },
    {
        "name": "爱肯拿草原猫粮 (Acana Grasslands)",
        "brand": "爱肯拿 (Acana)",
        "category": "猫粮",
        "type": "食品",
        "desc": "无谷猫粮，含自由放养禽肉和野生鱼类，75%动物成分，适合全阶段猫咪。",
        "approval": "",
        "score": 4.5,
        "usage": "根据体重和活动量喂食。",
        "species": "猫",
        "ingredients": ["Omega-3 脂肪酸", "牛磺酸 (Taurine)", "维生素E"],
    },
    # ── 狗粮 ──
    {
        "name": "冠能中型犬成犬粮 (Pro Plan Medium Adult)",
        "brand": "冠能 (Pro Plan)",
        "category": "狗粮",
        "type": "食品",
        "desc": "中型犬成犬粮，含优质鸡肉和益生元，支持消化健康和免疫力。",
        "approval": "",
        "score": 4.0,
        "usage": "根据体重和活动量喂食，分2餐。",
        "species": "狗",
        "ingredients": ["Omega-3 脂肪酸", "维生素E", "益生菌 (Probiotics)"],
    },
    {
        "name": "麦富迪牛肉双拼狗粮",
        "brand": "麦富迪",
        "category": "狗粮",
        "type": "食品",
        "desc": "国产高性价比狗粮，含牛肉和鸡肉双拼，添加益生元帮助消化。",
        "approval": "",
        "score": 3.5,
        "usage": "根据体重和活动量喂食。",
        "species": "狗",
        "ingredients": ["维生素E", "益生菌 (Probiotics)"],
    },
    # ── 保健品 ──
    {
        "name": "卫仕关节舒 (Nourse Joint Care)",
        "brand": "卫仕",
        "category": "关节保护",
        "type": "保健品",
        "desc": "犬猫关节保护营养品，含葡萄糖胺和硫酸软骨素，帮助维护关节健康。",
        "approval": "",
        "score": 4.5,
        "usage": "根据体重每日喂食，可混入粮中。",
        "species": "猫狗",
        "ingredients": ["葡萄糖胺 (Glucosamine)", "硫酸软骨素 (Chondroitin)"],
    },
    {
        "name": "红狗营养膏 (RedDog Nutrition Gel)",
        "brand": "红狗 (RedDog)",
        "category": "营养膏",
        "type": "保健品",
        "desc": "综合营养补充膏，含维生素、矿物质和氨基酸，适合食欲不振、术后恢复的犬猫。",
        "approval": "",
        "score": 4.0,
        "usage": "每日按体重挤出适量喂食，可直接喂或混入粮中。",
        "species": "猫狗",
        "ingredients": ["维生素E", "牛磺酸 (Taurine)", "赖氨酸 (Lysine)"],
    },
    {
        "name": "麦德氏益生菌 (IN-PLUS Probiotics)",
        "brand": "麦德氏",
        "category": "益生菌",
        "type": "保健品",
        "desc": "犬猫专用益生菌，调节肠道菌群，改善软便和消化不良。",
        "approval": "",
        "score": 4.5,
        "usage": "每日一包，混入粮中或直接喂食。",
        "species": "猫狗",
        "ingredients": ["益生菌 (Probiotics)"],
    },
    # ── 处方粮 ──
    {
        "name": "皇家犬低过敏处方粮 (Royal Canin Hypoallergenic)",
        "brand": "皇家 (Royal Canin)",
        "category": "处方粮",
        "type": "食品",
        "desc": "犬用低过敏处方粮，水解蛋白配方，用于食物过敏和不耐受的犬。需兽医指导使用。",
        "approval": "",
        "score": 4.0,
        "usage": "需兽医处方，根据体重喂食。",
        "species": "狗",
        "ingredients": ["Omega-3 脂肪酸", "维生素E"],
    },
    {
        "name": "皇家猫泌尿道处方粮 (Royal Canin Urinary SO)",
        "brand": "皇家 (Royal Canin)",
        "category": "处方粮",
        "type": "食品",
        "desc": "猫用泌尿道处方粮，帮助溶解鸟粪石结晶，降低复发风险。需兽医指导使用。",
        "approval": "",
        "score": 4.0,
        "usage": "需兽医处方，根据体重喂食。",
        "species": "猫",
        "ingredients": ["Omega-3 脂肪酸", "维生素E"],
    },
    # ── 皮肤病药 ──
    {
        "name": "皮特芬喷剂",
        "brand": "瑞普生物",
        "category": "皮肤病药",
        "type": "药品",
        "desc": "犬猫真菌性皮肤病外用喷剂，含特比萘芬，用于猫癣、狗癣等真菌感染。",
        "approval": "兽药字020032069",
        "score": 3.5,
        "usage": "每日1-2次，喷于患处。连续使用2-4周。",
        "species": "猫狗",
        "ingredients": ["特比萘芬 (Terbinafine)"],
    },
    {
        "name": "耳肤灵 (Surolan)",
        "brand": "硕腾 (Zoetis)",
        "category": "皮肤病药",
        "type": "药品",
        "desc": "犬猫耳部感染治疗滴剂，含莫匹罗星等成分，用于细菌性和真菌性外耳炎。",
        "approval": "兽药字(2015)140017079",
        "score": 3.5,
        "usage": "每日2次，滴入耳道后按摩耳根。连用7-14天。",
        "species": "猫狗",
        "ingredients": ["莫匹罗星 (Mupirocin)", "酮康唑 (Ketoconazole)"],
    },
    # ── 消化系统用药 ──
    {
        "name": "蒙脱石散 (Smecta)",
        "brand": "海正动保",
        "category": "消化系统用药",
        "type": "药品",
        "desc": "犬猫止泻药，蒙脱石成分，吸附毒素、保护肠道黏膜。用于急性腹泻。",
        "approval": "",
        "score": 4.0,
        "usage": "根据体重口服，每日2-3次。与其它药物间隔2小时。",
        "species": "猫狗",
        "ingredients": [],
    },
    # ── 关节保护 ──
    {
        "name": "麦德氏关节灵 (IN-PLUS Joint)",
        "brand": "麦德氏",
        "category": "关节保护",
        "type": "保健品",
        "desc": "犬猫关节保护咀嚼片，含葡萄糖胺、软骨素和绿唇贻贝，三重关节保护。",
        "approval": "",
        "score": 4.5,
        "usage": "根据体重每日喂食。",
        "species": "猫狗",
        "ingredients": ["葡萄糖胺 (Glucosamine)", "硫酸软骨素 (Chondroitin)", "绿唇贻贝提取物"],
    },
    # ── 化毛膏 ──
    {
        "name": "红狗化毛膏 (RedDog Hairball Gel)",
        "brand": "红狗 (RedDog)",
        "category": "化毛膏",
        "type": "保健品",
        "desc": "猫咪专用化毛膏，帮助排出体内毛球，预防毛球症。含膳食纤维和润滑成分。",
        "approval": "",
        "score": 4.0,
        "usage": "每日挤出适量喂食，可直接喂或混入粮中。",
        "species": "猫",
        "ingredients": ["维生素E"],
    },
    # ── 美毛护肤 ──
    {
        "name": "卫仕卵磷脂 (Nourse Lecithin)",
        "brand": "卫仕",
        "category": "美毛护肤",
        "type": "保健品",
        "desc": "犬猫美毛护肤营养品，含卵磷脂和Omega-3，改善毛发干枯、掉毛。",
        "approval": "",
        "score": 4.5,
        "usage": "根据体重每日喂食，可混入粮中。",
        "species": "猫狗",
        "ingredients": ["Omega-3 脂肪酸", "维生素E"],
    },
    # ── 综合营养 ──
    {
        "name": "卫仕复合维生素 (Nourse Multivitamin)",
        "brand": "卫仕",
        "category": "综合营养",
        "type": "保健品",
        "desc": "犬猫综合维生素片，含多种维生素和矿物质，补充日常营养。",
        "approval": "",
        "score": 4.5,
        "usage": "根据体重每日喂食。",
        "species": "猫狗",
        "ingredients": ["维生素E", "牛磺酸 (Taurine)", "赖氨酸 (Lysine)"],
    },
    # ── 猫零食 ──
    {
        "name": "麦富迪猫条 (Myfoodie Cat Treat)",
        "brand": "麦富迪",
        "category": "猫零食",
        "type": "食品",
        "desc": "猫咪零食肉泥条，多种口味，可作为奖励或互动零食。",
        "approval": "",
        "score": 3.5,
        "usage": "每日1-2条，作为零食补充。",
        "species": "猫",
        "ingredients": ["牛磺酸 (Taurine)", "维生素E"],
    },
    # ── 狗零食 ──
    {
        "name": "麦富迪鸡肉干 (Myfoodie Chicken Jerky)",
        "brand": "麦富迪",
        "category": "狗零食",
        "type": "食品",
        "desc": "犬用鸡肉干零食，纯肉制作，高蛋白低脂肪，适合训练奖励。",
        "approval": "",
        "score": 3.5,
        "usage": "每日适量，作为零食补充。",
        "species": "狗",
        "ingredients": ["维生素E"],
    },
]

for pdata in products_data:
    brand = get_brand(pdata["brand"])
    category = get_category(pdata["category"])
    product = models.Product(
        name=pdata["name"],
        brand_id=brand.id if brand else None,
        category_id=category.id if category else None,
        type=pdata["type"],
        description=pdata["desc"],
        approval_number=pdata["approval"],
        safety_score=pdata["score"],
        usage_guide=pdata["usage"],
        suitable_species=pdata["species"],
    )
    db.add(product)
    db.flush()

    # 关联成分
    for idx, ing_name in enumerate(pdata["ingredients"]):
        ing = get_ingredient(ing_name)
        if ing:
            db.execute(models.product_ingredient.insert().values(
                product_id=product.id,
                ingredient_id=ing.id,
                sort_order=idx + 1,
                is_active=1,
            ))

# ============================================================
# 6. 品种推荐产品
# ============================================================
breed_recommendations = {
    "金毛寻回犬": ["卫仕关节舒 (Nourse Joint Care)"],
    "拉布拉多寻回犬": ["卫仕关节舒 (Nourse Joint Care)"],
    "德国牧羊犬": ["卫仕关节舒 (Nourse Joint Care)"],
    "柯基犬": ["卫仕关节舒 (Nourse Joint Care)"],
    "法国斗牛犬": ["福来恩 (Frontline)"],
    "贵宾犬(泰迪)": ["卫仕关节舒 (Nourse Joint Care)"],
    "英国短毛猫": ["妙三多 (Nobivac Tricat)", "红狗营养膏 (RedDog Nutrition Gel)"],
    "布偶猫": ["妙三多 (Nobivac Tricat)", "红狗营养膏 (RedDog Nutrition Gel)"],
    "中华田园猫(橘猫)": ["大宠爱 (Revolution)", "麦德氏益生菌 (IN-PLUS Probiotics)"],
}

for breed_name, product_names in breed_recommendations.items():
    breed = db.query(models.PetBreed).filter(models.PetBreed.name == breed_name).first()
    if not breed:
        continue
    for pname in product_names:
        product = db.query(models.Product).filter(models.Product.name == pname).first()
        if product:
            db.execute(models.breed_product.insert().values(
                breed_id=breed.id, product_id=product.id
            ))

db.commit()
db.close()

print("✅ 种子数据导入完成！")
print(f"   品牌: {len(brands_data)}")
print(f"   品类: {len(categories_data)}")
print(f"   成分: {len(ingredients_data)}")
print(f"   品种: {len(breeds_data)}")
print(f"   产品: {len(products_data)}")
