import os
import sys
from src.main import  main

import asyncio

if __name__=="__main__":
    sys.path.insert(0,os.path.jion(os.path.dirname(__file__),"src"))
    main()