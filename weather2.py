import requests
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

## Gmail Auth
GMAIL = ""
RECIPIENTS = [""] #, "friend@gmail.com"]
APP_PASSWORD = ""

## Weather
weather_url = "https://api.openweathermap.org/data/2.5/weather?lat=40.02&lon=-105.28&appid=&units=metric"
forecast_url = "https://api.openweathermap.org/data/2.5/forecast?lat=40.02&lon=-105.28&appid=&units=metric"

weather_data = requests.get(weather_url).json()
forecast_data = requests.get(forecast_url).json()

## Current weather
temp = round(weather_data["main"]["temp"])
feels_like = round(weather_data["main"]["feels_like"])
humidity = weather_data["main"]["humidity"]
description = weather_data["weather"][0]["description"].capitalize()
windspeed = round(weather_data["wind"]["speed"] * 3.6)
windangle = weather_data["wind"]["deg"]
today = date.today().strftime("%A, %B %d")

## Wind direction from degrees
def wind_direction(deg):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(deg / 45) % 8]

wind_dir = wind_direction(windangle)

## Parse forecast — one entry per day at noon
forecast_list = forecast_data["list"]
daily = {}
for entry in forecast_list:
    dt = datetime.datetime.fromtimestamp(entry["dt"])
    day_key = dt.strftime("%A")
    hour = dt.hour
    if day_key not in daily and hour >= 11:
        daily[day_key] = {
            "day": dt.strftime("%a %b %d"),
            "temp": round(entry["main"]["temp"]),
            "feels_like": round(entry["main"]["feels_like"]),
            "humidity": entry["main"]["humidity"],
            "description": entry["weather"][0]["description"].capitalize(),
            "windspeed": round(entry["wind"]["speed"]*3.6),
            "windangle": entry["wind"]["deg"],
            "wind_dir": wind_direction(entry["wind"]["deg"])
        }

## Hourly (3-hour intervals) for today only
today_date = date.today().strftime("%Y-%m-%d")
hourly_rows = ""
for entry in forecast_list:
    dt = datetime.datetime.fromtimestamp(entry["dt"])
    if dt.strftime("%Y-%m-%d") == today_date:
        hourly_rows += f"""
        <tr style="border-bottom: 1px solid #f9f9f9;">
            <td style="padding: 9px 8px; color: #555; font-weight: 500;">{dt.strftime("%I:%M %p")}</td>
            <td style="padding: 9px 8px; color: #333;">{entry['weather'][0]['description'].capitalize()}</td>
            <td style="padding: 9px 8px; color: #333; text-align:center;">{round(entry['main']['temp'])}°C</td>
            <td style="padding: 9px 8px; color: #888; text-align:center;">{entry['main']['humidity']}%</td>
            <td style="padding: 9px 8px; color: #888; text-align:center;">{round(entry['wind']['speed'], 1)} m/s</td>
            <td style="padding: 9px 8px; color: #888; text-align:center;">{wind_direction(entry['wind']['deg'])} {entry['wind']['deg']}°</td>
        </tr>
        """


## Build forecast rows HTML
forecast_rows = ""
for day, d in list(daily.items())[:5]:
    forecast_rows += f"""
        <tr>
            <td style="padding: 10px 8px; color: #555; font-weight: 500;">{d['day']}</td>
            <td style="padding: 10px 8px; color: #333;">{d['description']}</td>
            <td style="padding: 10px 8px; color: #333; text-align:center;">{d['temp']}°C</td>
            <td style="padding: 10px 8px; color: #888; text-align:center;">{d['humidity']}%</td>
            <td style="padding: 10px 8px; color: #888; text-align:center;">{d['windspeed']} Kmph {d['wind_dir']}</td>
        </tr>
    """

## HTML Email
html = f"""
<html>
<body style="font-family: sans-serif; background: #f0f4ff; padding: 2rem; margin: 0;">
<div style="max-width: 580px; margin: auto;">

  <!-- Header -->
  <div style="margin-bottom: 1rem;">
    <p style="color: #888; font-size: 13px; margin: 0;">{today}</p>
    <h2 style="margin: 0.25rem 0 0; color: #222;">Good morning! 🌤️</h2>
  </div>

  <!-- Current weather card -->
  <div style="background: white; border-radius: 16px; padding: 1.75rem; margin-bottom: 1rem;">
    <p style="font-size: 13px; color: #888; margin: 0 0 4px;">Boulder, Colorado</p>
    <div style="display: flex; align-items: flex-end; gap: 1rem;">
      <p style="font-size: 64px; font-weight: 500; margin: 0; color: #222; line-height: 1;">{temp}°C</p>
      <p style="font-size: 16px; color: #555; margin: 0 0 10px;">{description}</p>
    </div>
    
    <!-- Details row -->
    <div style="display: flex; gap: 0; margin-top: 1.25rem; border-top: 1px solid #f0f0f0; padding-top: 1rem;">
      <div style="flex: 1; text-align: center;">
        <p style="font-size: 11px; color: #aaa; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.05em;">Feels like</p>
        <p style="font-size: 16px; font-weight: 500; color: #333; margin: 0;">{feels_like}°C</p>
      </div>
      <div style="flex: 1; text-align: center; border-left: 1px solid #f0f0f0;">
        <p style="font-size: 11px; color: #aaa; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.05em;">Humidity</p>
        <p style="font-size: 16px; font-weight: 500; color: #333; margin: 0;">{humidity}%</p>
      </div>
      <div style="flex: 1; text-align: center; border-left: 1px solid #f0f0f0;">
        <p style="font-size: 11px; color: #aaa; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.05em;">Wind</p>
        <p style="font-size: 16px; font-weight: 500; color: #333; margin: 0;">{windspeed} Kmph</p>
      </div>
      <div style="flex: 1; text-align: center; border-left: 1px solid #f0f0f0;">
        <p style="font-size: 11px; color: #aaa; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.05em;">Direction</p>
        <p style="font-size: 16px; font-weight: 500; color: #333; margin: 0;">{wind_dir} {windangle}°</p>
      </div>
    </div>
  </div>

   <!-- Hourly card -->
  <div style="background: white; border-radius: 16px; padding: 1.75rem; margin-bottom: 1rem;">
    <p style="font-size: 13px; font-weight: 500; color: #888; margin: 0 0 1rem; text-transform: uppercase; letter-spacing: 0.05em;">Today — 3-Hour Intervals</p>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
      <thead>
        <tr style="border-bottom: 1px solid #f0f0f0;">
          <th style="padding: 6px 8px; text-align: left; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Time</th>
          <th style="padding: 6px 8px; text-align: left; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Condition</th>
          <th style="padding: 6px 8px; text-align: center; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Temp</th>
          <th style="padding: 6px 8px; text-align: center; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Humidity</th>
          <th style="padding: 6px 8px; text-align: center; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Wind</th>
          <th style="padding: 6px 8px; text-align: center; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Direction</th>
        </tr>
      </thead>
      <tbody>
        {hourly_rows}
      </tbody>
    </table>
  </div>

  <!-- Forecast card -->
  <div style="background: white; border-radius: 16px; padding: 1.75rem;">
    <p style="font-size: 13px; font-weight: 500; color: #888; margin: 0 0 1rem; text-transform: uppercase; letter-spacing: 0.05em;">5-Day Forecast</p>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
      <thead>
        <tr style="border-bottom: 1px solid #f0f0f0;">
          <th style="padding: 6px 8px; text-align: left; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Day</th>
          <th style="padding: 6px 8px; text-align: left; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Condition</th>
          <th style="padding: 6px 8px; text-align: center; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Temp</th>
          <th style="padding: 6px 8px; text-align: center; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Humidity</th>
          <th style="padding: 6px 8px; text-align: center; font-size: 11px; color: #aaa; font-weight: 500; text-transform: uppercase;">Wind</th>
        </tr>
      </thead>
      <tbody>
        {forecast_rows}
      </tbody>
    </table>
  </div>

  <p style="text-align: center; font-size: 12px; color: #bbb; margin-top: 1.5rem;">Sent automatically by your Python dashboard</p>
</div>
</body>
</html>
"""

## Send
msg = MIMEMultipart("alternative")
msg["Subject"] = f"🌤️ Morning Weather · {today}"
msg["From"] = GMAIL
msg["To"] = ", ".join(RECIPIENTS)
msg.attach(MIMEText(html, "html"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(GMAIL, APP_PASSWORD)
    server.sendmail(GMAIL, RECIPIENTS, msg.as_string())

print("Email sent!")
print(weather_data)