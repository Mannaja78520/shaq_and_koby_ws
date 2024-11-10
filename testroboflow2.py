from roboflow import Roboflow
import cv2
import numpy as np


rf = Roboflow(api_key="WMxsFN2GNAOdocfzrVJ2")
project = rf.workspace().project("basketball-detector-quxtm")
model = project.version(1).model 

#ดาวน์โหลดภาพ
img_path = "bas1.jpg"
img = cv2.imread(img_path)
result = model.predict(img_path, confidence=40, overlap=30).json()
print(result)

for prediction in result['predictions']:
    x1, y1, x2, y2 = prediction['x'] - prediction['width'] / 2, prediction['y'] - prediction['height'] / 2, prediction['x'] + prediction['width'] / 2, prediction['y'] + prediction['height'] / 2
    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

 # เพิ่มข้อความแสดงชื่อคลาสและค่า confidence
    label = f"{prediction['class']} ({prediction['confidence']*100:.1f}%)"
    # แปลงตำแหน่งข้อความให้เป็นจำนวนเต็ม
cv2.putText(img, label, (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


cv2.imshow("Detection Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
