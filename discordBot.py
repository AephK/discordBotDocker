#general packages
import os, logging, random, math, sys, platform, urllib.request, subprocess
#media handling packages
import yt_dlp, ffmpeg
#platform api packages
import discord
from discord.ext import commands

#platform video size limit
videoMaxSize = 10000 #max size in Kb

#use fixed bitrate for audio in Kb/s
audioBitrate=48

#set audio codec
audioCodec="libopus"

#set video codec
videoCodec="hevc_qsv"

#factor to reduce max size by to account for codec overheads
overhead = 0.95

cwd = os.getcwd() + '/'
cookieFile = 'cookies.txt'
deleteTemp = 'rm -f temp.*'
scriptDir = cwd
token = os.getenv("DISCORD_BOT_TOKEN")

#####logging config
stdout_path = os.path.join(scriptDir, 'discordBot.log')
stderr_path = os.path.join(scriptDir, 'discordBotErr.log')

try:
    os.remove(stdout_path)
except FileNotFoundError:
    pass

try:
    os.remove(stderr_path)
except FileNotFoundError:
    pass

sys.stdout = open(stdout_path, "w")
sys.stderr = open(stderr_path, "w")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#####

print(cwd)

description = '''intrvBot!

User ?v [url] to send an inline video.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

@bot.command()
async def v(ctx, url: str):
    await ctx.message.delete()
    subprocess.Popen(deleteTemp, shell=True).wait()
    ydl_opts = {'format_sort' : ['res:1280', '+br'],
                'cookiefile' : cookieFile,
                'merge_output_format' : 'mp4',
                'outtmpl': cwd + 'temp.mp4'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    originalSize = int(ffmpeg.probe(cwd + "temp.mp4")["format"]["size"])

    if (originalSize > videoMaxSize):
        try:
            print("File too big. Resizing...")
            print("Renaming mp4 to temp")
            os.rename(cwd + "temp.mp4", cwd + "temp.temp")

            #Get video length and calculate max video bitrate in order to come in under 50MB (25MB?)
            sourceLength = float(ffmpeg.probe(cwd + "temp.temp")["format"]["duration"])
            #account for overhead, reduce max size
            finalMaxSize = (videoMaxSize * overhead)
            #get finalMaxBitrate using file's length (and convert to Bytes)
            finalMaxBitrate = (((finalMaxSize-audioBitrate)/(sourceLength))*8)
            videoBitrate = finalMaxBitrate
            #if video birate is higher than 2Mb/s, set to 2Mb/s to avoid unnecessarily large files 
            videoBitrate = min(finalMaxBitrate, 2000)

            in_path = os.path.join(cwd, 'temp.temp')
            out_path = os.path.join(cwd, 'temp.mp4')
            bufsize = finalMaxBitrate * 2

            inp = ffmpeg.input(in_path)

            v = (
                inp.video
                #.filter('pad', 'ceil(iw/2)*2', 'ceil(ih/2)*2')  #make width/height even
            )

            a = inp.audio  # take the audio stream unchanged (or add filters if you need)

            stream = (
               ffmpeg
                .output(
                   v, a, out_path,
                    vcodec=f'{videoCodec}',
                    acodec=f'{audioCodec}',
                    **{
                        'b:v': f'{videoBitrate}k',
                        'b:a': f'{audioBitrate}k',
                        'maxrate': f'{math.floor(finalMaxBitrate)}k',
                        'bufsize': f'{bufsize}k',
                        'extbrc': '1',
                        'look_ahead_depth': '80',
                        'vf': 'scale=1280:-1'
                    }
                )
                .global_args('-y', '-hwaccel', 'qsv', '-hwaccel_output_format', 'qsv')
            )

            stream.run(overwrite_output=True)


        except Exception as e:
            print(f"Error: {e}", flush=True)
            print("renaming temp to mp4")
            if os.path.isfile(cwd + "temp.temp"):
                os.rename(cwd + "temp.temp", cwd + "temp.mp4")

        except Exception as e:
            print(f"Error: {e}", flush=True)
            print("renaming temp to mp4")
            if os.path.isfile(cwd + "temp.temp"):
                os.rename(cwd + "temp.temp", cwd + "temp.mp4")

    file = open(cwd + 'temp.mp4', 'rb')
    caption='Sent by: ' + str(ctx.author.display_name)
    await ctx.send(caption, file=discord.File(cwd + "temp.mp4"), silent=True)
    
    subprocess.Popen(deleteTemp, shell=True).wait()

bot.run(token)
