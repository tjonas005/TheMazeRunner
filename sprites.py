import numpy as np
import main

class Sprite:
    p_sprite = np.array([0, 0])
    hoogte = 0
    breedte = 0
    afbeelding = ""
    r_sprite = np.array([0, 0])
    a = 0
    MOVEMENTSPEED = 0
    drawn = False
    followTime = 0
    volgt = False
    hp = 0
    hungerValue = 5
    eetbaar = False
    DPS = 0
    middensteKolom = 0

    def __init__(self, x, y, richting_x,richting_y, png, h, b, speed, volgIk, eet, waarde, health, damage, resources, factory):
        self.p_sprite = np.array([[x], [y]])
        self.afbeelding = factory.from_image(resources.get_path(png))
        self.hoogte = h
        self.breedte = b
        self.r_sprite = np.array([richting_x, richting_y])
        self.MOVEMENTSPEED = speed
        self.volgt = volgIk
        self.eetbaar = eet
        self.hungerValue = waarde
        self.hp = health
        self.DPS = damage

    def move(self, delta_x, delta_y):
        self.p_sprite += np.array([delta_x, delta_y])

    def moveToPlayer(self, p_speler, delta):
        if self.volgt:
            if self.followTime > 0:
                afstand = np.array([self.p_sprite[0]-p_speler[0], self.p_sprite[1]-p_speler[1]])
                norm = np.linalg.norm(afstand)
                afstand /= norm
                self.r_sprite = np.array([afstand[1], -1 * afstand[0]])
                p_sprite_nieuw = np.array([self.p_sprite[0] - delta * afstand[0], self.p_sprite[1] - delta * afstand[1]])

                #check of nieuwe positie geldig is
                if main.world_map[int(p_sprite_nieuw[1]), int(p_sprite_nieuw[0])] == 0:
                    self.p_sprite = p_sprite_nieuw

                elif main.world_map[int(self.p_sprite[1]), int(p_sprite_nieuw[0])] == 0:
                    self.p_sprite[0] = p_sprite_nieuw[0]

                elif main.world_map[int(p_sprite_nieuw[1]), int(self.p_sprite[0])] == 0:
                    self.p_sprite[1] = p_sprite_nieuw[1]

                self.followTime -= delta
            else:
                self.followTime = 0

    def setGrootte(self, h, b):
        self.hoogte = h
        self.breedte = b

    def render(self, renderer, r_speler, r_cameravlak, p_speler, z_buffer):
        breed = self.afbeelding.size[0]
        determinant = ((r_cameravlak[0] * r_speler[1]) - (r_speler[0] * r_cameravlak[1]))
        adj = np.array([[r_speler[1],-r_speler[0]],[-r_cameravlak[1],r_cameravlak[0]]])
        self.drawn = False

        for kolom in range(0, breed):
            p_kolom = np.array([self.p_sprite[0], self.p_sprite[1]])
            #bepaal de coordinaten van de kolom ten opzichte van de speler
            p_kolom[0] -= p_speler[0]
            p_kolom[1] -= p_speler[1]
            #p_kolom[0] += ((-0.5 + kolom / breed) * self.breedte) # * self.r_sprite[0]
            #p_kolom[1] += ((-0.5 + kolom / breed) * self.breedte) * self.r_sprite[1]

            #bepaal de coordinaten tov van het camera vlak
            cameraCoordinaten = (1 / determinant) * np.dot(adj, p_kolom)

            cameraCoordinaten[0] += ((-0.5 + kolom / breed) * self.breedte)

            #bepaal het snijpunt met het cameravlak
            snijpunt = (cameraCoordinaten[0] * main.D_CAMERA) / cameraCoordinaten[1]

            #bepaal in welke kolom van het scherm dit snijpunt valt
            if -1 <= snijpunt <= 1 and cameraCoordinaten[1] > 0:
                schermKolom = int(np.round((snijpunt + 1) * main.BREEDTE/2))
                d_sprite = np.linalg.norm(p_kolom)
                h = (main.HOOGTE/d_sprite)
                y1 = main.HOOGTE - int((main.HOOGTE-h)//2) - 100
                h = int(self.hoogte * h)
                schermKolom = main.BREEDTE - 1 - schermKolom
                if d_sprite < z_buffer[schermKolom] or z_buffer[schermKolom] == 0:
                    z_buffer[schermKolom] = d_sprite
                    self.drawn = True
                    self.followTime = 7.5
                    renderer.copy(self.afbeelding,
                                srcrect=(kolom, 0, 1, self.afbeelding.size[1]),
                                dstrect=(schermKolom, y1, 2, h))
            else:
                schermKolom = 0
            if kolom == main.BREEDTE//2:
                self.middensteKolom = schermKolom

        return z_buffer

    def checkInteractie(self, hunger, hp, p_speler, delta, damage):
        destroy = False
        if self.eetbaar:
            p_sprite = np.array([self.p_sprite[0], self.p_sprite[1]])
            p_sprite[0] -= p_speler[0]
            p_sprite[1] -= p_speler[1]
            p_sprite = np.linalg.norm(p_sprite)
            if p_sprite < main.INTERACTIONDISTANCE:
                hunger += self.hungerValue
                if hunger > 100:
                    hunger = 100
                destroy = True
        if self.volgt:
            if hp < 0:
                destroy = True

            p_sprite = np.array([self.p_sprite[0], self.p_sprite[1]])
            p_sprite[0] -= p_speler[0]
            p_sprite[1] -= p_speler[1]
            p_sprite = np.linalg.norm(p_sprite)
            if p_sprite < main.INTERACTIONDISTANCE:
                hp -= self.DPS * delta
                self.hp -= damage * delta

        return(hunger, hp, destroy)












