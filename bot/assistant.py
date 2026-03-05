import discord
import anthropic
import os
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')
CHANNEL_NAME = 'assistant'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SYSTEM_PROMPT = """你是 liaoshihang 的个人博客写手助手。博客使用 Hugo + Dream 主题，风格：个人视角，有观点，技术与感受结合，中文写作。

收到主题后，输出一篇完整的 Hugo Markdown 文章，包括：

1. frontmatter（严格按以下格式）：
---
title: "文章标题"
date: {date}
lastmod: {date}
author: liaoshihang
categories:
  - 分类
tags:
  - 标签1
  - 标签2
draft: false
---

2. 摘要段落（100字以内，放在 <!--more--> 之前）

3. <!--more-->

4. 正文（## 分节，800-1200字）

只输出 Markdown 文章本身，不要加任何解释或前言。"""

@client.event
async def on_ready():
    print(f'✅ Bot 已上线：{client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.name != CHANNEL_NAME:
        return
    if not message.content.strip():
        return

    async with message.channel.typing():
        try:
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

            response = claude.messages.create(
                model='claude-opus-4-6',
                max_tokens=4096,
                system=SYSTEM_PROMPT.replace('{date}', date_str),
                messages=[{
                    'role': 'user',
                    'content': f'主题：{message.content}'
                }]
            )

            draft = response.content[0].text
            filename = f'draft-{now.strftime("%Y%m%d-%H%M%S")}.md'
            file = discord.File(io.StringIO(draft), filename=filename)
            await message.reply(
                f'✅ 草稿已生成，下载后放入 `content/posts/` 即可发布。',
                file=file
            )

        except Exception as e:
            await message.reply(f'❌ 生成失败：{str(e)}')

client.run(DISCORD_TOKEN)
