import cv2
import numpy as np
import time
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
    work_zone = []
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
        
        if cv2.waitKey(1) & 0xFF == ord('q') or len(work_zone) == 2:
            break
    
    cv2.destroyAllWindows()
    return work_zone  # Убедитесь, что возвращается переменная work_zone

def find_colors(image):
    # Определяем нижний и верхний пороги для зеленого цвета в формате HSV
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    # Определяем нижний и верхний пороги для красного цвета в формате HSV
    lower_red1 = np.array([0, 40, 40])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 40, 40])
    upper_red2 = np.array([180, 255, 255])

    # Преобразуем изображение в формат HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Применяем маску для нахождения зеленого цвета
    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
    
    # Применяем маску для нахождения красного цвета
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    
    # Объединяем результаты поиска зеленого и красного цветов
    combined_mask = cv2.bitwise_or(green_mask, red_mask)
    
    # Находим контуры объектов на изображении
    contours, hierarchy = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Отладочный код: рисуем контуры объектов на изображении
    for contour in contours:
        # Вычисляем ограничивающий прямоугольник для каждого контура
        x, y, w, h = cv2.boundingRect(contour)
        # Рисуем прямоугольник вокруг контура
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return image, contours

def extract_candle_data(frame_with_colors, contours):
    candles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Определяем центры верхней и нижней части свечи
        top_center = (x + w // 2, y)
        bottom_center = (x + w // 2, y + h)

        # Проверяем цвета в этих точках для определения, является ли свеча бычьей или медвежьей
        if np.all(frame_with_colors[top_center[::-1]] == [255, 0, 0]) and np.all(frame_with_colors[bottom_center[::-1]] == [0, 0, 255]):
            color = 'green'  # Зеленый цвет свечи
            open_price = bottom_center[1]
            close_price = top_center[1]
        elif np.all(frame_with_colors[top_center[::-1]] == [0, 0, 255]) and np.all(frame_with_colors[bottom_center[::-1]] == [255, 0, 0]):
            color = 'red'  # Красный цвет свечи
            open_price = top_center[1]
            close_price = bottom_center[1]
        else:
            continue  # Если цвета не соответствуют, пропускаем эту свечу

        candles.append({'open': open_price, 'close': close_price, 'color': color})
    
    return candles



def determine_trade_signal(candles):
    # Проверяем, есть ли достаточно данных для анализа

    print(len(candles))

    if len(candles) < 2:
        return None

    print(len(candles))

    # Получаем последние две свечи
    last_candle = candles[-1]
    prev_candle = candles[-2]

    print(last_candle['color'], prev_candle['color'])

    # Определяем условия для "длинной" позиции (long)
    if last_candle['color'] == 'green' and last_candle['close'] > last_candle['open'] and \
       last_candle['close'] > prev_candle['close'] and last_candle['open'] > prev_candle['open']:
        return "long"

    # Определяем условия для "короткой" позиции (short)
    elif last_candle['color'] == 'red' and last_candle['close'] < last_candle['open'] and \
         last_candle['close'] < prev_candle['close'] and last_candle['open'] < prev_candle['open']:
        return "short"

    # Если нет сигнала для входа в сделку
    else:
        return None


def debug_candle_detection(frame_with_colors, iteration):
    # Сохраняем текущий кадр в файл для дебага
    cv2.imwrite(f'debug_frame_{iteration}.png', frame_with_colors)


def main():
    work_zone = choose_work_zone()
    if not work_zone or len(work_zone) != 2:
        print("Не выбраны оба угла. Программа завершается.")
        return
    
    print("Выбранная рабочая зона:", work_zone)

    while True:
        start_time = time.time()

        # Скриншот выбранной рабочей зоны
        screen = pyautogui.screenshot(region=(
            work_zone[0][0], work_zone[0][1],
            work_zone[1][0] - work_zone[0][0],
            work_zone[1][1] - work_zone[0][1]
        ))
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Обработка изображения для извлечения данных о свечах
        frame_with_colors, contours = find_colors(frame)

        candles = extract_candle_data(frame_with_colors, contours)

        # Определение торгового сигнала на основе анализа свечей
        trade_signal = determine_trade_signal(candles)

        # Вывод торгового сигнала
        if trade_signal == "long":
            print("Сигнал на вход в сделку на LONG")
        elif trade_signal == "short":
            print("Сигнал на вход в сделку на SHORT")

        # Показ обработанного изображения
        cv2.imshow("Objects", frame_with_colors)

        # Выход из цикла по нажатию клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Пауза для следующего анализа через 5 секунд
        time.sleep(max(0, 1 - (time.time() - start_time)))

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()