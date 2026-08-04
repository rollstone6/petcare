#!/usr/bin/env python3
"""
根据权威数据源更新品种详情
数据源:
  - 猫: TheCatAPI (api.thecatapi.com) — 聚合 CFA/TICA/VCA Hospitals/Wikipedia
  - 狗: dogapi.dog (283品种, 寿命/体重/低敏) + thedogapi.com (性格/产地补充)
  - 本土品种: 手工编写权威内容
用法: ./venv/bin/python update_breeds_authoritative.py
"""
import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'petcare.db')

# ============================================================
# 1. 表结构迁移: 新增字段
# ============================================================
NEW_COLUMNS = [
    ("name_en", "VARCHAR(100) DEFAULT ''"),        # 英文名
    ("lifespan", "VARCHAR(30) DEFAULT ''"),         # 寿命 如 "12-14年"
    ("weight_range", "VARCHAR(50) DEFAULT ''"),     # 体重 如 "25-34kg"
    ("temperament", "VARCHAR(200) DEFAULT ''"),     # 性格标签(中文,逗号分隔)
    ("origin", "VARCHAR(50) DEFAULT ''"),           # 产地(中文)
    ("hypoallergenic", "INTEGER DEFAULT 0"),        # 是否低敏
]

def migrate(conn):
    c = conn.cursor()
    c.execute("PRAGMA table_info(pet_breeds)")
    existing = {r[1] for r in c.fetchall()}
    for col, typedef in NEW_COLUMNS:
        if col not in existing:
            c.execute(f"ALTER TABLE pet_breeds ADD COLUMN {col} {typedef}")
            print(f"  + 新增列 {col}")
    conn.commit()

# ============================================================
# 2. 性格词汇翻译表 (英→中)
# ============================================================
TEMPERAMENT_CN = {
    "active": "活泼", "adaptable": "适应力强", "adventurous": "爱冒险",
    "affectionate": "深情", "agile": "敏捷", "alert": "警觉",
    "aloof": "高冷", "athletic": "运动型", "calm": "沉稳",
    "charming": "迷人", "clever": "聪明", "confident": "自信",
    "courageous": "勇敢", "curious": "好奇心强", "demanding": "需求感强",
    "dependent": "粘人", "determined": "坚定", "devoted": "忠心",
    "dignified": "威严", "docile": "温顺", "eager to please": "乐于服从",
    "easy going": "随和", "easygoing": "随和", "energetic": "精力充沛",
    "even-tempered": "性情稳定", "expressive": "表情丰富", "fearless": "无畏",
    "friendly": "友善", "fun-loving": "爱玩", "gentle": "温柔",
    "good-natured": "脾气好", "happy": "开朗", "hardy": "强壮皮实",
    "highly interactive": "互动性强", "highly intelligent": "智商极高",
    "independent": "独立", "inquisitive": "好奇", "intelligent": "聪明",
    "interactive": "互动性强", "lively": "活泼", "loving": "亲人",
    "loyal": "忠诚", "merry": "欢快", "mischievous": "调皮",
    "optimistic": "乐观", "outgoing": "外向", "patient": "耐心",
    "peaceful": "温和", "playful": "爱玩耍", "protective": "护卫性强",
    "quiet": "安静", "relaxed": "慵懒放松", "reserved": "矜持",
    "sedate": "沉静", "sensible": "懂事", "sensitive": "敏感",
    "shy": "害羞", "smart": "聪明", "sociable": "合群",
    "social": "社交性强", "spirited": "活力四射", "sweet": "甜美",
    "sweet-tempered": "性情甜美", "talkative": "爱说话", "tenacious": "执着",
    "trainable": "易训练", "warm": "温暖", "work-focused": "专注工作",
}

def translate_temperament(en_str, limit=6):
    """英文性格列表 → 中文标签"""
    tokens = [t.strip().lower() for t in en_str.split(',') if t.strip()]
    cn, seen = [], set()
    for t in tokens:
        c = TEMPERAMENT_CN.get(t)
        if c and c not in seen:
            seen.add(c)
            cn.append(c)
    return "、".join(cn[:limit])

# ============================================================
# 3. 产地翻译表
# ============================================================
ORIGIN_CN = {
    "Scotland": "苏格兰", "England": "英格兰", "United Kingdom": "英国",
    "Great Britain": "英国", "Germany": "德国", "France": "法国",
    "United States": "美国", "United States, Australia": "美国/澳大利亚",
    "Japan": "日本", "China": "中国", "Italy": "意大利",
    "Russia": "俄罗斯", "Canada": "加拿大", "Wales": "威尔士",
    "Cardiganshire, Wales": "威尔士", "Pembrokeshire, Wales": "威尔士",
    "Tibet": "中国西藏", "Belgium": "比利时", "Denmark": "丹麦",
    "Switzerland": "瑞士", "Australia": "澳大利亚", "Norway": "挪威",
    "Sweden": "瑞典", "Finland": "芬兰", "Egypt": "埃及",
    "Thailand": "泰国", "Turkey": "土耳其", "Iran": "伊朗(波斯)",
    "Persia": "波斯(今伊朗)", "Burma": "缅甸", "Myanmar": "缅甸",
    "Singapore": "新加坡", "Isle of Man": "马恩岛", "Spain": "西班牙",
    "Greece": "希腊", "Mexico": "墨西哥", "Cuba": "古巴",
    "Ethiopia": "埃塞俄比亚", "Abyssinia (Ethiopia)": "埃塞俄比亚",
    "Bangladesh": "孟加拉国", "Arctic": "北极地区", "Siberia": "西伯利亚",
    "Alaska": "阿拉斯加", "Alaska, United States": "美国阿拉斯加",
    "Croatia": "克罗地亚", "Czech Republic": "捷克", "Poland": "波兰",
    "Hungary": "匈牙利", "Netherlands": "荷兰", "Austria": "奥地利",
    "Ireland": "爱尔兰", "South Africa": "南非", "Argentina": "阿根廷",
    "Brazil": "巴西", "Chile": "智利", "India": "印度",
    "Korea": "韩国", "Vietnam": "越南", "Portugal": "葡萄牙",
    "Malta": "马耳他", "Cyprus": "塞浦路斯", "Kenya": "肯尼亚",
    "Congo": "刚果", "Turkey / Russia": "土耳其/俄罗斯",
    "Norway / Russia": "挪威/俄罗斯",
}

def translate_origin(en):
    if not en:
        return ""
    return ORIGIN_CN.get(en.strip(), en)

# ============================================================
# 4. 狗品种映射: DB名 → (dogapi.dog名, thedogapi补充名)
# ============================================================
DOG_MAP = {
    '金毛寻回犬': ('Golden Retriever', 'Golden Retriever'),
    '拉布拉多寻回犬': ('Labrador Retriever', 'Labrador Retriever'),
    '德国牧羊犬': ('German Shepherd Dog', 'German Shepherd'),
    '哈士奇': ('Siberian Husky', 'Siberian Husky'),
    '柴犬': ('Shiba Inu', 'Shiba Inu'),
    '边境牧羊犬': ('Border Collie', 'Border Collie'),
    '法国斗牛犬': ('French Bulldog', 'French Bulldog'),
    '萨摩耶': ('Samoyed', 'Samoyed'),
    '阿拉斯加雪橇犬': ('Alaskan Malamute', 'Alaskan Malamute'),
    '博美犬': ('Pomeranian', 'Pomeranian'),
    '比熊犬': ('Bichon Frise', 'Bichon Frisé'),
    '吉娃娃': ('Chihuahua', 'Chihuahua'),
    '约克夏梗': ('Yorkshire Terrier', 'Yorkshire Terrier'),
    '比格犬': ('Beagle', 'Beagle'),
    '巴哥犬': ('Pug', 'Pug'),
    '西施犬': ('Shih Tzu', 'Shih Tzu'),
    '马尔济斯犬': ('Maltese', 'Maltese'),
    '松狮犬': ('Chow Chow', 'Chow Chow'),
    '秋田犬': ('Akita', 'Akita'),
    '大白熊犬': ('Great Pyrenees', None),  # thedogapi 缺失
    '杜宾犬': ('Doberman Pinscher', 'Doberman Pinscher'),
    '罗威纳犬': ('Rottweiler', 'Rottweiler'),
    '牛头梗': ('Bull Terrier', 'Bull Terrier'),
    '巴吉度猎犬': ('Basset Hound', 'Basset Hound'),
    '喜乐蒂牧羊犬': ('Shetland Sheepdog', 'Shetland Sheepdog'),
    '卡斯罗犬': ('Cane Corso', 'Cane Corso'),
    '彭布罗克威尔士柯基犬': ('Pembroke Welsh Corgi', 'Pembroke Welsh Corgi'),
    '卡迪根威尔士柯基犬': ('Cardigan Welsh Corgi', 'Cardigan Welsh Corgi'),
    '标准腊肠犬': ('Dachshund', 'Dachshund'),
    '迷你腊肠犬': ('Dachshund', 'Dachshund'),
    '玩具贵宾犬': ('Poodle (Toy)', 'Poodle'),
    '迷你贵宾犬': ('Poodle (Miniature)', 'Poodle'),
    '标准贵宾犬': ('Poodle (Standard)', 'Poodle'),
    '迷你雪纳瑞犬': ('Miniature Schnauzer', 'Miniature Schnauzer'),
    '标准雪纳瑞犬': ('Standard Schnauzer', 'Standard Schnauzer'),
    '巨型雪纳瑞犬': ('Giant Schnauzer', 'Giant Schnauzer'),
}

# 猫品种映射: DB名 → TheCatAPI name
CAT_MAP = {
    '英国短毛猫': 'British Shorthair',
    '美国短毛猫': 'American Shorthair',
    '波斯猫': 'Persian',
    '缅因猫': 'Maine Coon',
    '布偶猫(蓝双)': 'Ragdoll',
    '布偶猫(手套色)': 'Ragdoll',
    '布偶猫(海双)': 'Ragdoll',
    '暹罗猫(重点色)': 'Siamese',
    '传统暹罗猫': 'Siamese',
    '现代暹罗猫': 'Siamese',
    '俄罗斯蓝猫': 'Russian Blue',
    '挪威森林猫': 'Norwegian Forest Cat',
    '斯芬克斯猫(无毛)': 'Sphynx',
    '苏格兰折耳猫': 'Scottish Fold',
    '异国短毛猫(加菲)': 'Exotic Shorthair',
    '阿比西尼亚猫': 'Abyssinian',
    '孟加拉豹猫': 'Bengal',
    '德文卷毛猫': 'Devon Rex',
    '美国卷耳猫': 'American Curl',
    '伯曼猫': 'Birman',
    '曼基康矮脚猫': 'Munchkin',
    '英国长毛猫': 'British Longhair',
    '金渐层': 'British Shorthair',
    '银渐层': 'British Shorthair',
}

# ============================================================
# 5. 手工编写内容 (权威来源无覆盖的本土品种 + 占位描述替换 + 常见疾病补全)
# ============================================================
HANDWRITTEN_DESCRIPTIONS = {
    # --- 狗 ---
    '中华田园犬': '中国本土最古老的犬种之一，数千年来与农耕生活相伴。体质强健、不易生病，忠诚护家、通人性，是公认的"最好养"的狗之一。',
    '卡斯罗犬': '源自古罗马军犬血统的意大利护卫犬，体型强健、气势威严。对家人极其忠诚温顺，对陌生人警惕，是顶级的护卫犬种，需要从小社会化训练。',
    '喜乐蒂牧羊犬': '来自苏格兰设德兰群岛的小型牧羊犬，外形酷似迷你版苏格兰牧羊犬。聪明灵敏、服从性高、叫声清亮，是优秀的家庭伴侣犬和敏捷运动犬。',
    '大白熊犬': '源自比利牛斯山的古老护卫犬，曾是法国宫廷的"皇家犬"。雪白厚毛、体态雄伟，性格沉稳温和，对家人极富耐心，天生具有守护本能。',
    '巴吉度猎犬': '来自法国的嗅觉猎犬，长耳朵和忧郁眼神是标志性特征。嗅觉仅次于寻血猎犬，性格温和固执，走路慢悠悠，对小孩非常友善。',
    '巴哥犬': '源自中国的古老伴侣犬，面部褶皱多、表情委屈可爱。性格温和黏人、不爱叫，运动需求低，是完美的公寓伴侣犬。',
    '杜宾犬': '19世纪末由德国税务官路易斯·杜宾培育的护卫犬，体态精干优雅、智商极高。忠诚度一流，常被用作军警犬，需要充足运动和训练。',
    '松狮犬': '中国古老犬种，有2000多年历史，蓝黑色舌头是其标志。外表像狮子，性格独立高冷、对主人忠诚，不太爱亲近陌生人。',
    '牛头梗': '来自英国的梗犬，独特的"蛋形头"极具辨识度。性格活泼滑稽、勇敢无畏，对家人温柔，被称为"狗中喜剧演员"。',
    '秋田犬': '日本国天然纪念物，因忠犬八公的故事闻名世界。体型魁梧、性格沉稳忠诚，对主人一往情深，对陌生人保持警惕。',
    '罗威纳犬': '古罗马牧牛犬后裔，世界顶级护卫犬之一。体格强壮、自信沉稳，对家人温柔忠诚，服从性好，需要主人有经验的引导。',
    '萨摩耶': '来自西伯利亚萨摩耶德族的工作犬，一身雪白蓬松长毛，嘴角上翘形成标志性的"萨摩耶微笑"。温顺友善、活泼亲人，被称为"微笑天使"。',
    '西施犬': '源自中国宫廷的古老伴侣犬，名字意为"狮子"。长毛垂坠优雅，性格高傲温和、不爱叫，是出色的公寓伴侣犬。',
    '马尔济斯犬': '地中海马耳他岛的古老玩具犬，有3000年历史。一身雪白丝质长毛，性格温柔甜美、活泼不掉毛，深受贵族女性喜爱。',
    # --- 猫 ---
    '中华田园猫(狸花)': '中国本土最经典的猫咪，虎斑花纹、身体结实。聪明独立、捕猎能力强、体质极佳，是最皮实好养的猫咪之一。',
    '中华田园猫(橘猫)': '橘色虎斑的中国本土猫，"十个橘猫九个胖"说的就是它。性格亲人温和、食欲旺盛，容易发胖，是社区里最受欢迎的猫咪。',
    '中华田园猫(奶牛)': '黑白花色的中国本土猫，像穿了燕尾服。性格活泼聪明、精力旺盛，个体差异大，有的高冷有的粘人，体质健康好养。',
    '中华田园猫(三花)': '黑、橘、白三色花斑的中国本土猫，绝大多数是母猫。性格机敏独立、通人性，花色独一无二，被视为幸运的象征。',
    '伯曼猫': '源自缅甸(经法国繁育)的"缅甸圣猫"，蓝眼睛配四只雪白"手套"是标志。性格温柔安静、亲人不粘人，是优雅的家庭伴侣猫。',
    '俄罗斯蓝猫': '来自俄罗斯阿尔汉格尔斯克港口的短毛猫，银蓝色被毛配翠绿眼睛。性格安静害羞、忠诚专一，对陌生人警惕，被称为"微笑天使"。',
    '孟加拉豹猫': '亚洲豹猫与家猫杂交培育的品种，身披华丽豹纹。精力极其旺盛、好奇心爆棚、爱玩水，智商高，需要大量互动和玩具。',
    '布偶猫(海双)': '海双(海豹双色)是布偶猫的经典花色，脸部白色倒V斑、身体海豹色斑块。性格与其他布偶一样温顺粘人，忍耐力强，被称为"仙女猫"。',
    '德文卷毛猫': '来自英国德文郡的卷毛猫，大耳朵配精灵脸，被毛短而卷曲。性格像狗一样粘人爱互动、爱玩接球，掉毛极少，被称为"小精灵猫"。',
    '暹罗猫(重点色)': '重点色暹罗的经典花色：奶白身体配深色面罩、耳朵、四肢和尾巴。蓝眼睛、话痨、粘人，是猫界最外向健谈的品种。',
    '曼基康矮脚猫': '自然基因突变产生的短腿猫，走路像小短腿赛车。性格活泼外向、永远保持幼猫般的好奇心，跑跳能力并不受短腿影响。',
    '美国卷耳猫': '美国加州自然突变的品种，耳朵向后优雅卷曲。性格友善童心、终身保持玩耍欲，被称为"彼得潘猫"。',
    '苏格兰折耳猫': '苏格兰农场自然突变的折耳猫，圆脸圆眼像猫头鹰。性格甜美安静、不爱动，但折耳基因与骨骼发育疾病强相关，饲养需特别关注骨骼健康。',
    '英国长毛猫': '英国短毛猫的长毛版本，体态圆胖、毛量丰厚。性格沉稳温和、独立不粘人，比英短更安静，适合上班族饲养。',
    '金渐层': '英国短毛猫的金色渐层毛色，毛尖金色、底绒杏色，眼睛多为绿色。性格延续英短的沉稳温和，圆润甜美，是近年最热门的毛色之一。',
    '银渐层': '英国短毛猫的银色渐层毛色，毛尖黑色、底绒纯白，绿眼睛像画了眼线。性格温顺安静、不爱拆家，和蓝猫一样好养。',
    '阿比西尼亚猫': '最古老的猫种之一，形似古埃及壁画中的圣猫。被毛有独特的"渐层色"(ticking)，身材精瘦健美，好奇心极强、爱攀爬探索，被称为"猫中哈士奇"。',
}

# 常见健康问题补全 (当前 DB 中为空的品种)
HANDWRITTEN_ISSUES = {
    # --- 狗 ---
    '中华田园犬': '体质极佳，遗传病少；注意犬瘟/细小疫苗和驱虫',
    '萨摩耶': '髋关节发育不良、糖尿病、进行性视网膜萎缩',
    '秋田犬': '皮脂腺炎、髋关节发育不良、自身免疫性疾病',
    '巴哥犬': '短头综合征(呼吸困难)、皮肤褶皱炎、眼球脱出风险',
    '西施犬': '眼部疾病、皮肤过敏、椎间盘疾病',
    '马尔济斯犬': '泪痕、髌骨脱位、牙周病、低血糖(幼犬)',
    '杜宾犬': '扩张型心肌病(DCM)、血管性血友病、颈椎不稳',
    '罗威纳犬': '髋/肘关节发育不良、十字韧带损伤、胃扭转',
    '松狮犬': '眼睑内翻、髋关节发育不良、易中暑(短吻)',
    '大白熊犬': '髋关节发育不良、胃扭转、骨癌',
    '卡斯罗犬': '髋关节发育不良、胃扭转、癫痫',
    '喜乐蒂牧羊犬': '柯利眼异常(CEA)、癫痫、伊维菌素敏感(MDR1基因)',
    '巴吉度猎犬': '耳道感染(耳道不透气)、椎间盘疾病、眼睑下垂',
    '牛头梗': '先天性耳聋(白色个体)、皮肤过敏、髌骨脱位',
    # --- 猫 ---
    '中华田园猫(狸花)': '体质健康，注意疫苗和驱虫即可',
    '中华田园猫(橘猫)': '体质健康，但贪吃易胖，需控制体重',
    '中华田园猫(奶牛)': '体质健康，遗传病少',
    '中华田园猫(三花)': '体质健康，遗传病少',
    '苏格兰折耳猫': '⚠️ 骨骼软骨发育不良(折耳基因遗传病)、肥厚性心肌病',
    '曼基康矮脚猫': '脊柱前凸、漏斗胸、关节问题',
    '美国卷耳猫': '耳软骨护理、肥厚性心肌病',
    '德文卷毛猫': '遗传性肌病、髌骨脱位、皮肤敏感',
    '孟加拉豹猫': '肥厚性心肌病、进行性视网膜萎缩',
    '俄罗斯蓝猫': '较健康，注意肥胖和下泌尿道问题',
    '伯曼猫': '肥厚性心肌病、多囊肾、先天性白内障',
    '阿比西尼亚猫': '丙酮酸激酶缺乏症、进行性视网膜萎缩、牙龈炎',
    '英国长毛猫': '多囊肾病(PKD)、肥厚性心肌病、肥胖',
    '金渐层': '多囊肾病(PKD)、肥厚性心肌病、肥胖',
    '银渐层': '多囊肾病(PKD)、肥厚性心肌病、肥胖',
    '布偶猫(海双)': '肥厚性心肌病(HCM)、膀胱结石',
    '暹罗猫(重点色)': '哮喘、口腔疾病、肾淀粉样变性',
}

# 体型修正 (基于权威体重数据)
SIZE_FIX = {
    '巨型雪纳瑞犬': '大型',
    '标准贵宾犬': '大型',
    '标准雪纳瑞犬': '中型',
    '大白熊犬': '大型',
}

# ============================================================
# 6. 主流程
# ============================================================
def main():
    # 加载 API 数据
    dogapi_data = json.load(open('/tmp/dogapi_dog.json'))['data']
    thedogapi_data = json.load(open('/tmp/dog_breeds_all.json'))
    thedogapi_fix = json.load(open('/tmp/dog_temperament_fix.json'))
    cat_data = json.load(open('/tmp/cat_breeds.json'))

    dogapi_idx = {b['attributes']['name'].lower(): b for b in dogapi_data}
    thedogapi_idx = {b['name'].lower(): b for b in thedogapi_data}
    cat_idx = {b['name'].lower(): b for b in cat_data}

    conn = sqlite3.connect(DB_PATH)
    migrate(conn)
    c = conn.cursor()

    c.execute("SELECT id, name, species, description, common_issues FROM pet_breeds")
    breeds = c.fetchall()

    updated, skipped = 0, []

    for bid, name, species, desc, issues in breeds:
        updates = {}

        if species == '狗' and name in DOG_MAP:
            dname, tname = DOG_MAP[name]
            d = dogapi_idx.get(dname.lower())
            t = thedogapi_idx.get(tname.lower()) if tname else None
            tf = thedogapi_fix.get(tname) if tname else None  # search API 补充

            if not d:
                skipped.append(f'{name}: dogapi.dog 未找到 {dname}')
                continue

            attr = d['attributes']
            updates['name_en'] = dname.split(' (')[0]
            life = attr.get('life') or {}
            if life.get('min') and life.get('max'):
                updates['lifespan'] = f"{life['min']}-{life['max']}年"
            mw, fw = attr.get('male_weight') or {}, attr.get('female_weight') or {}
            lo = min(mw.get('min', 999), fw.get('min', 999))
            hi = max(mw.get('max', 0), fw.get('max', 0))
            if lo < 999 and hi > 0:
                updates['weight_range'] = f"{lo}-{hi}kg"
            if attr.get('hypoallergenic') is not None:
                updates['hypoallergenic'] = 1 if attr['hypoallergenic'] else 0
            # 性格/产地: 优先 thedogapi 列表, 其次 search 补充
            temp_src = (t or {}).get('temperament') or (tf or {}).get('temperament') or ''
            updates['temperament'] = translate_temperament(temp_src)
            origin_src = (t or {}).get('origin') or (tf or {}).get('origin') or ''
            updates['origin'] = translate_origin(origin_src)

        elif species == '猫' and name in CAT_MAP:
            cname = CAT_MAP[name]
            b = cat_idx.get(cname.lower())
            if not b:
                skipped.append(f'{name}: TheCatAPI 未找到 {cname}')
                continue

            updates['name_en'] = cname
            ls = b.get('life_span', '')
            if ls:
                updates['lifespan'] = f"{ls.replace(' ', '')}年"
            wt = (b.get('weight') or {}).get('metric', '')
            if wt:
                updates['weight_range'] = f"{wt.replace(' ', '').replace('-', '~')}kg".replace('~', '-')
            updates['temperament'] = translate_temperament(b.get('temperament', ''))
            updates['origin'] = translate_origin(b.get('origin', ''))
            if b.get('hypoallergenic') is not None:
                updates['hypoallergenic'] = 1 if b['hypoallergenic'] else 0

        else:
            skipped.append(f'{name}: 无映射(其他物种)')
            # 其他物种仍走手工描述/疾病补全
            if name in HANDWRITTEN_DESCRIPTIONS and (not desc or '常见' in desc):
                updates['description'] = HANDWRITTEN_DESCRIPTIONS[name]
            if name in HANDWRITTEN_ISSUES and not (issues or '').strip():
                updates['common_issues'] = HANDWRITTEN_ISSUES[name]
            if updates:
                sets = ", ".join(f"{k}=?" for k in updates)
                c.execute(f"UPDATE pet_breeds SET {sets} WHERE id=?",
                          list(updates.values()) + [bid])
                updated += 1
            continue

        # 手工内容覆盖: 占位描述 / 缺失疾病
        cur_desc = desc or ''
        if (not cur_desc.strip() or '常见' in cur_desc) and name in HANDWRITTEN_DESCRIPTIONS:
            updates['description'] = HANDWRITTEN_DESCRIPTIONS[name]
        elif name in HANDWRITTEN_DESCRIPTIONS and cur_desc.strip() in ('常见狗品种', '常见猫品种'):
            updates['description'] = HANDWRITTEN_DESCRIPTIONS[name]
        cur_issues = issues or ''
        if not cur_issues.strip() and name in HANDWRITTEN_ISSUES:
            updates['common_issues'] = HANDWRITTEN_ISSUES[name]
        if name in SIZE_FIX:
            updates['size'] = SIZE_FIX[name]

        if updates:
            sets = ", ".join(f"{k}=?" for k in updates)
            c.execute(f"UPDATE pet_breeds SET {sets} WHERE id=?",
                      list(updates.values()) + [bid])
            updated += 1

    conn.commit()
    conn.close()

    print(f"\n✅ 更新完成: {updated} 个品种")
    if skipped:
        print(f"⏭ 跳过: {len(skipped)}")
        for s in skipped:
            print(f"  - {s}")

if __name__ == '__main__':
    main()
