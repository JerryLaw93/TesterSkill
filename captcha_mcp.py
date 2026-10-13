from fastmcp import FastMCP
import ddddocr

mcp = FastMCP("captcha-ocr")

# 只初始化一次，别每次识别都加载模型
_ocr = ddddocr.DdddOcr()


@mcp.tool()
def recognize_captcha(image_path: str) -> str:
    """
    识别本地验证码图片里的文字。
    参数 image_path: 图片绝对路径，例如 /tmp/captcha.png
    返回: 识别出的字符串
    """
    with open(image_path, "rb") as f:
        return _ocr.classification(f.read())


@mcp.tool()
def recognize_captcha_base64(image_base64: str) -> str:
    """
    识别 base64 编码的验证码图片，返回识别出的字符串。
    """
    import base64
    return _ocr.classification(base64.b64decode(image_base64))


if __name__ == "__main__":
    mcp.run(transport="stdio")