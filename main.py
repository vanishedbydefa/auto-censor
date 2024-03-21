import threading
import itertools
import argparse
import signal
import queue
import time
import sys
import os

from censor import draw_rectangle, blur_region, mosaic_region, draw_rectangle_with_text
from helper import find_nudity, get_files


STOP_THREADS = False
threads = []
all_images = 0
detected_images = 0
censored_images = 0

threads_remove_semaphore = threading.Semaphore(1)
data_update_mux = threading.Semaphore(1)
threads_semaphore = None

def calculate_progress():
    if detected_images == all_images == 0 or get_stop_threads(): return 0
    return round((detected_images / all_images)*100,4)

def set_stop_threads(value=True):
    global STOP_THREADS
    STOP_THREADS = value

def get_stop_threads():
    return STOP_THREADS

def reset_img_counter():
    global all_images, detected_images, censored_images
    all_images = 0
    detected_images = 0
    censored_images = 0

def prepare_parameters(selected_gender, selected_exposure, selected_bodyparts, selected_face):
    # Define the parameters
    GENDER_OPTIONS = ["MALE", "FEMALE"]
    EXPOSURE_OPTIONS = ["EXPOSED", "COVERED"]
    BODYPARTS_OPTIONS = ["BREAST", "BELLY", "FEET", "GENITALIA", "BUTTOCKS", "FEET"]

    # Generate all combinations of parameters
    combinations = itertools.product(selected_gender or GENDER_OPTIONS, 
                                    selected_exposure or EXPOSURE_OPTIONS, 
                                    selected_bodyparts or BODYPARTS_OPTIONS)

    # Craft strings for each combination
    result_strings = []
    for combination in combinations:
        gender, exposure, bodypart = combination
        if bodypart in ["BREAST", "GENITALIA"]:
            result_strings.append('_'.join([gender, bodypart, exposure]))
        else:
            result_strings.append('_'.join([bodypart, exposure]))

    if len(selected_gender) == len(selected_exposure) == len(selected_bodyparts) == 0 and selected_face:
        result_strings = []
    if selected_face:
        if len(selected_gender) > 0:
            for g in selected_gender: result_strings.append("FACE_" + g)
        else:
            for g in GENDER_OPTIONS: result_strings.append("FACE_" + g)
    print(result_strings)
    return result_strings

# Function to gracefully stop the program on CTRL + C
def stop_program(signum, img_queue):
    global threads, threads_semaphore, threads_remove_semaphore, censored_images, detected_images
    set_stop_threads(value=True)
    if signum != None:
        print("Ctrl + C detected. Emptying queue")
    else:
        print("Internal Call for program termination")

    print("Clearing queue: ", end="")
    img_queue.mutex
    while not img_queue.empty():
        img_queue.get()
        img_queue.task_done()
    print("Done")

    print("Clearing threads: ", end="")
    time.sleep(2)
    threads_remove_semaphore.acquire()
    for thread in threads:
            thread.join()
            threads.remove(thread)
            threads_semaphore.release()
    threads_remove_semaphore.release()
    print("Done")

def censor_manager(img_queue:queue, to_censors:list, method:str):
    global data_update_mux, detected_images, censored_images

    img = img_queue.get(timeout=1)
    img_path = img[0]

    try:
        nuditys = find_nudity(img_path)
    except AttributeError:
        nuditys = []
        print(f"Image: {img_path} couldn't be censored")

    censored = False
    for to_censor in to_censors:
        for nudity in nuditys:
            if to_censor == nudity["class"]:
                censored = True
                box = nudity["box"]
                if method == "rectangle":
                    draw_rectangle_with_text(img_path, box[0], box[1], box[2], box[3])
                elif method == "blur":
                    blur_region(img_path, box[0], box[1], box[2], box[3])
                elif method == "mosaic":
                    mosaic_region(img_path, box[0], box[1], box[2], box[3])
                elif method == "rectangle_text_blacked":
                    draw_rectangle_with_text(img_path, box[0], box[1], box[2], box[3])
                else:
                    print("Image wasn't censored because the censor method: {method} isn't specified.")

    if censored:
        data_update_mux.acquire()
        detected_images += 1
        censored_images += 1
        data_update_mux.release()
    else:
        data_update_mux.acquire()
        detected_images += 1
        data_update_mux.release()
    img_queue.task_done()
    threads_semaphore.release()


def main(to_censors:list, method:str, path=".", recursive=False, thread_amount=4):
    global all_images, threads_semaphore, threads, threads_remove_semaphore
    # Create queue and fill it with images
    print("Creating queue...", end="")
    img_queue = queue.Queue()
    images = get_files(path, recursive)
    for img in images:
        img_queue.put(img)
    all_images = img_queue.qsize()
    print(" [Done]")

    # Thread logic
    threads_semaphore = threading.Semaphore(thread_amount)

    while int(img_queue.qsize()) != 0:
        print(f"Remaining Images: {str(img_queue.qsize())} get censored by {str(str(len(threads)))}/{thread_amount} Threads      ", flush=True)
        threads_semaphore.acquire()
        thread = threading.Thread(target=censor_manager, args=(img_queue, to_censors, method))
        thread.start()
        threads.append(thread)

        for thread in threads:
            if not thread.is_alive():
                thread.join()
                threads_remove_semaphore.acquire()
                threads.remove(thread)
                threads_remove_semaphore.release()

        if get_stop_threads():
            stop_program(None, img_queue)

    stop_program(None, img_queue)
    print("Program done")
    return all_images, detected_images, censored_images 