requirementni ustanovka qilganingdan keyin manabuni ham ustanovka qil.

1. Tesseract dasturini o'rnatish
Agar sizning operatsion tizimingiz Ubuntu bo'lsa, quyidagi buyruqlarni terminalda bajarib tesseract-ocr ni o'rnating:

sudo apt update                          <-- asosan bu
sudo apt install tesseract-ocr -y       <-- asosan bu
sudo apt install libtesseract-dev -y    <-- asosan bu

O'rnatilganligini tekshirish uchun:
tesseract --version


pip install pytesseract pillow   <-- asosan bu


from pytesseract import pytesseract
from PIL import Image

# Tesseract yo'lini sozlash
pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Test uchun rasmni yuklash
image = Image.open("test_image.jpg")  # Rasmni "test_image.jpg" bilan almashtiring

# Rasmni matnga aylantirish
text = pytesseract.image_to_string(image)
print("Matn:", text)
