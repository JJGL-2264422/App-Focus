import cronometro as crono
import multiprocessing as mul
import sys

if __name__ == '__main__':
    timerThread = mul.Process(target = crono.openTimer)
    timerThread.start()
    while(crono.active):
        a = int(input("Cerrar Cronometro?\nYes (1) - No (0): "))

        if(a==1):
            print("Cronometro cerrado.")
            timerThread.terminate()
            sys.exit()
            break