#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from debug_utils import *

old_cm_as_tankmenResponseS = CrewMeta.as_tankmenResponseS

def new_cm_as_tankmenResponseS(self, data):
    for tankmenData in data['tankmen']:
        tankmenData['rank'] = '[1111/2222] ' + tankmenData['rank']
        tankmenData['role'] = '[3333/4444] ' + tankmenData['role']
    old_cm_as_tankmenResponseS(self, data)

CrewMeta.as_tankmenResponseS = new_cm_as_tankmenResponseS

