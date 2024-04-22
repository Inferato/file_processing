from django.views.generic import TemplateView
from django.conf import settings
import cv2
import os
import base64
from ultralytics import YOLO

class ProcessImageView(TemplateView):
    template_name = 'processed_images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Завантаження моделей
        car_detector = YOLO(os.path.join(settings.BASE_DIR, 'yolov8n.pt'))
        plate_detector = YOLO(os.path.join(settings.BASE_DIR, 'license_plate_detector.pt'))

        # Шлях до директорії з зображеннями
        images_dir = os.path.join(settings.MEDIA_ROOT, 'car_samples')

        # Отримання списку імен файлів зображень
        image_files = [os.path.join(images_dir, file) for file in os.listdir(images_dir) if file.endswith('.jpg')]

        processed_images = []

        # Ітерація по зображеннях
        for image_file in image_files:
            # Зчитування зображення
            original_image = cv2.imread(image_file)

            # Виконання детектування об'єктів з використанням детекторів
            car_detection_results = car_detector(image_file)
            plate_detection_results = plate_detector(image_file)

            # Об'єднання результатів детектування
            combined_results = car_detection_results + plate_detection_results

            processed_result = original_image.copy()

            # Ітерація по об'єднаним результатам
            for result in combined_results:
                for box in result.boxes:
                    # Обрізка області інтересу
                    x1, y1, x2, y2 = map(int, box.xyxy.tolist()[0])  # Перетворення тензора в список цілих чисел


                    cv2.rectangle(processed_result, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # Додавання тексту з координатами
                    text = f"{round(box.xyxy.tolist()[0][0], 6)}, {round(box.xyxy.tolist()[0][1], 6)}"
                    cv2.putText(processed_result, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Кодування обробленого зображення у формат base64
            _, buffer = cv2.imencode('.jpg', processed_result)
            encoded_image = base64.b64encode(buffer).decode('utf-8')
            processed_images.append(encoded_image)

        context['processed_images'] = processed_images

        return context
