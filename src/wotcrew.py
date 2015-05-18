#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import math
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.shared import g_itemsCache
from debug_utils import *

def numWithPostfix(value):
    if value < 1000:
        return str(int(value))
    elif value < 100000:
        return '{:0.1f}k'.format(value/1000.0)
    elif value < 1000000:
        return '{0:d}k'.format(int(math.ceil(value/1000.0)))
    else:
        return '{:0.1f}M',format(value/1000000.0)

old_cm_as_tankmenResponseS = CrewMeta.as_tankmenResponseS

def new_cm_as_tankmenResponseS(self, data):
    for tankmenData in data['tankmen']:
        tankman = g_itemsCache.items.getTankman(tankmenData['tankmanID'])
        tankmanDossier = g_itemsCache.items.getTankmanDossier(tankman.invID)
        avgXp = float(tankmanDossier.getAvgXP())
        if tankman.isInTank:
            vehicle = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
            if vehicle is not None and vehicle.isPremium:
                avgXp *= 1.5
        nextLevelBattleCount = numWithPostfix(math.ceil(tankman.getNextLevelXpCost()/avgXp)) if avgXp > 0 else 'X'
        nextSkillBattleCount = numWithPostfix(math.ceil(tankman.getNextSkillXpCost()/avgXp)) if avgXp > 0 else 'X'
        rankPrefix = '[{0}|{1}] '.format(nextLevelBattleCount, numWithPostfix(tankman.getNextLevelXpCost()))
        rolePrefix = '[{0}|{1}] '.format(nextSkillBattleCount, numWithPostfix(tankman.getNextSkillXpCost()))
        tankmenData['rank'] = rankPrefix + tankmenData['rank']
        tankmenData['role'] = rolePrefix + tankmenData['role']
    old_cm_as_tankmenResponseS(self, data)

CrewMeta.as_tankmenResponseS = new_cm_as_tankmenResponseS

