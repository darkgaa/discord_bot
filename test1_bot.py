import discord  
from discord.ext import commands
from googleapiclient.discovery import build
import yt_dlp
import random
import asyncio
from PIL import Image, ImageDraw, ImageFont
import io


intents = discord.Intents.default()
intents.voice_states = True  # 음성 상태 관련 인텐트 활성화

bot = commands.Bot(command_prefix='`',intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot)) #봇이 실행되면 콘솔창에 표시


@bot.command()
async def hello(ctx):
    await ctx.send("hello")

@bot.command()
async def CTRL동아리(ctx):
    await ctx.send("안화고 1짱 동아리")


#주사위 보드게임
@bot.command()
async def 주사위(ctx):
    result, _color, bot, user = dice()
    embed = discord.Embed(title = "주사위 게임 결과", description = None, color = _color)
    embed.add_field(name = "CTRL 대표 봇의 숫자", value = ":game_die: " + bot, inline = True)
    embed.add_field(name = ctx.author.name + "의 숫자", value = ":game_die: " + user, inline = True)
    embed.set_footer(text="결과 : " + result)
    await ctx.send(embed=embed)

def dice():
    a = random.randrange(1,7)
    b = random.randrange(1,7)
    if a > b:
        return "패배", 0xff0000, str(a), str(b)
    elif a < b:
        return "승리", 0x0000ff, str(a), str(b)
    elif a == b:
        return "무승부", 0xffff00, str(a), str(b)

        
#음성채팅 입퇴장
@bot.command()
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        await ctx.send(f"{voice_client.channel} 채널에 입장합니다")
    else:
        await ctx.send("연결을 한 뒤 실행해주세요")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("채널에서 나갑니다")
    else:
        await ctx.send("채널에 들어와있지 않습니다 ")

#음악 재생
async def play(ctx, *, query):
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        voice_client = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extract_flat': True,
        'quiet': True,
        'api_key': 'AIzaSyDfkvYkBjMfwZHk9-1EGkHMRLATo2Z3pyk'  # 유튜브 API 키 입력
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        if 'entries' in info:
            url = info['entries'][0]['url']
            if not ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            ctx.voice_client.play(discord.FFmpegPCMAudio(url))
            
            await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Music"))
            await ctx.send(f"Now playing: {info['entries'][0]['title']}")
        else:
            await ctx.send("No search results found.")

#일시정지
@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused the music.")

#재생
@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")

#정지
@bot.command()
async def stop(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped the music.")

#스킵
@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")


#타이머
@bot.command()
async def set_timer(ctx, seconds: int):    #!set_timer [초] 명령어를 사용하여 타이머를 설정합니다.
    await ctx.send(f"타이머가 {seconds}초로 설정되었습니다.")
    await asyncio.sleep(seconds)
    await ctx.send(f"{ctx.author.mention}, {seconds}초의 타이머가 종료되었습니다!")


#베팅
user_points= {}
@bot.command()
async def flip_coin_image(ctx):
    """!flip_coin_image 명령어를 사용하여 동전 던지기 게임을 이미지로 플레이합니다."""
    if ctx.author not in user_points:
        user_points[ctx.author] = 100  # 초기 포인트 설정 (원하는 값으로 변경 가능)

    # 무작위로 앞면 또는 뒷면 결정
    coin_result = random.choice(["앞면", "뒷면"])

    # 동전 이미지 생성
    image = create_coin_flip_image(coin_result)

    # 이미지를 Discord 메시지로 전송
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    file = discord.File(image_bytes, filename="coin_flip.png")

    await ctx.send(f"{ctx.author.mention}, 동전을 던집니다!", file=file)

def create_coin_flip_image(result):
    """동전 던지기 결과를 나타내는 이미지를 생성합니다."""
    image_size = (200, 200)
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text = f"결과: {result}"
    text_width, text_height = draw.textsize(text, font)
    draw.text(
        ((image_size[0] - text_width) / 2, (image_size[1] - text_height) / 2),
        text,
        fill="black",
        font=font,
    )
    return image


#명령어 오류
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
    	await ctx.send("명령어를 찾지 못했습니다")



bot.run('토큰') #토큰
