"""宠物宝 (PetCare) — AI 问答 API"""
import logging
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
import urllib.request, json, os, yaml

from app.auth import get_current_user
from app import models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI问答"])

# 从 hermes 配置读取 API key
def _get_ark_key():
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config.get("model", {}).get("api_key", "")
    except Exception:
        return os.getenv("ARK_API_KEY", "")

ARK_KEY = _get_ark_key()
ARK_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

SYSTEM_PROMPT = """你是宠物宝(PetCare)的AI助手，专门解答宠物药品、食品、保健品相关问题。

请用中文回答，简洁专业，适合宠物主阅读。回答格式：
1. 先直接回答问题
2. 如有需要，补充注意事项
3. 最后可推荐相关产品类型

如果问题超出宠物健康范围，请礼貌说明你只能回答宠物相关问题。

注意：你的建议仅供参考，不能替代兽医诊断。涉及用药请务必咨询兽医。"""


class AskRequest(BaseModel):
    question: str
    context: str = ""


@router.post("/ask")
async def ask(
    req: AskRequest,
    user: models.User = Depends(get_current_user),
):
    """AI 问答（建议登录，未登录限频）"""
    if not ARK_KEY:
        raise HTTPException(500, "AI 服务未配置")

    user_msg = req.question
    if req.context:
        user_msg = f"用户正在查看「{req.context}」，问题：{req.question}"

    body = json.dumps({
        "model": "deepseek-v4-flash-260425",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 800,
        "temperature": 0.7,
    }).encode()

    try:
        r = urllib.request.Request(ARK_URL, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ARK_KEY}",
        })
        with urllib.request.urlopen(r, timeout=30) as resp:
            data = json.loads(resp.read())
            answer = data["choices"][0]["message"]["content"]
            return {"code": 0, "data": {"answer": answer}}
    except Exception as e:
        # 服务端日志记录完整错误，客户端只返回通用信息
        logger.error(f"AI service error: {e}")
        raise HTTPException(500, "AI 服务暂时不可用，请稍后重试")


class AnalyzeIngredientsRequest(BaseModel):
    ingredients_text: str
    product_name: str = ""
    product_type: str = "食品"


@router.post("/analyze-ingredients")
async def analyze_ingredients(
    req: AnalyzeIngredientsRequest,
    user: models.User = Depends(get_current_user),
):
    """AI 分析配料表安全性"""
    if not ARK_KEY:
        raise HTTPException(500, "AI 服务未配置")

    analyze_prompt = f"""请分析以下宠物{req.product_type}的配料表安全性：

产品名称：{req.product_name if req.product_name else '未知产品'}
配料表：
{req.ingredients_text}

请从以下维度评估：
1. **安全评分**（1-5分，5分最安全）
2. **主要风险成分**（列出有潜在风险的成分及原因）
3. **优质成分**（列出有益健康的成分）
4. **总体评价**（50字以内的总结）

请以 JSON 格式返回：
```json
{{
  "score": 4.2,
  "risk_ingredients": [
    {{"name": "成分名", "reason": "风险原因"}},
  ],
  "good_ingredients": ["成分1", "成分2"],
  "summary": "总体评价文字"
}}
```

只返回 JSON，不要其他内容。"""

    body = json.dumps({
        "model": "deepseek-v4-flash-260425",
        "messages": [
            {"role": "user", "content": analyze_prompt},
        ],
        "max_tokens": 1000,
        "temperature": 0.3,
    }).encode()

    try:
        r = urllib.request.Request(ARK_URL, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ARK_KEY}",
        })
        with urllib.request.urlopen(r, timeout=60) as resp:
            data = json.loads(resp.read())
            answer = data["choices"][0]["message"]["content"]
            
            # 尝试解析 JSON
            try:
                # 清理可能的 markdown 代码块标记
                answer = answer.replace("```json", "").replace("```", "").strip()
                analysis = json.loads(answer)
                return {"code": 0, "data": analysis}
            except json.JSONDecodeError:
                logger.error(f"AI 返回格式错误: {answer}")
                # 返回默认值
                return {
                    "code": 0,
                    "data": {
                        "score": 3.0,
                        "risk_ingredients": [],
                        "good_ingredients": [],
                        "summary": "AI 分析暂时不可用，请稍后再试"
                    }
                }
    except Exception as e:
        logger.error(f"AI analyze error: {e}")
        raise HTTPException(500, "AI 服务暂时不可用，请稍后重试")


@router.post("/parse-ingredient-image")
async def parse_ingredient_image(file: UploadFile = File(None)):
    """
    使用多模态 VLM 解析配料表图片
    
    上传图片，返回结构化的配料表数据：
    - ingredients: 原料组成列表
    - additives: 添加剂组成列表  
    - guaranteed_analysis: 成分分析保证值（粗蛋白、粗脂肪等）
    """
    if not file:
        raise HTTPException(400, "请上传图片文件")
    
    # 检查文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "只支持图片文件")
    
    # 保存临时文件
    import tempfile
    from pathlib import Path
    
    suffix = ".jpg"
    if file.filename and "." in file.filename:
        suffix = "." + file.filename.rsplit(".", 1)[-1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)
    
    try:
        # 调用 VLM 解析器
        from app.crawler.jd_vlm_ingredient_parser import IngredientExtractor
        extractor = IngredientExtractor()
        result = await extractor.parse_ingredient_image(tmp_path)
        
        if result is None:
            raise HTTPException(500, "无法从图片中解析出配料表")
        
        return {
            "code": 0,
            "data": result,
            "message": f"成功解析出 {len(result.get('ingredients', []))} 种原料，{len(result.get('additives', []))} 种添加剂"
        }
    finally:
        # 清理临时文件
        if tmp_path.exists():
            tmp_path.unlink()
