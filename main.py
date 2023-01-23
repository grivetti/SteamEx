from SteamEX.SteamEX import *
from SteamEX.SteamREX import process
from numba import jit
import argparse
from pathlib import Path
import os

parser = argparse.ArgumentParser()

def scrapping(page: int):
    if(not Path("Data/").is_dir()):
        os.mkdir(os.path.join(os.path.curdir, "Data"),777)
    if(not Path("Data/steam.csv").is_file()):
        fp = open('Data/steam.csv', 'w')
        fp.close()
    steam = ParseSteam()
    steam.run(1,page+1)

@jit(parallel=True,fastmath = True,forceobj=True)
def main():
    parser = argparse.ArgumentParser(description = 'Steamex Bot - A Steam Bot for Game Developers')
    
    parser.add_argument('-s','--scrapping',action="store",metavar='N', type=int,
                                default = False,
                                help = 'Pass the number of pages to scrap data from steam website into Data/steam.csv')
    parser.add_argument('-p', '--processing',action = 'store',metavar='N', type=int,
                           default = False,
                            help = 'Pass thr number of ages for processing data to make the recommendation"')
    args = parser.parse_args()
    if(args.scrapping):
        scrapping(args.scrapping)
    elif(args.processing):
        process(args.processing)
    else:
        parser.print_help()
if __name__ == '__main__':
    main()
