import cv2
import matplotlib.pyplot as plt
import numpy as np

def cartoonize(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    edges = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
    quantized = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    quantized = cv2.convertScaleAbs(quantized, alpha=(255.0/254.0))
    quantized = cv2.cvtColor(quantized, cv2.COLOR_RGB2LAB)
    quantized = cv2.medianBlur(quantized, 5)
    Z = quantized.reshape((-1,3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 8
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    res = center[label.flatten()]
    quantized = res.reshape((quantized.shape))
    quantized = cv2.cvtColor(quantized, cv2.COLOR_LAB2RGB)
    cartoon = cv2.bitwise_and(quantized, quantized, mask=edges)
    return cartoon


def run(filename):
    cap = cv2.VideoCapture('templates/' + filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('static/' + filename, fourcc, fps, (width, height))
    print(cap.isOpened())

    frameC = 0

    while cap.isOpened():
        ret, frame = cap.read()
        frameC = frameC + 1
        print(ret, frameC)
        if ret:
            cartoon = cartoonize(frame)
            hsv = cv2.cvtColor(cartoon, cv2.COLOR_RGB2HSV)
            hsv[:, :, 0] = (hsv[:, :, 0] + 20) % 180
            cartoon = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            out.write(cartoon)
            plt.imshow(cartoon)
            # plt.show()
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("completed")