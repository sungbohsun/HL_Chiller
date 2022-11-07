##training
import os,pickle
import pandas as pd
from utils.DataProcess import Start
from utils.ClooingTowerOptimize import CT_opt

opt = CT_opt()
opt.df = Start('HL_14')
opt.train()
opt.predict(1)