import smtplib
import cv2
import time
import glob
import os
from emailing import send_email
from threading import Thread

video = cv2.VideoCapture(0)

# Stops the execution of the code for 1 second for the camera to start
time.sleep(1)


# This function will be responsible for sending and email and deleting the images. We need to merge these two functionalities, to prevent the video from being paused for a few seconds,
# when the image is being sent via email. We also delete images in the same function, to prevent from deleting the image too quickly, before it has been sent via email.
def manage_emails_and_images(image, images):
    # Deamon Threads zostaną zastopowane kiedy program się zamknie. Normalne thready na to nie pozwolą, program poczeka na ich wykonanie przed zamknięciem.
    try:
        send_email(image)
        for image in images:
            os.remove(image)
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPResponseException):
        print('Credentials error, check sender, password and reciever. Email was not sent')
    except AttributeError:
        print("NoneType' object has no attribute 'encode' -> check env variables if they are correct. Email has not been sent.")


first_frame = None
status_list = []
count = 1

while True:
    status = 0
    check, frame = video.read()

    # 1. We change the pixels of the frame to gray color.
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 2. Then we use blur on it. We do it to make the frames less precise, to be easier and faster to compare with each other.
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau

    # 3. We compare every frame with the original frame. Delta frame means pixels, which aren't in the first frame. So this is a difference between the first frame, and a current frame.
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    # 4. We want to make whiteish pixels more white, more explicit. We want the objects to be more white. This method changes every pixel which is 30 or more into 255.
    # cv2.THRESH_BINARY -> algorithm we use for the conversion
    thresh_frame = cv2.threshold(delta_frame, 90, 255, cv2.THRESH_BINARY)[1]

    # 5. We try to remove the "noise" from the video. The higher iterations, the more proccessing will be applied to this method.
    dil_frame = cv2.dilate(thresh_frame, None, iterations=3)

    # 6. Detect the contours around white areas. Countours is a list of all detected countours. cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE -> algorithms
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # If the contour is less than 5000 pixels, it is a light noise, not an object.
        if cv2.contourArea(contour) < 3000:
            continue
        # If the counter is more than 3000 pixels, we draw a rectangle. 24:50 na filmie 307
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, x + y), (0, 0, 255), 3)
        if rectangle.any():
            status = 1
            # If there is a rectangle around the object, save this frame
            cv2.imwrite(f"images/{count}.png", frame)
            count += 1
    status_list.append(status)

    # 7. If the object has left the camera, send an email to the user and remove all the images
    status_list = status_list[-2:]
    if status_list[0] and not status_list[1]:  # if status_list[0] == 1 and status_list[1] == 0
        # Choose which frame will be sent via email
        all_images = glob.glob('images/*.png')
        image_to_send = all_images[int(len(all_images) / 2)]
        Thread(target=manage_emails_and_images, args=(image_to_send, all_images), daemon=True, name='Email Sending Thread').start()

    # 8. Display the video with rectangles
    cv2.imshow('My Video', frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

video.release()
