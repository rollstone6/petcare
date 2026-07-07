#!/usr/bin/env python3
"""批量生成动漫风格宠物头像 - 使用 Pollinations.ai，串行+长间隔"""
import os, sys, json, subprocess, time, urllib.parse
from pathlib import Path

OUTPUT_DIR = Path("/root/workspace/petcare/frontend/public/avatars")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BREEDS = [
    ("金毛寻回犬", "Golden Retriever dog"),
    ("拉布拉多寻回犬", "Labrador Retriever dog"),
    ("德国牧羊犬", "German Shepherd dog"),
    ("哈士奇", "Siberian Husky dog"),
    ("阿拉斯加雪橇犬", "Alaskan Malamute dog"),
    ("柯基犬", "Welsh Corgi dog"),
    ("柴犬", "Shiba Inu dog"),
    ("边境牧羊犬", "Border Collie dog"),
    ("法国斗牛犬", "French Bulldog dog"),
    ("贵宾犬_泰迪", "Toy Poodle teddy bear dog"),
    ("比熊犬", "Bichon Frise dog"),
    ("博美犬", "Pomeranian dog"),
    ("吉娃娃", "Chihuahua dog"),
    ("约克夏梗", "Yorkshire Terrier dog"),
    ("英国短毛猫", "British Shorthair cat"),
    ("美国短毛猫", "American Shorthair cat"),
    ("异国短毛猫_加菲", "Exotic Shorthair Garfield cat"),
    ("暹罗猫", "Siamese cat blue eyes"),
    ("布偶猫", "Ragdoll cat blue eyes fluffy"),
    ("波斯猫", "Persian cat long fur"),
    ("缅因猫", "Maine Coon cat large fluffy"),
    ("挪威森林猫", "Norwegian Forest Cat"),
    ("中华田园猫_橘猫", "Orange tabby cat"),
    ("斯芬克斯猫_无毛", "Sphynx hairless cat"),
    ("曼基康矮脚猫", "Munchkin cat short legs"),
    ("苏格兰折耳猫", "Scottish Fold cat"),
    ("英国长毛猫", "British Longhair cat"),
    ("蓝猫_英短", "Russian Blue cat"),
    ("金渐层", "Golden shaded British Shorthair cat"),
    ("银渐层", "Silver shaded British Shorthair cat"),
    ("罗威纳犬", "Rottweiler dog"),
    ("巴哥犬", "Pug dog"),
    ("西施犬", "Shih Tzu dog"),
    ("马尔济斯犬", "Maltese dog white fluffy"),
    ("腊肠犬", "Dachshund dog long body"),
    ("巴吉度猎犬", "Basset Hound dog long ears"),
    ("威尔士柯基犬", "Pembroke Welsh Corgi dog"),
    ("雪纳瑞犬", "Schnauzer dog with beard"),
    ("中华田园犬", "Chinese rural dog"),
    ("阿拉斯加犬", "Alaskan Malamute dog"),
    ("卡斯罗犬", "Cane Corso dog"),
    ("金毛犬", "Golden Retriever puppy"),
    ("牛头梗", "Bull Terrier dog"),
    ("喜乐蒂牧羊犬", "Shetland Sheepdog"),
    ("大白熊犬", "Great Pyrenees dog white fluffy"),
    ("萨摩耶", "Samoyed dog white fluffy"),
    ("松狮犬", "Chow Chow dog"),
    ("秋田犬", "Akita Inu dog"),
    ("比格犬", "Beagle dog"),
    ("杜宾犬", "Doberman Pinscher dog"),
    ("布偶猫_海双", "Seal bicolor Ragdoll cat"),
    ("暹罗猫_重点色", "Seal point Siamese cat"),
    ("加拿大无毛猫", "Canadian Sphynx hairless cat"),
    ("德文卷毛猫", "Devon Rex cat curly"),
    ("美国卷耳猫", "American Curl cat"),
    ("俄罗斯蓝猫", "Russian Blue cat green eyes"),
    ("伯曼猫", "Birman cat blue eyes"),
    ("阿比西尼亚猫", "Abyssinian cat"),
    ("孟加拉豹猫", "Bengal cat spotted"),
    ("中华田园猫_狸花", "Dragon Li tabby cat"),
    ("中华田园猫_三花", "Calico cat"),
    ("中华田园猫_奶牛", "Tuxedo black white cat"),
    ("荷兰垂耳兔", "Holland Lop rabbit"),
    ("迷你雷克斯兔", "Mini Rex rabbit"),
    ("安哥拉兔", "Angora rabbit fluffy"),
    ("侏儒兔", "Netherland Dwarf rabbit"),
    ("荷兰兔", "Dutch rabbit black white"),
    ("金丝熊仓鼠", "Syrian hamster golden"),
    ("三线仓鼠", "Djungarian hamster"),
    ("一线仓鼠", "Campbell dwarf hamster"),
    ("罗伯罗夫斯基仓鼠", "Roborovski dwarf hamster"),
    ("虎皮鹦鹉", "Budgerigar parakeet green"),
    ("玄凤鹦鹉", "Cockatiel bird"),
    ("牡丹鹦鹉", "Lovebird colorful parrot"),
    ("金丝雀", "Canary bird yellow"),
    ("文鸟", "Java Sparrow bird"),
    ("金鱼", "Goldfish orange"),
    ("锦鲤", "Koi fish colorful"),
    ("斗鱼", "Betta fish purple"),
    ("孔雀鱼", "Guppy fish colorful"),
    ("豹纹守宫", "Leopard Gecko lizard"),
    ("鬃狮蜥", "Bearded Dragon lizard"),
    ("巴西龟", "Red-eared slider turtle"),
    ("草龟", "Chinese pond turtle"),
    ("非洲迷你刺猬", "African pygmy hedgehog"),
    ("雪貂", "Ferret"),
    ("豚鼠", "Guinea pig"),
    ("龙猫", "Chinchilla"),
    ("蜜袋鼯", "Sugar glider"),
]

PROMPT_TEMPLATE = "A cute anime-style chibi portrait of a {breed}, kawaii illustration, round face, big sparkling eyes, soft pastel gradient background, professional pet portrait, studio ghibli inspired, adorable and detailed, centered composition, high quality digital art"

def download(url, output_path, timeout=60):
    try:
        result = subprocess.run(
            ["curl", "-sL", "-o", str(output_path), "--max-time", str(timeout), "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=timeout + 10
        )
        http_code = result.stdout.strip()
        if output_path.exists():
            size = output_path.stat().st_size
            # Check if it's an error JSON
            if size < 2000:
                content = output_path.read_text(errors='ignore')
                if 'error' in content or 'Too Many' in content:
                    output_path.unlink(missing_ok=True)
                    return False, "rate limited"
            if size > 5000:
                return True, f"{size/1024:.1f}KB"
            output_path.unlink(missing_ok=True)
        return False, f"http={http_code}"
    except Exception as e:
        output_path.unlink(missing_ok=True)
        return False, str(e)

def main():
    total = len(BREEDS)
    success = 0
    failed = []
    rate_limited = 0

    print(f"=== 开始生成 {total} 个动漫风格头像 ===", flush=True)

    for i, (name_cn, name_en) in enumerate(BREEDS, 1):
        output_file = OUTPUT_DIR / f"{name_cn}.png"

        if output_file.exists() and output_file.stat().st_size > 5000:
            print(f"[{i:2d}/{total}] ✓ {name_cn} (已存在)", flush=True)
            success += 1
            continue

        prompt = PROMPT_TEMPLATE.format(breed=name_en)
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&seed={i*13+42}"

        print(f"[{i:2d}/{total}] → {name_cn}...", end=" ", flush=True)

        ok, info = download(url, output_file)

        if ok:
            print(f"✓ {info}", flush=True)
            success += 1
        else:
            print(f"✗ {info}", flush=True)
            failed.append(name_cn)
            if "rate" in info:
                rate_limited += 1
                # Rate limited - wait longer
                print(f"       ⏳ 被限流，等待10秒...", flush=True)
                time.sleep(10)
                # Retry once
                ok2, info2 = download(url, output_file)
                if ok2:
                    print(f"       ✓ 重试成功 {info2}", flush=True)
                    success += 1
                    failed.pop()
                else:
                    print(f"       ✗ 重试失败 {info2}", flush=True)

        # 间隔3秒，避免限流
        time.sleep(3)

    print(f"\n===== 完成 =====", flush=True)
    print(f"成功: {success}/{total}", flush=True)
    if failed:
        print(f"失败 ({len(failed)}): {chr(10).join(failed)}", flush=True)

    # 保存结果
    result = {"success": success, "total": total, "failed": failed}
    with open("/tmp/anime_avatar_result.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
