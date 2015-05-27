#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import math
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.Scaleform.daapi.view.meta.ResearchPanelMeta import ResearchPanelMeta
from gui.shared import g_itemsCache
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.techtree import dumpers, NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from debug_utils import *

def numWithPostfix(value):
    if value < 1000:
        return str(int(value))
    elif value < 100000:
        return '{:0.1f}k'.format(value/1000.0)
    elif value < 1000000:
        return '{0:d}k'.format(int(math.ceil(value/1000.0)))
    else:
        return '{:0.1f}M'.format(value/1000000.0)

old_cm_as_tankmenResponseS = CrewMeta.as_tankmenResponseS

def new_cm_as_tankmenResponseS(self, data):
    for tankmenData in data['tankmen']:
        tankman = g_itemsCache.items.getTankman(tankmenData['tankmanID'])
        tankmanDossier = g_itemsCache.items.getTankmanDossier(tankman.invID)
        avgXp = float(tankmanDossier.getAvgXP())
        if tankman.isInTank:
            vehicle = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
            if vehicle is not None and vehicle.isPremium:
                avgXp = (avgXp + int(avgXp*(9 - max(min(vehicle.level, 9), 2))/10.0))*1.5
        nextLevelBattleCount = numWithPostfix(math.ceil(tankman.getNextLevelXpCost()/avgXp)) if avgXp > 0 else 'X'
        nextSkillBattleCount = numWithPostfix(math.ceil(tankman.getNextSkillXpCost()/avgXp)) if avgXp > 0 else 'X'
        rankPrefix = '[{0}|{1}] '.format(nextLevelBattleCount, numWithPostfix(tankman.getNextLevelXpCost()))
        rolePrefix = '[{0}|{1}] '.format(nextSkillBattleCount, numWithPostfix(tankman.getNextSkillXpCost()))
        tankmenData['rank'] = rankPrefix + tankmenData['rank']
        tankmenData['role'] = rolePrefix + tankmenData['role']
    old_cm_as_tankmenResponseS(self, data)

CrewMeta.as_tankmenResponseS = new_cm_as_tankmenResponseS

old_rpm_as_updateCurrentVehicleS = ResearchPanelMeta.as_updateCurrentVehicleS

def new_rpm_as_updateCurrentVehicleS(self, name, type, vDescription, earnedXP, isElite, isPremIGR):
    if isElite or not g_currentVehicle.isPresent():
        old_rpm_as_updateCurrentVehicleS(self, name, type, vDescription, earnedXP, isElite, isPremIGR)
        return
    vehDoss = g_itemsCache.items.getVehicleDossier(g_currentVehicle.item.intCD)
    avgXp = vehDoss.getRandomStats().getAvgXP()
    if not avgXp:
        avgXp = 0
    dumper = dumpers.ResearchItemsObjDumper()
    research = ResearchItemsData(dumper)
    research.setRootCD(g_currentVehicle.item.intCD)
    research.load()
    requiredTopXp = 0
    requiredEliteXp = 0
    for node in research._getNodesToInvalidate():
        if node['state'] & NODE_STATE.UNLOCKED > 0:
            continue
        if node['state'] & NODE_STATE.VEHICLE_CAN_BE_CHANGED > 0 and node['displayInfo']['level'] < 0:
            continue
        requiredEliteXp += node['unlockProps'].xpCost
        if node['state'] < NODE_STATE.VEHICLE_CAN_BE_CHANGED:
            requiredTopXp += node['unlockProps'].xpCost
    xp = g_itemsCache.items.stats.vehiclesXPs.get(g_currentVehicle.item.intCD, 0)
    freeXP = g_itemsCache.items.stats.actualFreeXP
    requiredXp = 0
    if requiredTopXp > 0:
        requiredXp = max(requiredTopXp - xp - freeXP, 0)
    else:
        requiredXp = max(requiredEliteXp - xp, 0)
    battleCount = numWithPostfix(math.ceil(requiredXp/avgXp)) if avgXp > 0 else 'X'
    description = vDescription +\
        ' [ {0} <img align="top" src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3"/>'\
        ' {1} <img align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"/>]'.\
        format(battleCount, numWithPostfix(requiredXp))
    old_rpm_as_updateCurrentVehicleS(self, name, type, description, earnedXP, isElite, isPremIGR)

ResearchPanelMeta.as_updateCurrentVehicleS = new_rpm_as_updateCurrentVehicleS
