import os
import discord
from discord.ext import commands
from server import server_thread
from rembg import remove
from PIL import Image
from io import BytesIO
import numpy as np

import dotenv

dotenv.load_dotenv()

# ---- 環境変数読み込み ----
DISCORD_TOKEN = os.environ.get("TOKEN")

# ---- Discord Bot 設定 ----
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
  # Bot 自身のメッセージは無視
  if message.author == bot.user:
    return

  # 画像が添付されているか確認
  if message.attachments:
    for attachment in message.attachments:
      if attachment.filename.lower().endswith(
          (".png", ".jpg", ".jpeg", ".webp")):

        await message.channel.send("画像を処理中です… ")

        try:
          # --- 添付画像の取得 ---
          img_bytes = await attachment.read()

          # --- 背景削除実行 ---
          input_img = Image.open(BytesIO(img_bytes))
          output_img = remove(input_img, model_name='u2netp')
        

          # --- 返送用にバイトに変換 ---
          buffer = BytesIO()
          if isinstance(output_img, bytes):
            buffer.write(output_img)
          elif isinstance(output_img, Image.Image):
            output_img.save(buffer, format="PNG")
          elif isinstance(output_img, np.ndarray):
            output_img_pil = Image.fromarray(output_img)
            output_img_pil.save(buffer, format="PNG")
          else:
            raise ValueError(
                f"Unexpected output type from rembg: {type(output_img)}")
          buffer.seek(0)

          # --- 返送 ---
          file = discord.File(buffer, filename="bg_removed.png")
          await message.channel.send("背景を削除しました！", file=file)

        except Exception as e:
          print(f"Error processing image '{attachment.filename}': {e}")
          await message.channel.send("画像の処理中にエラーが発生しました。別の画像をお試しください。")

  await bot.process_commands(message)


if not DISCORD_TOKEN:
  print("Error: DISCORD_TOKEN environment variable not set")
  exit(1)

server_thread()
bot.run(DISCORD_TOKEN)
