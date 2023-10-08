# Virtual_Sorting_System_with_CNN_TransferLearning_HoG

Product sorting system in virtual production line is developed in this project. The tasks for building
the sorting production line are virtual modeling, PLC programming, vision algorithm and image
classification, and robot operation.

**Virtual model**
Virtual model is developed using Simumatik. The model is shown in Fig.1. The conveyors are put
on the tables and moved by DC motor. The number of conveyers is six and the length of each
conveyer is 500mm. The DC motor gets electricity from the power supply through DC relay and DC
reversing contractor. Products are conveyed on the conveyers and pushed by pneumatic cylinders to
sort products into five different plastic boxes.

The fourth pneumatic cylinder is replaced with ABB robot. A compressor is equipped to operate the
pneumatic cylinders. Also, solenoid valves are equipped to control the air pressure from the
compressor to the pneumatic cylinders. Products include apples, bolts, cups, scissors, and screwdrivers. Photoelectric sensors are equipped to detect the products that are conveyed on the
conveyers instead of inductive sensors because inductive sensors can only detect metal targets
although the objects in this project include non-metal objects such as apples and cups. Two push
buttons are placed on the corner of the table to start PLC program and drop products.

<img width="413" alt="image" src="https://github.com/yy7-f/Virtual_Sorting_System_with_CNN_TransferLearning_HoG/assets/76237852/21cb07cc-52ae-479f-b617-afa6295d392c">

Fig.1 Virtual model developed using Simumatik

**PLC programming**
PLC programming is built using Codesys. The digital inputs of the PLC contain system start
button, products entry button, input conveyer sensor, sorter 1 sensor, sorter 2 sensor, sorter 3 sensor,
sorter 4 (ABB robot) sensor, and sorter 5 sensor and gripper signal of ABB robot. The digital
outputs of the PLC include motor contactors of input conveyor, sorter 1 conveyer, sorter 2
conveyor, sorter 3 conveyor, sorter 4 conveyor, and sorter 5 conveyor, pneumatic valves of sorter1,
sorter2, sorter 3, and sorter 5, and a vacuum gripper of the robot, and product entry.

The sequential function chart of PLC is illustrated in Fig.2. At first, the PLC is in the initial phase.
Once the system starts button is pushed the phase moves to ‘wait for product’ phase. After that, when
the product entry button is pushed, a product drops on the input conveyor. After waiting 0.5 seconds, the input
conveyor is moved by sending signal to input motor contractor to move DC motor of the input
conveyor. And then, when the sensor on the input conveyor detects a product, the conveyor is stopped
for 2 seconds and a picture is taken to obtain input for the classification model to sort the products. In
the picture-taking phase, the trigger variable ‘trigger_vision’ changes from False to True and after
stopping the conveyor for 2 seconds, and the phase is into ‘wait for answer’ step. In this step, the
PLC waits for the result of the vision algorithm (vision_result). The result returns six different
integers including the case that the products are classified as each product and unrecognized
product.

When the result of vision algorithm is 1, the signal from PLC is sent to the motor contrctor of the
conveyors of input and sorter 1and the product is conveyed. When the sorter 1 sensor detect the
product, the signal from PLC is sent to the solenoid valve of the pneumatic cylinder of sorter1 and the
cylinder push the product and drop it into the sorting box. After pushing the product and waiting
one second, the phase goes back to the entry product phase, and a new product is dropped.

When the result returns 2, 3, 4, 5, 6, similar operation is conducted. For example, when the result is
3, PLC send signal to the contrctor of the conveyors of input and sorter 1and the product is
conveyed. When the sorter 1 sensor detect the product, PLC send signal to the contrctor of the
conveyors of sorter 1 and sorter 2 and the product is conveyed. After that, when the sorter 2 sensor
detect the product, PLC send signal to the contrctor of the conveyors of sorter 2 and sorter 3 and the
product is conveyed. And then, when the sorter 3 sensor detect the product, the digital output from
PLC is sent to solenoid valve of the pneumatic cylinder of sorter 3 and the cylinder push the product
and drop it into the sorting box. After pushing the product and waiting one second, the stage go
back to the product entry phase and new product is dropped.

In order to deal with some issues such that a product gets stuck or falls off the conveyor, I put error
handling program on the PLC. If the specific motor contactor get signal and the specific conveyer
move but the specific sensor does not detect products for more than 20 seconds, the phase go back
to initial phase. Therefore, the production can start over after removing the issues from the
production system. The error handling program is placed before each sensor detection. Furthermore,
I develop another error handling model that go back to production entry phase if the errors happen.
The sequential function chart of Error handling is illustrated in Fig.2.

<img width="657" alt="image" src="https://github.com/yy7-f/Virtual_Sorting_System_with_CNN_TransferLearning_HoG/assets/76237852/7fbcf5d5-a6ab-4236-ac5a-bc9462d776ec">

Fig.2 Sequential function chart of PLC

<img width="236" alt="image" src="https://github.com/yy7-f/Virtual_Sorting_System_with_CNN_TransferLearning_HoG/assets/76237852/0e5eb5b3-7d23-4625-9e80-1c579eaf1542">

Fig. 3 Sequential function chart of Error handling

**Vision algorithm**
Vision algorithms are developed for sorting the products. OpenCV library is used to read pictures
taken by camera on Simumatik from a specific folder on the PC. Additionally, OPCUA library is
used to communicate between the PLC and python script. When the trigger variable ‘trigger_vision’
change to True from False, the ‘vision_program’ method is implemented.

In ‘vision_program’ method, a picture taken by camera on Simumatik is read from a specific folder
and image classification model that developed is loaded.After that, the model classify the photo.

If the model classify it as a cup, vision result = 1 is sent to PLC. If the model classify it as a bolt,
vision result = 2 is sent to PLC. If the model classify it as a screw driver, vision result = 3 is sent to
PLC. If the model classify it as an apple, vision result = 4 is sent to PLC. If the model classify it as
a scissor, vision result = 5 is sent to PLC. If the model cannot classify it, vision result = 6 is sent to
PLC.

Three image classification algorithms are used in this project. First algorithm is convolutional
neural network. The convolutional neural network consists of four convolution layers, four pooling
layers, four dropout layers, a flatten layer, and two dense layers. The kernel size is 3 x 3 and the
number of filters is 16, 32, 64, 128 respectively. The dropout rate is 25% and the activation function
of convolution layer is ReLU function. The dropout layers are utilized for avoiding overfitting. The
filter size of max pooling is 2 x 2. The final dense layer has 5 outputs and the activation function of
the layer is soft max function to classify 5 products. In the case of real object classification, there
are 4 objects except for apple, therefore the the number of outputs of the final dense layer is 4. In
convolution layer, at each tensor's location, an element-wise product between the input and each
kernel element is computed, and it is then summed to acquire the output value at the corresponding
position of the output tensor (Yamashita et.al 2018). The purpose of pooling layers’ operation is
down sampling.

Second classification algorithm is transfer learning using VGG16 for feature extraction and four
dense layers for classification. VGG 16 has 13 convolution layers and five pooling layers. In
addition, there are three Dense layers (Rezende et.al 2018). The input size is 224 x 224. The kernel
size of the convolution layers is 3 x 3 and the filter size of the max pooling layers is 2 x 2. The
number of outputs of the four dense layers is 2048, 1024, 512, and 5 respectively. The activation
function of the final layer is softmax function.

Third one uses HoG (Histogram of Oriented Gradients) algorithm for feature extraction and
machine learning algorithms including random forest and k-nearest neighbors. HoGs (Histograms
of Oriented Gradients) are histograms of the gradient direction of pixel values in a local area. The
orientation parameter is 9, pixels per cell is 8 x 8, cells per block is 2 x 2. In HoG algorithm,
gradient of x-direction and y-direction of each cell are calculated and gradient magnitude and
gradient direction are computed. Based on the result, the histogram of gradients is created. These
calculation executed for each cell and each vector of each cell is obtained.

**Robot**
Sorting Robot is created with ABB RobotStudio and shown in Fig.4. It is equipped to sort products
instead of the fourth pneumatic cylinder. The robot pick products up and drop them into ‘sorting
box 4’ when the vision algorithm return ‘vision result = 4’. The robot head move to the point where
the product is and pick it up and move to the point above the sorting box and drop it and go back to
initial position. The path is shown in Fig.4 as yellow arrows. The vacuum gripper is equipped on
the robot head to pick up products. It is connected to the air compressor through a solenoid valve.
The vacuum length is made longer than default to pick up various different product with the same
robot path.

<img width="218" alt="image" src="https://github.com/yy7-f/Virtual_Sorting_System_with_CNN_TransferLearning_HoG/assets/76237852/1f0c2e69-0ee2-4130-8070-e98c80fad40f">

Fig.4 The ABB robot


