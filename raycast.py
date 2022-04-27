import numpy as np
import main
import rendering
import dramcontroller


def bereken_r_straal(r_speler, r_cameravlak, kolom):
    r_straal_kolom = (float(main.D_CAMERA) * r_speler) + (
                ((-1) + ((2 * float(kolom)) / float(main.BREEDTE))) * r_cameravlak)
    r_straal = r_straal_kolom / np.linalg.norm(r_straal_kolom)
    return r_straal


def raycast(p_speler, r_straal, renderer, window, kolom, textures, r_speler, timeCycle, z_buffer, door_map, world_map,
            delta, wall_map):
    d_muur = -1
    intersectie = np.array([0, 0])
    horizontaal = True
    deur = False
    texture = ""

    # stap 0 initialiseer x en y met waarde 0
    x = 0.0
    y = 0.0

    # stap 1 bereken delta v en h

    delta_v = 1.0 / abs(r_straal[0])
    delta_h = 1.0 / abs(r_straal[1])

    # stap 2 bereken d_horizontaal en d_verticaal
    if r_straal[1] >= 0:
        d_horizontaal = float(1 - p_speler[1] + int(p_speler[1])) * delta_h
    else:
        d_horizontaal = float(p_speler[1] - int(p_speler[1])) * delta_h

    if r_straal[0] >= 0:
        d_verticaal = float(1 - p_speler[0] + int(p_speler[0])) * delta_v
    else:
        d_verticaal = float(p_speler[0] - int(p_speler[0])) * delta_v

    # loop van stap 3 tot stap 6
    while d_muur == -1:
        if (d_horizontaal + x * delta_h) <= (d_verticaal + y * delta_v):
            intersectie = (p_speler + (d_horizontaal + (x * delta_h)) * r_straal)
            horizontaal = True
            x += 1.0

        else:
            intersectie = (p_speler + (d_verticaal + (y * delta_v)) * r_straal)
            horizontaal = False
            y += 1.0

        if horizontaal:
            i_x = int(intersectie[0])
            if r_straal[1] < 0:
                i_y = int(round(intersectie[1]))
                i_y -= 1
            else:
                i_y = int(round(intersectie[1]))

        else:
            i_y = int(intersectie[1])
            if r_straal[0] >= 0:
                i_x = int(round(intersectie[0]))
            else:
                i_x = int(round(intersectie[0])) - 1

        if world_map[i_y, i_x] != 0 and world_map[i_y, i_x] != 10:
            if world_map[i_y, i_x] == 1:
                d_muur = np.linalg.norm(
                    intersectie - p_speler)  # np.sqrt(np.power(intersectie[0] - p_speler[0], 2) + np.power(intersectie[1] - p_speler[1], 2))
                texture = wall_map[i_y, i_x].image

            elif (world_map[i_y, i_x] == 2 or world_map[i_y, i_x] == 3) and not (deur):
                deur = True
                z_buffer_nieuw = door_map[i_y, i_x].render(renderer, window, kolom,
                                                           np.linalg.norm(intersectie - p_speler), intersectie,
                                                           horizontaal, textures, r_straal, r_speler, timeCycle,
                                                           z_buffer, p_speler, delta)
                if z_buffer[main.BREEDTE - 1 - kolom] == 0 or z_buffer_nieuw[main.BREEDTE - 1 - kolom] < z_buffer[
                    main.BREEDTE - 1 - kolom]:
                    z_buffer = z_buffer_nieuw

    return (d_muur, intersectie, horizontaal, z_buffer, door_map, texture)

















