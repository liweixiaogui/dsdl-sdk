# Generated by the dsdl parser. DO NOT EDIT!

from dsdl.types import *
from enum import Enum, unique


@unique
class COCOClassFullDom(Enum):
    person = 1
    bicycle = 2
    car = 3
    motorcycle = 4
    airplane = 5
    bus = 6
    train = 7
    truck = 8
    boat = 9
    traffic_light = 10
    fire_hydrant = 11
    street_sign = 12
    stop_sign = 13
    parking_meter = 14
    bench = 15
    bird = 16
    cat = 17
    dog = 18
    horse = 19
    sheep = 20
    cow = 21
    elephant = 22
    bear = 23
    zebra = 24
    giraffe = 25
    hat = 26
    backpack = 27
    umbrella = 28
    shoe = 29
    eye_glasses = 30
    handbag = 31
    tie = 32
    suitcase = 33
    frisbee = 34
    skis = 35
    snowboard = 36
    sports_ball = 37
    kite = 38
    baseball_bat = 39
    baseball_glove = 40
    skateboard = 41
    surfboard = 42
    tennis_racket = 43
    bottle = 44
    plate = 45
    wine_glass = 46
    cup = 47
    fork = 48
    knife = 49
    spoon = 50
    bowl = 51
    banana = 52
    apple = 53
    sandwich = 54
    orange = 55
    broccoli = 56
    carrot = 57
    hot_dog = 58
    pizza = 59
    donut = 60
    cake = 61
    chair = 62
    couch = 63
    potted_plant = 64
    bed = 65
    mirror = 66
    dining_table = 67
    window = 68
    desk = 69
    toilet = 70
    door = 71
    tv = 72
    laptop = 73
    mouse = 74
    remote = 75
    keyboard = 76
    cell_phone = 77
    microwave = 78
    oven = 79
    toaster = 80
    sink = 81
    refrigerator = 82
    blender = 83
    book = 84
    clock = 85
    vase = 86
    scissors = 87
    teddy_bear = 88
    hair_drier = 89
    toothbrush = 90
    hair_brush = 91


class LocalObjectEntry(Struct):
    bbox = BBoxField()
    label = LabelField(dom=COCOClassFullDom)
    is_crowd = BoolField()


class ObjectDetectionSample(Struct):
    image = ImageField()
    objects = ListField(ele_type=LocalObjectEntry())


@unique
class COCOClassDom(Enum):
    person = 1
    bicycle = 2
    car = 3
    motorcycle = 4
    airplane = 5
    bus = 6
    train = 7
    truck = 8
    boat = 9
    traffic_light = 10
    fire_hydrant = 11
    stop_sign = 12
    parking_meter = 13
    bench = 14
    bird = 15
    cat = 16
    dog = 17
    horse = 18
    sheep = 19
    cow = 20
    elephant = 21
    bear = 22
    zebra = 23
    giraffe = 24
    backpack = 25
    umbrella = 26
    handbag = 27
    tie = 28
    suitcase = 29
    frisbee = 30
    skis = 31
    snowboard = 32
    sports_ball = 33
    kite = 34
    baseball_bat = 35
    baseball_glove = 36
    skateboard = 37
    surfboard = 38
    tennis_racket = 39
    bottle = 40
    wine_glass = 41
    cup = 42
    fork = 43
    knife = 44
    spoon = 45
    bowl = 46
    banana = 47
    apple = 48
    sandwich = 49
    orange = 50
    broccoli = 51
    carrot = 52
    hot_dog = 53
    pizza = 54
    donut = 55
    cake = 56
    chair = 57
    couch = 58
    potted_plant = 59
    bed = 60
    dining_table = 61
    toilet = 62
    tv = 63
    laptop = 64
    mouse = 65
    remote = 66
    keyboard = 67
    cell_phone = 68
    microwave = 69
    oven = 70
    toaster = 71
    sink = 72
    refrigerator = 73
    book = 74
    clock = 75
    vase = 76
    scissors = 77
    teddy_bear = 78
    hair_drier = 79
    toothbrush = 80
