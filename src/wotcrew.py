#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import math
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.shared import g_itemsCache
from debug_utils import *

old_cm_as_tankmenResponseS = CrewMeta.as_tankmenResponseS

def new_cm_as_tankmenResponseS(self, data):
    for tankmenData in data['tankmen']:
        tankman = g_itemsCache.items.getTankman(tankmenData['tankmanID'])
        tankmanDossier = g_itemsCache.items.getTankmanDossier(tankman.invID)
        avgXp = float(tankmanDossier.getAvgXP())
        nextLevelBattleCount = int(math.ceil(tankman.getNextLevelXpCost()/avgXp)) if avgXp > 0 else 'X'
        nextSkillBattleCount = int(math.ceil(tankman.getNextSkillXpCost()/avgXp)) if avgXp > 0 else 'X'
        rankPrefix = '[{0}|{1}] '.format(nextLevelBattleCount, tankman.getNextLevelXpCost())
        rolePrefix = '[{0}|{1}] '.format(nextSkillBattleCount, tankman.getNextSkillXpCost())
        tankmenData['rank'] = rankPrefix + tankmenData['rank']
        tankmenData['role'] = rolePrefix + tankmenData['role']
    old_cm_as_tankmenResponseS(self, data)

CrewMeta.as_tankmenResponseS = new_cm_as_tankmenResponseS

