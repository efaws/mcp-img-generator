import os
import io
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
import boto3
import platform
import subprocess

from .logger import logger

mcp = FastMCP("img_generator")

def ensure_playwright_chromium():
    # 安装 chromium
    subprocess.run(
        ["playwright", "install", "chromium"],
        check=True
    )
    if platform.system().lower() == "linux":
        subprocess.run(["playwright", "install-deps"], check=True)
        logger.info("Linux 系统依赖安装完成")
    logger.info("Playwright Chromium 安装完成")

async def html_to_image(html_content: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        page = await browser.new_page(
            device_scale_factor=3.0  # 提高设备缩放因子以获得更清晰的图像
        )

        # 加载 HTML 内容
        await page.set_content(html_content, wait_until="networkidle")
        # content_size = await page.evaluate("""() => {
        #     const target = document.querySelector('body > div');
        #     if (!target) return null;
        #
        #     // 获取元素的完整尺寸（包括滚动区域）
        #     const fullWidth = Math.max(target.scrollWidth, target.offsetWidth, target.clientWidth);
        #     const fullHeight = Math.max(target.scrollHeight, target.offsetHeight, target.clientHeight);
        #
        #     const rect = target.getBoundingClientRect();
        #     const absoluteX = rect.left + window.scrollX;
        #     const absoluteY = rect.top + window.scrollY;
        #     return {
        #         documentPosition: {
        #             x: Math.round(absoluteX),
        #             y: Math.round(absoluteY)
        #         },
        #         dimensions: {
        #             width: Math.round(fullWidth),
        #             height: Math.round(fullHeight)
        #         }
        #     };
        # }""")
        # screenshot_options = {
        #     "type": "png",
        #     "full_page": False,
        #     "omit_background": False,
        #     "clip": {
        #     "x": content_size["documentPosition"]["x"]-2,
        #     "y": content_size["documentPosition"]["y"]-2,
        #     "width": content_size["dimensions"]["width"]+4,
        #     "height": content_size["dimensions"]["height"]+4
        # },
        #     "scale": "device"
        # }

        element = await page.query_selector('body > div')
        if not element:
            raise ValueError("Target div element not found")

        # 生成图片字节流
        image_data = await element.screenshot(type="png",
            omit_background=False,
            scale="device")
        await browser.close()

        return image_data

@mcp.tool(description="将html代码转换为图片并保存为本地PNG文件")
async def save_image_to_file(html_content: str) -> str:
    """
    将html代码转换为图片并保存为本地PNG文件
    
    Args:
        html_content: 完整的html代码
    
    Returns:
        保存后的完整文件路径
    """
    image_data = await html_to_image(html_content)
    output_dir = "./img"
    os.makedirs(output_dir, exist_ok=True)
    file_name=f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = os.path.join(output_dir, file_name)
    
    # 写入文件
    with open(file_path, 'wb') as f:
        f.write(image_data)

    return file_path

async def check_bucket(s3_client,bucket_name: str):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except:
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"桶 {bucket_name} 已创建")
        except Exception as e:
            return f"创建桶失败：{str(e)}"

@mcp.tool(description="将html转换为图片并上传到S3兼容的对象存储(minio,oss,aws等)")
async def upload_image_to_s3(html_content: str) -> str:
    """
    将html转换为图片并上传到S3兼容的对象存储(minio,oss,aws等)
    
    Args:
        html_content: 完整的html代码
    
    Returns:
        上传成功后的文件URL
    """
    config={
        "endpoint_url": os.getenv("ENDPOINT_URL"),
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_KEY")
    }
    bucket_name = os.getenv("BUCKET_NAME")
    logger.info(f"当前桶为：{bucket_name}")
    object_name = os.getenv("OBJECT_NAME")
    # 生成图片字节流
    image_data = await html_to_image(html_content)

    # 设置默认的对象名称
    if object_name is None:
        object_name = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    logger.info(f"当前对象名为：{object_name}")

    # 创建S3客户端
    s3_client = boto3.client(
        's3',
        **config
    )

    try:
        await check_bucket(s3_client,bucket_name)
        # 将图片字节流上传到S3
        s3_client.upload_fileobj(
            io.BytesIO(image_data),
            bucket_name,
            object_name
        )
        file_url = f"{config['endpoint_url']}/{bucket_name}/{object_name}"
        logger.info(f"文件已上传到S3，URL为：{file_url}")
        return file_url
    except Exception as e:
        return f"上传失败：{str(e)}"

def main():
    ensure_playwright_chromium()
    mcp.run()





