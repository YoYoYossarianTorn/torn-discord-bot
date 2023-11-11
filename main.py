import os
import discord
from keep_alive import keep_alive
import requests
import asyncio

'''
shoplifting
'''
BASE_MESSAGE = "Shoplift now for special ammo https://www.torn.com/loader.php?sid=crimes#/shoplifting"
# guardsDown = "Guards are gone at Big Al's - "
# camerasDown = "Cameras are down at Big Al's - "
# bothDown = "Cameras AND guards are down at Big Al's, holy shit - "

api_url = "https://api.torn.com/torn/"
api_url_playerInfo = "https://api.torn.com/user/"
api_key = os.environ.get('PUBLIC_API')
response = requests.get(api_url, params={'key': api_key})
client = discord.Client(intents=discord.Intents.all())
CHECK_STATUS_DELAY = 300 #how many seconds to wait before checking the status check


# Define your user ID (to send DM)
YOUR_USER_ID = 698031280008331367  # Replace 'YOUR_USER_ID' with your Discord user ID


@client.event
async def on_message(message):
  # Check if the message author is not the bot itself
  if message.author != client.user:
    # Check if the message was sent in a DM
    if isinstance(message.channel, discord.DMChannel):
      # Check if the message content is asking for the Big Als status
      if message.content.lower() == 'bigals status':
        response = requests.get(api_url, params={'key': api_key})
        if response.status_code == 200:
          data = response.json()
          # Access the status of cameras and guards at Big Al's
          big_als_data = data.get('shoplifting', {}).get('big_als', [])
          cameras_disabled = any(
              item['title'] == 'Four cameras' and not item['disabled']
              for item in big_als_data)
          guards_disabled = any(
              item['title'] == 'Two guards' and not item['disabled']
              for item in big_als_data)
          status_message = f'Cameras at Big Al\'s: {"Offline" if cameras_disabled else "Online"}\n'
          status_message += f'Guards at Big Al\'s: {"Gone" if guards_disabled else "On duty"}'
          await message.channel.send(status_message)
        else:
          await message.channel.send(
              f"Failed to retrieve data. Status code: {response.status_code}")


# sends status update for bigals when the cameras are off or the guards are away
async def send_bigals_status():
  await client.wait_until_ready()  # Wait for the bot to be ready

  while not client.is_closed():
    response = requests.get(api_url, params={'key': api_key})
    if response.status_code == 200:
      data = response.json()

      # Access the status of cameras and guards at Big Al's
      big_als_data = data.get('shoplifting', {}).get('big_als', [])
      cameras_disabled = any(
          item['title'] == 'Four cameras' and not item['disabled']
          for item in big_als_data)
      guards_disabled = any(
          item['title'] == 'Two guards' and not item['disabled']
          for item in big_als_data)

      status_message = f'Cameras at Big Al\'s: {"Offline" if cameras_disabled else "Online"}\n'
      status_message += f'Guards at Big Al\'s: {"Gone" if guards_disabled else "On duty"}'
      user = await client.fetch_user(YOUR_USER_ID)
      if cameras_disabled or guards_disabled:
        await user.send(status_message + "\n" + BASE_MESSAGE)
      else:
        await user.send("Cameras and guards are back at Big Al's. Sad.")
    await asyncio.sleep(CHECK_STATUS_DELAY) 


@client.event
async def on_ready():
  print("I'm in")
  print(client.user)
  client.loop.create_task(send_bigals_status())


# Start the bot
keep_alive()
my_secret = os.environ['DISCORD_BOT_SECRET']
client.run(my_secret)
