from PIL import Image, ImageDraw, ImageFont
import time
import calendar
import requests
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')

def Read_todo(fileName):
    todo = []
    fileName = fileName + '.txt'
    if os.path.exists(fileName):
        with open(fileName, mode='r',encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n').split("** ")
                todo.append(line)
    else:
        with open(fileName, mode='w') as f:
            print('without local message')
    return todo

def Read_list(fileName):
    todo = []
    fileName = fileName + '.txt'
    if os.path.exists(fileName):
        with open(fileName, mode='r',encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n')
                todo.append(line)
    else:
        with open(fileName, mode='w') as f:
            print('without local message')
    return todo

# font
font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'),18)
font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
font110 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 110)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'),35)
font25 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 25)
font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
font_cal = ImageFont.truetype(os.path.join(picdir, 'FreeMonoBold.ttf'), 18)
font_weather_icons = ImageFont.truetype(os.path.join(picdir, 'meteocons-webfont.ttf'), 42)

icons_list = {u'01d':u'B',u'01n':u'C',u'02d':u'H',u'02n':u'I',u'03d':u'N',u'03n':u'N',u'04d':u'Y',u'04n':u'Y',u'09d':u'R',u'09n':u'R',u'10d':u'R',u'10n':u'R',u'11d':u'P',u'11n':u'P',u'13d':u'W',u'13n':u'W',u'50d':u'M',u'50n':u'W'}

def generate_dates():
    WEATHER_API = '157ddafe99ba80ecb2d8c4d8257fc1c8'
    weather_response = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"appid":WEATHER_API, "q":'Hangzhou'}).json()
    forecast_response = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={"appid":WEATHER_API, "q":'Hangzhou'}).json()
    current_weather = weather_response['weather'][0]['main']
    current_icon = weather_response['weather'][0]['icon']
    current_temp = str(int(weather_response['main']['temp']) - 273) + 'C'
    forecast_weather = forecast_response['list'][0]['weather'][0]['main']
    forecast_icon = forecast_response['list'][0]['weather'][0]['icon']
    forecast_temp_min_max = str(int(forecast_response['list'][0]['main']['temp_min']) - 273) + 'C - ' + str(int(forecast_response['list'][0]['main']['temp_max']) - 273) + 'C'

    # Drawing on the Horizontal image
    Img = Image.new('RGB', (648, 480), '#ffffff')
    Cat_Img = Image.open(os.path.join(picdir, 'cat.jpg'))
    Heart_Img = Image.open(os.path.join(picdir, 'heart.jpg')) 
    Img.paste(Cat_Img, (0,420))  
    Img.paste(Heart_Img, (30,410)) 

    draw = ImageDraw.Draw(Img)

    total = 14
    todos = Read_todo('todo')

    draw.rectangle((245,0, 648, 55), fill = 'red') # Task area banner
    draw.text((250,12), "Course Tasks", font = font30, fill = 'white') # Task text
    height = 60
    if len(todos) == 0:
        todos = [('暂无课程任务','烦请尽情享乐')]
    if len(todos) > 7:
        todos = todos[:7]
    for idx,todo in enumerate(todos):
        if len(todo[0]) >= 15:
            todo[0] = todo[0][:14] + '...'
        draw.text((248,height), todo[0], font = font18, fill = 0) # Task text
        draw.text((500,height), todo[1], font = font18, fill = 'red') # Task text
        draw.line((245,height+23, 648, height+23), fill = 0)
        height += 25 

    draw.rectangle((245,240-(total/2-1-idx)*25, 648, 295-(total/2-1-idx)*25), fill = 'red') # Task area banner
    draw.text((250,252-(total/2-1-idx)*25), "Fun", font = font30, fill = 'white') # Task text
    update = Read_list('spider')
    height = 300 - (total/2-1-idx)*25
    if len(update) > (total-idx -1) :
        update = update[:(total-idx -1)]
    for idx,up in enumerate(update):
        if len(up) >= 25:
            if up[-1] == '*':
                head = ''
                for c in up:
                    head = head + c
                    if c == ' ':
                        break
                up = head + up[-12:-10] + '集 已更新'
            else:
                up = up[:22] + '...' + up[-3:]
        draw.text((248,height),up, font = font18, fill = 0) # Task text
        draw.line((245,height+23, 648, height+23), fill = 0)
        height += 25 

    if idx < total - len(todos):
        for i in range(total - len(todos)-len(update)):
            draw.line((245,height+23, 648, height+23), fill = 0)
            height += 25 

    # Calendar strings to be displayed
    day_str = time.strftime("%A")
    day_number = time.strftime("%d")
    month_str = time.strftime("%B") + ' ' + time.strftime("%Y")
    month_cal = str(calendar.month(int(time.strftime("%Y")), int(time.strftime("%m"))))
    month_cal = month_cal.split("\n",1)[1]
    update_moment = time.strftime("%I") + ':' + time.strftime("%M") + ' ' + time.strftime("%p")

    cal_width = 240
    # This section is to center the calendar text in the middle
    w_day_str,h_day_str = font35.getsize(day_str)
    x_day_str = (cal_width / 2) - (w_day_str / 2)

    # The settings for the Calenday today number in the middle
    w_day_num,h_day_num = font110.getsize(day_number)
    x_day_num = (cal_width / 2) - (w_day_num / 2)

    # The settings for the month string in the middle
    w_month_str,h_month_str = font25.getsize(month_str)
    x_month_str = (cal_width / 2) - (w_month_str / 2)

    draw.rectangle((0,0,240, 384), fill = 0) # Calender area rectangle
    draw.text((11, 190),month_cal , font = font_cal, fill = 'white') # Month calender text
    draw.text((x_day_str,10),day_str, font = font35, fill = 'white') # Day string calender text
    draw.text((x_day_num,35),day_number, font = font110, fill = 'white') # Day number string text
    draw.text((x_month_str,150),month_str, font = font25, fill = 'white') # Month string text
    draw.line((10,323,230,323), fill = 'white') # Weather line
    draw.text((70, 340), update_moment, font = font24, fill = 'white')  
    
    # weather
    w_current_icon,h_current_icon = font_weather_icons.getsize(icons_list[str(current_icon)])
    y_current_icon = 417 - (h_current_icon / 2)
    w_current_weather,h_current_weather = font18.getsize(current_weather)
    x_current_weather = (cal_width / 2) - (w_current_weather / 2)
    w_current_temp,h_current_temp = font18.getsize(current_temp)
    x_current_temp = (cal_width / 2) - (w_current_temp / 2)

    w_forecast_icon,h_forecast_icon = font_weather_icons.getsize(icons_list[str(forecast_icon)])
    y_forecast_icon = 417 - (h_forecast_icon / 2)
    w_forecast_weather,h_forecast_weather = font18.getsize(forecast_weather)
    x_forecast_weather = (cal_width / 2) - (w_forecast_weather / 2)

    draw.text((90,390),icons_list[str(current_icon)], font = font_weather_icons, fill = 0) # Diplay weather icon
    draw.text((x_current_weather-7,435), current_weather, font = font18, fill = 0) # Display the current weather text
    draw.text((x_current_temp-8,458), current_temp, font = font18, fill = 0) # Display the current weather text

    draw.text((175,390),icons_list[str(forecast_icon)], font = font_weather_icons, fill = 0) # Diplay weather icon
    draw.text((x_forecast_weather+78,435), forecast_weather, font = font18, fill = 0) # Display the current weather text
    draw.text((165,458), forecast_temp_min_max, font = font18, fill = 0) # Display the current weather text

    draw.rectangle((145,414,155,420), fill = 'red') # Rectangle of the arrow
    draw.polygon([155, 425, 155, 409, 163, 417], fill = 'red') # Triangle of the arrow

    #ImageShow.show(Black_Img)
    #ImageShow.show(Red_Img)
    Img.save('frame.bmp')

if __name__ == '__main__':
    generate_dates()