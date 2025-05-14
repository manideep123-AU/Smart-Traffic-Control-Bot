import serial
import time
import openai
import asyncio
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Your API Keys
openai.api_key = 'sk-xxxxxxxxxxx-xxxxxx-xxxxx-xxxxx'
TELEGRAM_BOT_TOKEN = '7794886386:xxxx-xxxx-xxxx'

# Attempt to connect to Arduino
try:
    arduino = serial.Serial('COM8', 9600, timeout=1)
    arduino_connected = True
    print("✅ Arduino connected.")
    time.sleep(2)
except Exception as e:
    arduino_connected = False
    print("⚠️ Arduino not connected. Using simulated data.")

# Global sensor data
latest_sensor_data = {
    "light": "Red",
    "cars": 0,
    "temp": 0.0,
    "gas": "Safe",
    "distance": 0.0
}

# Helper: calculate red signal time
def calculate_red_time(cars):
    if cars > 15:
        return 10
    elif cars > 5:
        return 20
    else:
        return 30

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚦 Hello! I'm your Smart Traffic Assistant Bot.\nAsk me about traffic, pollution, or safety tips.")

# /status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    red_time = calculate_red_time(int(latest_sensor_data["cars"]))
    await update.message.reply_text(
        f"🚥 Light: {latest_sensor_data['light']}\n"
        f"🚗 Cars: {latest_sensor_data['cars']}\n"
        f"🌡️ Temp: {latest_sensor_data['temp']} °C\n"
        f"🧪 Gas: {latest_sensor_data['gas']}\n"
        f"📏 Distance: {latest_sensor_data['distance']} m\n"
        f"🕒 Estimated Red Time: {red_time} seconds"
    )

# Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    red_time = calculate_red_time(int(latest_sensor_data["cars"]))
    prompt = f"""
You are a smart assistant at a traffic junction.
Sensor Data:
- Light: {latest_sensor_data['light']}
- Cars Waiting: {latest_sensor_data['cars']}
- Temperature: {latest_sensor_data['temp']} °C
- Gas Condition: {latest_sensor_data['gas']}
- Distance: {latest_sensor_data['distance']} meters
- Red Signal Time Estimate: {red_time} seconds

User Question: "{user_msg}"

Answer helpfully in one paragraph and add one safety tip at the end.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        print("❌ OpenAI error:", e)
        await update.message.reply_text("⚠️ I couldn't contact the AI server.")

# Sensor loop (runs in background)
async def sensor_loop():
    global latest_sensor_data
    while True:
        try:
            if arduino_connected and arduino.in_waiting:
                line = arduino.readline().decode(errors='ignore').strip()
                # Expected format: light:Red,cars:5,temp:28.5,gas:Safe,distance:3.2
                parts = line.split(',')
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':')
                        key = key.strip().lower()
                        value = value.strip()
                        if key == 'cars':
                            latest_sensor_data["cars"] = int(value)
                        elif key == 'temp':
                            latest_sensor_data["temp"] = float(value)
                        elif key == 'gas':
                            latest_sensor_data["gas"] = value
                        elif key == 'distance':
                            latest_sensor_data["distance"] = float(value)
                        elif key == 'light':
                            latest_sensor_data["light"] = value
                print("📡 Updated:", latest_sensor_data)
            else:
                # Simulate sensor data
                latest_sensor_data = {
                    "light": random.choice(["Red", "Green", "Yellow"]),
                    "cars": random.randint(0, 20),
                    "temp": round(random.uniform(25, 35), 1),
                    "gas": random.choice(["Safe", "Alert", "Danger"]),
                    "distance": round(random.uniform(2.0, 10.0), 1)
                }
                print("🧪 Simulated:", latest_sensor_data)

        except Exception as e:
            print("Sensor Read Error:", e)

        await asyncio.sleep(2)

# Main function to run bot and sensor loop
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run bot and sensor reader together
    async with app:
        task1 = asyncio.create_task(app.run_polling())
        task2 = asyncio.create_task(sensor_loop())
        await asyncio.gather(task1, task2)

# Setup and start the event loop
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
