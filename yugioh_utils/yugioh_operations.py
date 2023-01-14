def getricon(race,ricon):

    continuous, field, equip, counter, ritual, quick_play = '<:continuous:1060059486091489300>','<:field:1060061606727385128>', '<:equip:1060060942609690747>'\
                                                                            ,'<:counter:1060060902570856559>', '<:ritual:1060061076957450341>','<:quick_play:1060061028022485052>'

    aqua, beast, beast_warrior, cyberse, dinosaur, divine_beast, dragon, fairy, fiend,\
    fish, insect, machine, plant, psychic, pyro, reptile, rock, sea_serpent,\
    spellcaster, thunder, warrior, winged_beast, wyrm, zombie = \
    "<:aqua:1060056550191939616>","<:beast:1060056513189781514>",\
    "<:beast_warrior:1060056473096433685>","<:cyberse:1063961658755649638>",\
    "<:dinosaur:1060056438476636251>", "<:divine_beast:1060056388920934510>",\
    "<:dragon:1060056349167329300>", "<:fairy:1060056312827879474>",\
    "<:fiend:1060056266061398097>", "<:fish:1060056223791206451>",\
    "<:insect:1060056164118827149>", "<:machine:1060056124499427358>",\
    "<:plant:1060056072917876856>", "<:psychic:1060056019637653594>",\
    "<:pyro:1060055977510055936>", "<:reptile:1060055927178403901>",\
    "<:rock:1060055879971524658>", "<:sea_serpent:1060055774744817725>",\
    "<:spellcaster:1060055685276123266>", "<:thunder:1060055623640817724>",\
    "<:warrior:1060055520381247588>", "<:winged_beast:1060055427540324372>",\
    "<:wyrm:1060055319927078954>", "<:zombie:1060055023058419722>"

    if race == "Aqua":
        ricon.append(aqua)
    elif race == "Beast":
        ricon.append(beast)
    elif race == "Beast-Warrior":
        ricon.append(beast_warrior)
    elif race == "Cyberse":
        ricon.append(cyberse)
    elif race == "Dinosaur":
        ricon.append(dinosaur)
    elif race == "Divine-Beast":
        ricon.append(divine_beast)
    elif race == "Dragon":
        ricon.append(dragon)
    elif race == "Fairy":
        ricon.append(fairy)
    elif race == "Fiend":
        ricon.append(fiend)
    elif race == "Fish":
        ricon.append(fish)
    elif race == "Insect":
        ricon.append(insect)
    elif race == "Machine":
        ricon.append(machine)
    elif race == "Plant":
        ricon.append(plant)
    elif race == "Psychic":
        ricon.append(psychic)
    elif race == "Pyro":
        ricon.append(pyro)
    elif race == "Reptile":
        ricon.append(reptile)
    elif race == "Rock":
        ricon.append(rock)
    elif race == "Sea Serpent":
        ricon.append(sea_serpent)
    elif race == "Spellcaster":
        ricon.append(spellcaster)
    elif race == "Thunder":
        ricon.append(thunder)
    elif race == "Warrior":
        ricon.append(warrior)
    elif race == "Winged Beast":
        ricon.append(winged_beast)
    elif race == "Wyrm":
        ricon.append(wyrm)
    elif race == "Zombie":
        ricon.append(zombie)
    elif race == "Continuous":
        ricon.append(continuous)
    elif race == "Field":
        ricon.append(field)
    elif race == "Equip":
        ricon.append(equip)
    elif race == "Counter":
        ricon.append(counter)
    elif race == "Ritual":
        ricon.append(ritual)
    elif race == "Quick-Play":
        ricon.append(quick_play)
    elif race == "Normal":
        ricon.append("")

    return ricon

def getattricon(att,attricon):
    dark, divine, earth, fire, light, water, wind, spell, trap = \
        "<:dark:1060047681545830530>", "<:divine:1060048064750047323>",\
        "<:earth:1060048304316104744>", "<:fire:1060048511099482112>",\
        "<:light:1060045885070913556>", "<:water:1060049005108797512>",\
        "<:wind:1060049169894625310>", "<:spell:1060048999765250068>",\
        "<:trap:1060049002466381834>"

    if att == "DARK":
        attricon.append(dark)
    elif att == "DIVINE":
        attricon.append(divine)
    elif att == "FIRE":
        attricon.append(fire)
    elif att == "LIGHT":
        attricon.append(light)
    elif att == "EARTH":
        attricon.append(earth)
    elif att == "WIND":
        attricon.append(wind)
    elif att == "WATER":
        attricon.append(water)

    return attricon