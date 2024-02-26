import cv2
import numpy as np
import pyautogui

work_zone = []

def select_work_zone(event, x, y, flags, param):
    global work_zone
    if event == cv2.EVENT_LBUTTONDOWN:
        work_zone.append((x, y))
        if len(work_zone) == 2:
            cv2.setMouseCallback("Select Work Zone", lambda *args : None)  # Запрещаем обработку событий мыши
            cv2.destroyWindow("Select Work Zone")

def choose_work_zone():
    global work_zone
    screen = pyautogui.screenshot()
    frame = np.array(screen)
    cv2.namedWindow("Select Work Zone")
    cv2.setMouseCallback("Select Work Zone", select_work_zone)
    
    while True:
        frame_copy = frame.copy()
        if len(work_zone) == 1:
            cv2.circle(frame_copy, work_zone[0], 5, (0, 255, 0), -1)
        elif len(work_zone) == 2:
            cv2.rectangle(frame_copy, work_zone[0], work_zone[1], (0, 255, 0), 2)
        cv2.imshow("Select Work Zone", frame_copy)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

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
    # Преобразуем изображение в формат HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Применяем маску для нахождения зеленого цвета
    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
    
    # Применяем маску для нахождения красного цвета
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    
    # Объединяем результаты поиска зеленого, красного и дополнительных цветов
    combined_mask = cv2.bitwise_or(green_mask, red_mask)
    
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
    global work_zone
    choose_work_zone()
    if len(work_zone) != 2:
        print("Не выбраны оба угла. Программа завершается.")
        return
    
    print("Выбранная рабочая зона:", work_zone)
    
    candles = [
        {'open': 100, 'close': 110},
        {'open': 110, 'close': 105},
        # Здесь может быть больше данных о свечах
    ]
    
    while True:
        screen = pyautogui.screenshot(region=(*work_zone[0], work_zone[1][0] - work_zone[0][0], work_zone[1][1] - work_zone[0][1]))  # Регион области
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_with_colors = find_colors(frame)
        has_additional_color = np.any(np.all(frame == [102, 124, 131], axis=-1))
        trade_signal = determine_trade_signal(candles, has_additional_color)
        
        if trade_signal == "long":
            print("Сигнал на вход в сделку на LONG")
        elif trade_signal == "short":
            print("Сигнал на вход в сделку на SHORT")
        
        cv2.imshow("Objects", frame_with_colors)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
