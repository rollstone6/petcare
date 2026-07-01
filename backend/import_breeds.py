"""从 Dog API 和 Cat API 导入品种数据"""
import urllib.request, json, time, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app import models

db = SessionLocal()

# 品种名中英文映射（常见品种）
NAME_MAP = {
    "Affenpinscher": "艾芬品犬",
    "Afghan Hound": "阿富汗猎犬",
    "Airedale Terrier": "万能梗",
    "Akita": "秋田犬",
    "Alaskan Malamute": "阿拉斯加雪橇犬",
    "American Bulldog": "美国斗牛犬",
    "American Eskimo Dog": "美国爱斯基摩犬",
    "American Foxhound": "美国猎狐犬",
    "American Staffordshire Terrier": "美国斯塔福梗",
    "American Water Spaniel": "美国水猎犬",
    "Anatolian Shepherd Dog": "安纳托利亚牧羊犬",
    "Australian Cattle Dog": "澳大利亚牧牛犬",
    "Australian Shepherd": "澳大利亚牧羊犬",
    "Australian Terrier": "澳大利亚梗",
    "Basenji": "巴辛吉犬",
    "Basset Hound": "巴吉度猎犬",
    "Beagle": "比格犬",
    "Bearded Collie": "长须牧羊犬",
    "Beauceron": "博斯龙犬",
    "Bedlington Terrier": "贝灵顿梗",
    "Belgian Malinois": "比利时马林诺斯犬",
    "Belgian Sheepdog": "比利时牧羊犬",
    "Belgian Tervuren": "比利时特伏丹犬",
    "Bernese Mountain Dog": "伯恩山犬",
    "Bichon Frise": "比熊犬",
    "Black and Tan Coonhound": "黑褐猎浣熊犬",
    "Bloodhound": "寻血猎犬",
    "Border Collie": "边境牧羊犬",
    "Border Terrier": "边境梗",
    "Borzoi": "俄罗斯猎狼犬",
    "Boston Terrier": "波士顿梗",
    "Bouvier des Flandres": "法兰德斯牧牛犬",
    "Boxer": "拳师犬",
    "Briard": "伯瑞犬",
    "Brittany": "布列塔尼犬",
    "Brussels Griffon": "布鲁塞尔格里芬犬",
    "Bull Terrier": "牛头梗",
    "Bulldog": "英国斗牛犬",
    "Bullmastiff": "斗牛獒犬",
    "Cairn Terrier": "凯恩梗",
    "Canaan Dog": "迦南犬",
    "Cane Corso": "卡斯罗犬",
    "Cardigan Welsh Corgi": "卡迪根威尔士柯基犬",
    "Cavalier King Charles Spaniel": "查理王小猎犬",
    "Chesapeake Bay Retriever": "切萨皮克湾寻回犬",
    "Chihuahua": "吉娃娃",
    "Chinese Crested": "中国冠毛犬",
    "Chinese Shar-Pei": "沙皮犬",
    "Chow Chow": "松狮犬",
    "Clumber Spaniel": "克伦伯猎犬",
    "Cocker Spaniel": "可卡犬",
    "Collie": "柯利牧羊犬",
    "Curly-Coated Retriever": "卷毛寻回犬",
    "Dachshund": "腊肠犬",
    "Dalmatian": "大麦町犬",
    "Dandie Dinmont Terrier": "丹迪丁蒙梗",
    "Doberman Pinscher": "杜宾犬",
    "English Cocker Spaniel": "英国可卡犬",
    "English Foxhound": "英国猎狐犬",
    "English Setter": "英国雪达犬",
    "English Springer Spaniel": "英国史宾格犬",
    "English Toy Spaniel": "英国玩具犬",
    "Field Spaniel": "田野猎犬",
    "Finnish Spitz": "芬兰波美拉尼亚犬",
    "Flat-Coated Retriever": "平毛寻回犬",
    "French Bulldog": "法国斗牛犬",
    "German Pinscher": "德国宾莎犬",
    "German Shepherd Dog": "德国牧羊犬",
    "German Shorthaired Pointer": "德国短毛指示犬",
    "German Wirehaired Pointer": "德国刚毛指示犬",
    "Giant Schnauzer": "巨型雪纳瑞",
    "Glen of Imaal Terrier": "伊玛尔峡谷梗",
    "Golden Retriever": "金毛寻回犬",
    "Gordon Setter": "戈登雪达犬",
    "Great Dane": "大丹犬",
    "Great Pyrenees": "大白熊犬",
    "Greater Swiss Mountain Dog": "大瑞士山地犬",
    "Greyhound": "灵缇犬",
    "Harrier": "哈利犬",
    "Havanese": "哈瓦那犬",
    "Ibizan Hound": "伊比沙猎犬",
    "Icelandic Sheepdog": "冰岛牧羊犬",
    "Irish Red and White Setter": "爱尔兰红白雪达犬",
    "Irish Setter": "爱尔兰雪达犬",
    "Irish Terrier": "爱尔兰梗",
    "Irish Water Spaniel": "爱尔兰水猎犬",
    "Irish Wolfhound": "爱尔兰猎狼犬",
    "Italian Greyhound": "意大利灵缇犬",
    "Japanese Chin": "日本狆",
    "Keeshond": "荷兰毛狮犬",
    "Kerry Blue Terrier": "凯利蓝梗",
    "Komondor": "可蒙犬",
    "Kuvasz": "库瓦兹犬",
    "Labrador Retriever": "拉布拉多寻回犬",
    "Lakeland Terrier": "湖畔梗",
    "Lhasa Apso": "拉萨犬",
    "Maltese": "马尔济斯犬",
    "Manchester Terrier": "曼彻斯特梗",
    "Mastiff": "马士提夫獒犬",
    "Miniature Bull Terrier": "迷你牛头梗",
    "Miniature Pinscher": "迷你宾莎犬",
    "Miniature Schnauzer": "迷你雪纳瑞",
    "Newfoundland": "纽芬兰犬",
    "Norfolk Terrier": "诺福克梗",
    "Norwegian Buhund": "挪威布哈德犬",
    "Norwegian Elkhound": "挪威猎麋犬",
    "Norwegian Lundehund": "挪威伦德猎犬",
    "Norwich Terrier": "诺维奇梗",
    "Nova Scotia Duck Tolling Retriever": "新斯科舍诱鸭寻回犬",
    "Old English Sheepdog": "英国古代牧羊犬",
    "Otterhound": "水獭猎犬",
    "Papillon": "蝴蝶犬",
    "Parson Russell Terrier": "帕森罗素梗",
    "Pekingese": "北京犬",
    "Pembroke Welsh Corgi": "柯基犬",
    "Petit Basset Griffon Vendeen": "小巴塞格里芬旺代犬",
    "Pharaoh Hound": "法老王猎犬",
    "Plott": "普罗特猎犬",
    "Pointer": "指示犬",
    "Polish Lowland Sheepdog": "波兰低地牧羊犬",
    "Pomeranian": "博美犬",
    "Poodle": "贵宾犬",
    "Portuguese Water Dog": "葡萄牙水犬",
    "Pug": "巴哥犬",
    "Puli": "波利犬",
    "Rhodesian Ridgeback": "罗德西亚脊背犬",
    "Rottweiler": "罗威纳犬",
    "Saint Bernard": "圣伯纳犬",
    "Saluki": "萨路基犬",
    "Samoyed": "萨摩耶犬",
    "Schipperke": "史奇派克犬",
    "Scottish Deerhound": "苏格兰猎鹿犬",
    "Scottish Terrier": "苏格兰梗",
    "Sealyham Terrier": "西里汉梗",
    "Shetland Sheepdog": "喜乐蒂牧羊犬",
    "Shiba Inu": "柴犬",
    "Shih Tzu": "西施犬",
    "Siberian Husky": "哈士奇",
    "Silky Terrier": "丝毛梗",
    "Skye Terrier": "斯凯梗",
    "Soft Coated Wheaten Terrier": "软毛麦色梗",
    "Spinone Italiano": "意大利斯皮奥尼犬",
    "Staffordshire Bull Terrier": "斯塔福斗牛梗",
    "Standard Schnauzer": "标准雪纳瑞",
    "Sussex Spaniel": "苏塞克斯猎犬",
    "Tibetan Mastiff": "藏獒",
    "Tibetan Spaniel": "西藏猎犬",
    "Tibetan Terrier": "西藏梗",
    "Toy Fox Terrier": "玩具猎狐梗",
    "Vizsla": "维兹拉犬",
    "Weimaraner": "魏玛犬",
    "Welsh Springer Spaniel": "威尔士史宾格犬",
    "Welsh Terrier": "威尔士梗",
    "West Highland White Terrier": "西高地白梗",
    "Whippet": "惠比特犬",
    "Wirehaired Pointing Griffon": "刚毛指示格里芬犬",
    "Yorkshire Terrier": "约克夏梗",
}

# 常见健康问题（按品种类型）
HEALTH_ISSUES = {
    "large": "髋关节发育不良、肘关节发育不良、胃扭转、肥胖",
    "medium": "髋关节发育不良、过敏、甲状腺问题",
    "small": "髌骨脱位、气管塌陷、牙周病",
    "brachycephalic": "短头综合征、呼吸道问题、皮肤病、眼部疾病",
    "working": "髋关节发育不良、肘关节发育不良、退行性脊髓病",
    "toy": "髌骨脱位、气管塌陷、牙齿问题、脑积水",
    "sighthound": "胃扭转、心脏问题、骨肉瘤",
    "terrier": "过敏、髌骨脱位、牙齿问题",
}

def get_health_issues(name, size):
    name_lower = name.lower()
    if any(kw in name_lower for kw in ["bulldog", "pug", "boston", "boxer", "pekingese", "shih tzu", "brussels"]):
        return HEALTH_ISSUES["brachycephalic"]
    if any(kw in name_lower for kw in ["chihuahua", "pomeranian", "papillon", "toy", "yorkshire", "maltese", "pekingese"]):
        return HEALTH_ISSUES["toy"]
    if any(kw in name_lower for kw in ["greyhound", "whippet", "borzoi", "saluki", "afghan", "irish wolfhound"]):
        return HEALTH_ISSUES["sighthound"]
    if any(kw in name_lower for kw in ["terrier", "schnauzer"]):
        return HEALTH_ISSUES["terrier"]
    if any(kw in name_lower for kw in ["shepherd", "malinois", "doberman", "rottweiler", "mastiff", "great dane", "bernese", "newfoundland"]):
        return HEALTH_ISSUES["working"]
    if size == "大型":
        return HEALTH_ISSUES["large"]
    if size == "中型":
        return HEALTH_ISSUES["medium"]
    return HEALTH_ISSUES["small"]

def get_size(min_w, max_w):
    avg = (min_w + max_w) / 2
    if avg >= 25:
        return "大型"
    elif avg >= 10:
        return "中型"
    return "小型"

# 拉取 Dog API
print("🐶 从 Dog API 导入犬种...")
page = 1
imported = 0

while True:
    url = f"https://dogapi.dog/api/v2/breeds?page[number]={page}&page[size]=50"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"  ⚠️ 第{page}页失败: {e}")
        break
    
    breeds = data.get('data', [])
    if not breeds:
        break
    
    for b in breeds:
        attrs = b['attributes']
        name_en = attrs['name']
        name_cn = NAME_MAP.get(name_en, name_en)
        
        # 检查是否已存在
        existing = db.query(models.PetBreed).filter(
            models.PetBreed.name == name_cn,
            models.PetBreed.species == "狗"
        ).first()
        if existing:
            continue
        
        life = attrs.get('life', {})
        male_w = attrs.get('male_weight', {})
        female_w = attrs.get('female_weight', {})
        min_w = min(male_w.get('min', 10), female_w.get('min', 10))
        max_w = max(male_w.get('max', 10), female_w.get('max', 10))
        size = get_size(min_w, max_w)
        
        desc = attrs.get('description', '') or ''
        life_span = f"{life.get('min','?')}-{life.get('max','?')}年" if life else ""
        
        breed = models.PetBreed(
            name=name_cn,
            species="狗",
            size=size,
            common_issues=get_health_issues(name_en, size),
            description=f"{desc[:200]} | 寿命: {life_span} | 体重: {min_w}-{max_w}kg",
            image_url="",
        )
        db.add(breed)
        imported += 1
    
    db.commit()
    print(f"  📄 第{page}页: {len(breeds)} 品种")
    page += 1
    time.sleep(1)

print(f"  🎉 犬种导入完成: {imported} 个")

# 拉取 Cat API
print("\n🐱 从 Cat API 导入猫品种...")
try:
    req = urllib.request.Request("https://api.thecatapi.com/v1/breeds?limit=100")
    with urllib.request.urlopen(req, timeout=15) as r:
        cats = json.loads(r.read())
    
    cat_imported = 0
    for c in cats:
        name_en = c['name']
        # 猫品种名映射
        cat_name_map = {
            "Abyssinian": "阿比西尼亚猫",
            "American Bobtail": "美国短尾猫",
            "American Curl": "美国卷耳猫",
            "American Shorthair": "美国短毛猫",
            "American Wirehair": "美国刚毛猫",
            "Balinese": "巴厘猫",
            "Bengal": "孟加拉猫",
            "Birman": "伯曼猫",
            "Bombay": "孟买猫",
            "British Shorthair": "英国短毛猫",
            "Burmese": "缅甸猫",
            "Burmilla": "伯米拉猫",
            "Chartreux": "沙特尔猫",
            "Cornish Rex": "柯尼斯卷毛猫",
            "Devon Rex": "德文卷毛猫",
            "Egyptian Mau": "埃及猫",
            "European Burmese": "欧洲缅甸猫",
            "Exotic Shorthair": "异国短毛猫(加菲)",
            "Havana Brown": "哈瓦那棕猫",
            "Himalayan": "喜马拉雅猫",
            "Japanese Bobtail": "日本短尾猫",
            "Korat": "科拉特猫",
            "LaPerm": "拉邦猫",
            "Maine Coon": "缅因猫",
            "Manx": "曼岛猫",
            "Munchkin": "曼基康猫",
            "Nebelung": "内华达猫",
            "Norwegian Forest Cat": "挪威森林猫",
            "Ocicat": "欧西猫",
            "Oriental": "东方短毛猫",
            "Persian": "波斯猫",
            "Pixie-bob": "精灵猫",
            "Ragamuffin": "褴褛猫",
            "Ragdoll": "布偶猫",
            "Russian Blue": "俄罗斯蓝猫",
            "Savannah": "萨凡纳猫",
            "Scottish Fold": "苏格兰折耳猫",
            "Selkirk Rex": "塞尔凯克卷毛猫",
            "Siamese": "暹罗猫",
            "Siberian": "西伯利亚猫",
            "Singapura": "新加坡猫",
            "Snowshoe": "雪鞋猫",
            "Somali": "索马里猫",
            "Sphynx": "斯芬克斯猫(无毛)",
            "Tonkinese": "东奇尼猫",
            "Toyger": "玩具虎猫",
            "Turkish Angora": "土耳其安哥拉猫",
            "Turkish Van": "土耳其梵猫",
        }
        name_cn = cat_name_map.get(name_en, name_en)
        
        existing = db.query(models.PetBreed).filter(
            models.PetBreed.name == name_cn,
            models.PetBreed.species == "猫"
        ).first()
        if existing:
            continue
        
        weight = c.get('weight', {}).get('metric', '3-5')
        parts = weight.split('-')
        try:
            avg_w = (float(parts[0].strip()) + float(parts[-1].strip().replace('kg',''))) / 2
        except:
            avg_w = 4
        size = "大型" if avg_w >= 7 else "中型" if avg_w >= 4 else "小型"
        
        breed = models.PetBreed(
            name=name_cn,
            species="猫",
            size=size,
            common_issues=c.get('description', '')[:200] if c.get('description') else "",
            description=f"{c.get('temperament','')} | 寿命: {c.get('life_span','')} | 体重: {weight}kg | 来源: {c.get('origin','')}",
            image_url="",
        )
        db.add(breed)
        cat_imported += 1
    
    db.commit()
    print(f"  🎉 猫品种导入完成: {cat_imported} 个")
except Exception as e:
    print(f"  ❌ Cat API 失败: {e}")

# 统计
total = db.query(models.PetBreed).count()
dogs = db.query(models.PetBreed).filter(models.PetBreed.species == "狗").count()
cats = db.query(models.PetBreed).filter(models.PetBreed.species == "猫").count()

print(f"\n{'='*50}")
print(f"📊 品种导入完成!")
print(f"  犬种: {dogs}")
print(f"  猫种: {cats}")
print(f"  总计: {total}")
print(f"{'='*50}")

db.close()
