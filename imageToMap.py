from PIL import Image
import numpy as np
import doors
import main
import random
import time
import sprites

MUUR = 1
TIMEDDEUR = 2
INTERACTABLEDEUR = 3
LEFT = 0
RIGHT = 1

TIPS = ["Watch out! At night the doors will close and monster will appear!",
        "If your hunger drops to 0 you will die a slow and painful death!",
        "By sprinting you can cover more ground but your hunger bar wil drop faster.",
        "Consumables and other items can be picked up and dropped using F and G.",
        "Certain doors can be opened by answering the question with wisdom and strength.",
        "Items can be crafted by combining specific items at the crafting station and pressing F",
        "Watch out to not get crushed by closing doors, they will not wait for you!",
        "To turn 180 degrees, press c."
        ]

def generateWorld(afbeelding, factory, resources, textures, renderer, fontManager):
    input_image = Image.open(afbeelding)
    r_image_in, g_image_in, b_image_in = input_image.split()
    r_in = np.uint32(np.array(r_image_in))
    b_in = np.uint32(np.array(b_image_in))
    g_in = np.uint32(np.array(g_image_in))

    world_map = np.zeros((r_in.shape[0], r_in.shape[1]), int)
    door_map = np.empty((r_in.shape[0], r_in.shape[1]), object)
    wall_map = np.empty((r_in.shape[0], r_in.shape[1]), object)
    doorLocation = []
    spriteList = []
    timeIndex = random.randint(0, len(TIPS)-1)
    starttime = time.time()
    for i in range(r_in.shape[0]):
        for j in range(r_in.shape[1]):
            #zwarte pixel ==> muur met texture[0]
            if r_in[i, j] == 0 and b_in[i, j] == 0 and g_in[i, j] == 0:
                world_map[i, j] = MUUR
                wall_map[i, j] = Wall(i, j, textures[0], "wall")

                #grijze pixel ==> craftingbench
            elif r_in[i, j] == 128 and b_in[i, j] == 128 and g_in[i, j] == 128:
                world_map[i, j] = MUUR
                wall_map[i, j] = Wall(i, j, textures[2], "crafting bench")

            #blauwwe pixel ==> timed deur die van links opent
            elif b_in[i, j] == 255 and r_in[i, j] == 0 and g_in[i, j] == 0:
                world_map[i, j] = TIMEDDEUR
                door_map[i, j] = doors.timedDoor((j, i), LEFT, textures[0])
                doorLocation.append((i, j))

            #groene pixel ==> timed deur die van rechts opent
            elif b_in[i, j] == 0 and r_in[i, j] == 0 and g_in[i, j] == 255:
                world_map[i, j] = TIMEDDEUR
                door_map[i, j] = doors.timedDoor((j, i), RIGHT, textures[0])
                doorLocation.append((i, j))

            elif b_in[i, j] == 0 and r_in[i, j] == 255 and g_in[i, j] == 0:
                world_map[i, j] = INTERACTABLEDEUR
                door_map[i, j] = doors.interactableDoor((j, i), RIGHT, textures[1])
                door_map[i, j].setPassCode(main.codeList, main.instructionsList)
                doorLocation.append((i, j))

            elif b_in[i, j] == 50 and r_in[i, j] == 117 and g_in[i, j] == 116:
                world_map[i, j] = 0
                spriteList.append(sprites.Sprite(j + 0.5, i + 0.5, 1, 0, "burger.png", 0.5, 0.5, 1, False, False, False, True, 10, 0, 5, resources, factory, None))

            elif b_in[i, j] == 50 and r_in[i, j] == 117 and g_in[i, j] == 50:
                world_map[i, j] = 0
                spriteList.append(sprites.Sprite(j + 0.5, i + 0.5, 1, 0, "medkit.png", 0.5, 0.5, 1, False, False, False, True, 0, 0, 10, resources, factory, None))
            elif r_in[i, j] == 78 and g_in[i, j] == 168 and b_in[i, j] == 153:
                world_map[i, j] = 0
                spriteList.append(sprites.Sprite(j + 0.5, i + 0.5, 1, 0, "stick.png", 0.5, 0.5, 1, False, False, False, True, 10, 0, 0, resources, factory, None))


            #witte pixel ==> openruimte
            else:
                world_map[i, j] = 0

        endtime = time.time()
        if (endtime - starttime) >= 2:
            starttime += 5
            timeIndex = random.randint(0, len(TIPS)-1)
        renderLoadingScreen(fontManager, factory, renderer, i, r_in.shape[0], timeIndex)

    return(world_map, doorLocation, door_map, wall_map, spriteList)


class Wall:
    image = ""
    posWorldCoordinates = np.array([0.0, 0.0])
    type = "wall"

    def __init__(self, x, y, image, type):
        self.posWorldCoordinates = np.array([x, y])
        self.image = image
        self.type = type


def renderLoadingScreen(resources, factory, renderer, waarde, max, textindex):

    completion = int(100*waarde/max)
    renderer.clear()
    renderer.fill((0, 0, main.BREEDTE, main.HOOGTE), main.kleuren[5])
    renderer.fill((main.BREEDTE//2 - 100,  main.HOOGTE//2 - 50, 2*completion, 100), main.kleuren[2])
    text1 = "Loading: " + str(completion) + "%"
    text2 = TIPS[textindex]
    text = factory.from_text(text1, fontmanager = resources)
    renderer.copy(text, dstrect=(main.BREEDTE//2 - 100, main.HOOGTE//2 - 50, 200, 100))
    text = factory.from_text(text2, fontmanager = resources)
    renderer.copy(text, dstrect=(main.BREEDTE // 2 - len(text2)*4, main.HOOGTE - 100, len(text2) * 8, 60))
    renderer.present()
