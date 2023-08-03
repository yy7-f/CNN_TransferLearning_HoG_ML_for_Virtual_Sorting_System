# from matplotlib import pyplot as plt
import cv2
import numpy as np
import time
from opcua import Client, ua
from collections import deque
from keras.models import load_model
from tensorflow.keras.preprocessing import image

"""
This is a master class to implement Vision applications.
"""


class VisionSystem():

    def __init__(self, opca_url: str = "opc.tcp://localhost:4840"):
        self._opca_url = opca_url
        self._trigger_varname = "trigger_vision"
        self._result_varname = "vision_result"
        self._result_queue = deque()

    def run(self):
        self._connected = self.connect()
        while self._connected:
            if self._result_queue:
                self._result_var.set_value(ua.Variant(self._result_queue.popleft(), ua.VariantType.Int16))
            time.sleep(0.1)

    def connect(self) -> bool:
        # Create OPCUA Client
        self._client = Client(self._opca_url)
        try:
            # Connect to server
            self._client.connect()
            print("OPCUA Client connected.")
            # Create subscription handler and subscription with 100ms period
            subscription = self._client.create_subscription(100, self)
            # Get GVL node. Use the path from the root node
            GVL = self._client.get_root_node().get_child([
                "0:Objects",
                "0:Server",
                "4:CODESYS Control Win V3 x64",
                "3:Resources",
                "4:Application",
                "3:GlobalVars",
                "4:GVL",
            ])
            # Subscribe to trigger variable
            self._trigger_var = GVL.get_child([f"4:{self._trigger_varname}"])
            subscription.subscribe_data_change(self._trigger_var)
            # Reset result variable value
            self._result_var = GVL.get_child([f"4:{self._result_varname}"])
            self._result_var.set_value(ua.Variant(0, ua.VariantType.Int16))
            print("OPCUA Client ready.")
            return True

        except Exception as e:
            print(f"Exception setting up OPCUA communication: {e}")
            return False

    def datachange_notification(self, node, val, data):
        if self._trigger_varname == node.nodeid.Identifier.split('.')[-1]:
            if val is True:
                self.vision_program()
            else:
                self.send_vision_result(0)

    def send_vision_result(self, result: int = 0):
        self._result_queue.append(result)

    def vision_program(self):
        # This method is executed when the trigger variable changes from False to True
        pass


class MyVisionProg(VisionSystem):

    def vision_program(self):
        img = cv2.imread('C:\\Users\\YFUJIMOT\\Simumatik\\Cameras\\Saved_View_6.png')
        cv2.imshow('image', img)
        height, width, _ = np.shape(img)
        # print(height, width)
        file_path = 'C:\\Users\\YFUJIMOT\\Documents\\vim\\virtual_object\\savedImage.jpg'
        if os.path.exists(file_path):
            os.remove(file_path)
            print('remove file')
        else:
            print("The system cannot find the file specified")
        cv2.imwrite('C:\\Users\\YFUJIMOT\\Documents\\vim\\virtual_object\\savedImage.jpg', img)
        print('Successfully saved')

        # dim = (100, 100)
        # # resize image
        # resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)  
        # height, width, _ = np.shape(resized)
        # print(height, width)
        # data = np.reshape(img, (height * width, 3))
        # data = np.float32(data)
        # print(data)

        # loaded_model = load_model('\\Users\\YFUJIMOT\\Documents\\vim\\model\\vir_object_200_400_classification_ep60_lre3.h5')
        loaded_model = load_model('\\Users\\YFUJIMOT\\Documents\\vim\\model\\vir_object_classification_ep30_lre4++3_lre3_2.h5')
        #print(loaded_model.summary())

        # predict a new image
        img_path = 'C:\\Users\\YFUJIMOT\\Simumatik\\Cameras\\Saved_View_6.png'
        # test_image = image.load_img(img_path, target_size=(200, 400))
        test_image = image.load_img(img_path, target_size=(100, 100))
        # img = image.load_im2g(img_path, color_mode='rgb', target_size=(224, 224))
        
        # display(img)

        # # test (save image)
        # os.chdir(directory)
        # filename = 'savedImage.jpg'
        # cv2.imwrite('C:\\Users\\YFUJIMOT\\Documents\\vim\\virtual_object\\savedImage.jpg', test_image)
        # print("After saving image:")  
        # print(os.listdir(directory))
        # print('Successfully saved')

        test_image = np.expand_dims(test_image, axis=0)
        result = loaded_model.predict(test_image)
        if result[0][0] == 1:
            self.send_vision_result(4)
            print("apple")
        elif result[0][1] == 1:
            self.send_vision_result(2)
            print("bolt")
        elif result[0][2] == 1:
            self.send_vision_result(1)
            print("cup")
        elif result[0][3] == 1:
            self.send_vision_result(5)
            print("scissor")
        elif result[0][4] == 1:
            self.send_vision_result(3)
            print("screwdriver")
        else:
            self.send_vision_result(6)
            print("Unrecognized product!")
        # cv2.waitKey(3000)
        # cv2.destroyAllWindows()

        '''number_clusters = 2
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, _, centers = cv2.kmeans(data, number_clusters, None, criteria, 10, flags)
        bars = []
        dominant_color = None
        for center in centers:
            bar = np.zeros((200, 200, 3), np.uint8)
            bar[:] = center
            bars.append(bar)
            if np.all(center < 80):
                pass  # Conveyor color
            else:
                dominant_color = center
        img_bar = np.hstack(bars)
        cv2.imshow('dominant colors', img_bar)
        if dominant_color is None:
            self.send_vision_result(-1)
            print("No valid dominant color!")
        elif np.all(abs((dominant_color - np.array([52, 108, 168]))) <= [30, 30, 10]):
            self.send_vision_result(1)
            print("Brown product")
        elif np.all(abs((dominant_color - np.array([5, 5, 165]))) <= [15, 15, 15]):
            self.send_vision_result(0)
            print("Red product")
        elif np.all(abs((dominant_color - np.array([90, 30, 25]))) <= [20, 25, 15]):
            self.send_vision_result(4)
            print("Blue product")
        elif np.all(abs((dominant_color - np.array([5, 105, 50]))) <= [20, 20, 15]):
            self.send_vision_result(3)
            print("Green product")
        else:
            self.send_vision_result(-1)
            print("Unrecognized product!")
        print(dominant_color)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()'''


if __name__ == "__main__":
    vision = MyVisionProg(opca_url="opc.tcp://localhost:4840")
    vision._trigger_varname = "trigger_vision"
    vision._result_varname = "vision_result"
    vision.run()
