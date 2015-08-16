#!/usr/bin/python
# -*- coding: utf-8 -*-

import BigWorld
import math
import json
import os
import ResMgr
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.Scaleform.daapi.view.meta.ResearchPanelMeta import ResearchPanelMeta
from gui.shared import g_itemsCache
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from debug_utils import *

class WotXp(object):

    def __init__(self):
        self.config = {}
        res = ResMgr.openSection('../paths.xml')
        sb = res['Paths']
        vals = sb.values()[0:2]
        for vl in vals:
            path = vl.asString + '/scripts/client/mods/'
            if os.path.isdir(path):
                conf_file = path + 'wotxp.json'
                if os.path.isfile(conf_file):
                    with open(conf_file) as data_file:
                        self.config = json.load(data_file)
                        break
    @staticmethod
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
        nextLevelBattleCount = wotxp.numWithPostfix(math.ceil(tankman.getNextLevelXpCost()/avgXp)) if avgXp > 0 else 'X'
        nextSkillBattleCount = wotxp.numWithPostfix(math.ceil(tankman.getNextSkillXpCost()/avgXp)) if avgXp > 0 else 'X'
        values = {}
        values['freeXp'] = wotxp.numWithPostfix(tankman.descriptor.freeXP)
        values['nextLevelBattleCount'] = nextLevelBattleCount
        values['nextSkillBattleCount'] = nextSkillBattleCount
        values['nextLevelXpCost'] = wotxp.numWithPostfix(tankman.getNextLevelXpCost())
        values['nextSkillXpCost'] = wotxp.numWithPostfix(tankman.getNextSkillXpCost())
        rankPrefix = ''
        rolePrefix = ''
        if tankman.hasNewSkill:
            rankPrefix = wotxp.config.get("tankmanNewSkillRankPrefix", "[+{{freeXp}}]")
            rolePrefix = wotxp.config.get("tankmanNewSkillRolePrefix", "")
        else:
            rankPrefix = wotxp.config.get("tankmanRankPrefix", "[{{nextLevelBattleCount}}|{{nextLevelXpCost}}]")
            rolePrefix = wotxp.config.get("tankmanRolePrefix", "[{{nextSkillBattleCount}}|{{nextSkillXpCost}}]")
        for key in values.keys():
            rankPrefix = rankPrefix.replace('{{%s}}' % key, values[key])
            rolePrefix = rolePrefix.replace('{{%s}}' % key, values[key])
        tankmenData['rank'] = rankPrefix + tankmenData['rank']
        tankmenData['role'] = rolePrefix + tankmenData['role']
    old_cm_as_tankmenResponseS(self, data)

CrewMeta.as_tankmenResponseS = new_cm_as_tankmenResponseS

old_rpm_as_updateCurrentVehicleS = ResearchPanelMeta.as_updateCurrentVehicleS

def new_rpm_as_updateCurrentVehicleS(self, name, type, vDescription, earnedXP, isElite, isPremIGR):
    if isElite or not g_currentVehicle.isPresent():
        old_rpm_as_updateCurrentVehicleS(self, name, type, vDescription, earnedXP, isElite, isPremIGR)
        return
    if wotxp.config.get('debug', False):
        LOG_NOTE(g_currentVehicle.item.n)
    vehDoss = g_itemsCache.items.getVehicleDossier(g_currentVehicle.item.intCD)
    avgXp = vehDoss.getRandomStats().getAvgXP()
    if not avgXp:
        avgXp = 0
    dumper = dumpers.ResearchItemsObjDumper()
    research = ResearchItemsData(dumper)
    research.setRootCD(g_currentVehicle.item.intCD)
    research.load()
    requiredTopXp = 0
    requiredElitXp = 0
    for node in research._getNodesToInvalidate():
        if wotxp.config.get('debug', False):
            LOG_NOTE(node)
        if node['state'] & NODE_STATE.UNLOCKED > 0:
            continue
        if node['state'] & NODE_STATE.VEHICLE_CAN_BE_CHANGED > 0 and node['displayInfo']['level'] < 0:
            continue
        requiredElitXp += node['unlockProps'].xpCost
        if node['state'] < NODE_STATE.VEHICLE_CAN_BE_CHANGED:
            requiredTopXp += node['unlockProps'].xpCost
    xp = g_itemsCache.items.stats.vehiclesXPs.get(g_currentVehicle.item.intCD, 0)
    freeXP = g_itemsCache.items.stats.actualFreeXP
    descriptionPostfix = ''
    extraXp = 0
    values = {}
    if requiredTopXp > 0:
        if requiredTopXp > xp:
            requiredTopXp -= xp
        else:
            xp -= requiredTopXp
            extraXp += xp
            requiredTopXp = 0
        if wotxp.config.get("useFreeXpForModuleResearch", True):
            if requiredTopXp > freeXP:
                requiredTopXp -= freeXP
            else:
                extraXp += freeXP - requiredTopXp
                requiredTopXp = 0
        requiredElitXp = max(requiredElitXp - xp, 0)
        if wotxp.config.get("useFreeXpForVehicleResearch", False):
            requiredElitXp = max(requiredElitXp - freeXP, 0)
        descriptionPostfix = wotxp.config.get("stockVehicle", "[{{topBattleCount}}|{{requiredTopXp}}]") \
            if requiredTopXp > 0 else wotxp.config.get("stockVehicleResearchCompleted", " [+{{extraXp}}]")
    else:
        if requiredElitXp > xp:
            requiredElitXp -= xp
        else:
            extraXp += xp - requiredElitXp
            requiredElitXp = 0
        if wotxp.config.get("useFreeXpForVehicleResearch", False):
            if requiredElitXp > freeXp:
                requiredElitXp -= freeXp
            else:
                extraXp += freeXp - requiredElitXp
                requiredElitXp = 0
        descriptionPostfix = wotxp.config.get("topVehicle", "[{{elitBattleCount}}|{{requiredElitXp}}]") \
            if requiredElitXp > 0 else wotxp.config.get("topVehicleResearchCompleted", " [+{{extraXp}}]")
    values['requiredTopXp'] = wotxp.numWithPostfix(requiredTopXp)
    values['requiredElitXp'] = wotxp.numWithPostfix(requiredElitXp)
    values['topBattleCount'] = wotxp.numWithPostfix(math.ceil(requiredTopXp/avgXp)) if avgXp > 0 else 'X'
    values['elitBattleCount'] = wotxp.numWithPostfix(math.ceil(requiredElitXp/avgXp)) if avgXp > 0 else 'X'
    values['extraXp'] = wotxp.numWithPostfix(extraXp)
    for key in values.keys():
        descriptionPostfix = descriptionPostfix.replace('{{%s}}' % key, values[key])
    old_rpm_as_updateCurrentVehicleS(self, name, type, vDescription + descriptionPostfix, earnedXP, isElite, isPremIGR)

ResearchPanelMeta.as_updateCurrentVehicleS = new_rpm_as_updateCurrentVehicleS

wotxp = WotXp()
