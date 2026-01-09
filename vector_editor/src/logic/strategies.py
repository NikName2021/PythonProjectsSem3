import json
from abc import ABC, abstractmethod

from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage, QPainter, QColor


class SaveStrategy(ABC):
    @abstractmethod
    def save(self, filename: str, scene):
        pass


class JsonSaveStrategy(SaveStrategy):
    def save(self, filename, scene):
        data = {
            "version": "1.0",
            "scene": {
                "width": scene.sceneRect().width(),
                "height": scene.sceneRect().height()
            },
            "shapes": []
        }

        items = scene.items()[::-1]

        for item in items:
            if hasattr(item, "to_dict"):
                data["shapes"].append(item.to_dict())

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            raise IOError(f"Не удалось записать файл: {e}")


class ImageSaveStrategy(SaveStrategy):
    def __init__(self, format_name="PNG", background_color="white"):
        self.format_name = format_name
        self.bg_color = background_color

    def save(self, filename, scene):
        rect = scene.sceneRect()
        width = int(rect.width())
        height = int(rect.height())

        image = QImage(width, height, QImage.Format_ARGB32)

        if self.bg_color == "transparent":
            image.fill(QColor(0, 0, 0, 0))
        else:
            image.fill(QColor(self.bg_color))

        painter = QPainter(image)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scene.render(painter, QRectF(image.rect()), rect)

        painter.end()

        if not image.save(filename, self.format_name):
            raise IOError(f"Не удалось сохранить изображение: {filename}")
