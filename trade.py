import cv2
import numpy as np
import pyautogui

def find_colors(image):
    # Определяем нижний и верхний пороги для зеленого цвета в формате HSV
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    # Определяем нижний и верхний пороги для красного цвета в формате HSV
    lower_red1 = np.array([0, 40, 40])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 40, 40])
    upper_red2 = np.array([180, 255, 255])

    # Определяем дополнительные цвета, привязанные к зеленой свече
    additional_colors = [
        np.array([191, 109, 209]),  # Цвет 1
        np.array([193, 109, 169]),  # Цвет 2
        np.array([195, 109, 129]),  # Цвет 3
        np.array([191, 129, 92]),   # Цвет 4
        np.array([197, 134, 56])    # Цвет 5
    ]
    
    # Преобразуем изображение в формат HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Применяем маску для нахождения зеленого цвета
    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
    
    # Применяем маску для нахождения красного цвета
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # Применяем маску для нахождения дополнительных цветов
    additional_color_mask = np.zeros_like(green_mask)
    for color in additional_colors:
        additional_color_mask += cv2.inRange(image, color - 10, color + 10)
    
    # Объединяем результаты поиска зеленого, красного и дополнительных цветов
    combined_mask = cv2.bitwise_or(green_mask, red_mask)
    combined_mask = cv2.bitwise_or(combined_mask, additional_color_mask)
    
    # Находим контуры объектов на изображении
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Рисуем контуры объектов на изображении
    cv2.drawContours(image, contours, -1, (150, 75, 0), 2)  # Изменено на коричневый цвет
    
    return image

def determine_trade_signal(candles, has_additional_color):
    # Проверяем условия для долгосрочного входа (long entry)
    if has_additional_color:
        return "long"
    # Проверяем условия для краткосрочного входа (short entry)
    elif candles[-1]['close'] < candles[-2]['close'] or \
            (candles[-1]['open'] > candles[-2]['open'] and candles[-1]['close'] < candles[-2]['close']):
        return "short"
    # Если нет сигнала для входа в сделку
    else:
        return None

def main():
    # Список для хранения информации о свечах (здесь предполагается, что он будет заполняться вашей программой)
    candles = [
        {'open': 100, 'close': 110},
        {'open': 110, 'close': 105},
        # Здесь может быть больше данных о свечах
    ]
    
    while True:
        # Получаем изображение экрана
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        
        # Преобразуем изображение в формат OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Ищем зеленый, красный и дополнительные цвета на изображении экрана
        frame_with_colors = find_colors(frame)
        
        # Оцениваем, есть ли дополнительный цвет на изображении
        has_additional_color = np.any(np.all(frame == [102, 124, 131], axis=-1))
        
        # Анализируем свечи и определяем момент входа в сделку
        trade_signal = determine_trade_signal(candles, has_additional_color)
        
        # Выводим сообщение о входе в сделку, если сигнал обнаружен
        if trade_signal == "long":
            print("Сигнал на вход в сделку на LONG")
        elif trade_signal == "short":
            print("Сигнал на вход в сделку на SHORT")
        
        # Отображаем изображение с зелеными и красными объектами
        cv2.imshow("Objects", frame_with_colors)
        
        # Ждем нажатия клавиши "q" для выхода из цикла
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
