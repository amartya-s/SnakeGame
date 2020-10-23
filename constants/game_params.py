import os
import pathlib

class GameParams:
    # Controller params
    SNAKE_INIT_COORD = (600, 200)
    FOOD_INIT_COORD = (500, 100)

    # Snake params
    SPEED_INCREMENT_SEGMENT_COUNT = 10
    SPEED_INCREMENT_FACTOR = 5
    MAX_SNAKE_SPEED = 50

    # Food Params
    FOOD_WITH_TIMERS_ALLOWED_AT_SAME_TIME = 3
    FOOD_SCORE = 1
    FOOD_WITH_TIMER_SCORE = 10

    FOOD_WIDTH = 80
    IMAGE = None
    IMAGE_PATH_FOOD = os.path.join(os.path.split(os.path.dirname(__file__))[0],'images','rat.jpg')

    # AutoDestroyable food params
    RANDOM_FOOD_WITH_TIMER_AFTER_DURATION_MIN_MAX = 10000, 50000
    FOOD_WITH_TIMER_DURATION_MIN_MAX = 5000, 15000

    CLOCK_WIDTH = 20
    UPDATE_FREQ_IN_MILLIS = 200
    IMAGE_PATH_SUPER_FOOD = os.path.join(os.path.split(os.path.dirname(__file__))[0] ,'images','frog.jpg')

    # Bomb params
    RANDOM_BOMB_AFTER_DURATION_MIN_MAX = 30000, 50000
    BOMB_DURATION_MIN_MAX = 20000, 30000

    IMAGE_PATH_BOMB = os.path.join(os.path.split(os.path.dirname(__file__))[0],'images','bomb.jpg')

    # Button config
    SAVE_IMAGE_PATH =  os.path.join(os.path.split(os.path.dirname(__file__))[0],'images','save.png')
    RESUME_IMAGE_PATH = os.path.join(os.path.split(os.path.dirname(__file__))[0],'images','resume.png')
    PAUSE_IMAGE_PATH = os.path.join(os.path.split(os.path.dirname(__file__))[0],'images','pause.png')

    # Datastore config
    DATASTORE_FILE_PATH = pathlib.Path.home()
