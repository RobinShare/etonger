# -*- coding: utf-8 -*-

from etonger import etonger #After you have run "pip3 install -i https://test.pypi.org/simple/ etonger==1.1.7"
import time

if __name__ == "__main__":
    pass
    # --- Service
    # -----------------------------------------
    service = etonger.Service()

    status = service.isClientLoggedIn()
    print(status)
    time.sleep(1)

    status = service.loginClient()
    print(status)
    time.sleep(1)

    status = service.isClientLoggedIn()
    print(status)
    time.sleep(1)

    status = service.logoutClient()
    print(status)
    time.sleep(1)

    status = service.isClientLoggedIn()
    print(status)
    time.sleep(1)

    status = service.reLoginClient()
    print(status)
    time.sleep(1)

    status, entrustDf = service.getEntrustInfo()
    print("status:", status, "entrustDf:", entrustDf)

    time.sleep(5)
    status = service.lockClient()
    print("status:",status)
    

    #---暂时不知道锁屏后怎么解锁操作，待定
    # service.unlockClient()



    # --- Etonger
    # -----------------------------------------
    tonger = etonger.Etonger()
    tonger.keepInformed = True

    status = tonger.isBrokerLoggedIn()
    print(status)

    status = tonger.loginBroker()
    print(status)

    status = tonger.isBrokerLoggedIn()
    print(status)
    
    accountInfo = tonger.getAccountInfo()
    print("accountInfo:",accountInfo)

    status, entrustDf = tonger.getEntrustMentInfo()
    print("status:",status, "entrustDf:", entrustDf)

    status, entrustNo = tonger.sellAStock(stock_code='600336', price=7.45, amount=100, mode=0)
    print("status:", status, "entrustNo:", entrustNo)

    status, entrustNo = tonger.sellAStock(stock_code='300059', price=32.29, amount=100, mode=5)
    print("status:", status, "entrustNo:", entrustNo)

    statusList, entrustNoDict = tonger.sellAllStocks(stock_codeList=['600336','300059'], priceList=[7.28, 32.88], amountList=[100,500], mode=0)
    print("statusList:", statusList, "entrustNoDict:", entrustNoDict)

    status, entrustNo = tonger.buyAStock(stock_code='300059', price=29.29, amount=100, mode=0)
    print("status:", status, "entrustNo:", entrustNo)

    status, entrustNo = tonger.buyAStock(stock_code='600336', price=7.29, amount=100, mode=2)
    print("status:", status, "entrustNo:", entrustNo)

    statusList, entrustNoDict = tonger.buyAllStocks(stock_codeList=['600336','300059'], priceList=[6.59, 28.29], amountList=[100,100], mode=0)
    print("statusList:", statusList, "entrustNoDict:", entrustNoDict)

    positionDataFrame = tonger.checkPosition()
    print("positionDataFrame:", positionDataFrame)
    
    time.sleep(15.0)
    status = tonger.cancelAllSellStocks()
    print(status)

    status = tonger.cancelAllStocks()
    print(status)

    status = tonger.cancelAllBuyStocks()
    print(status)
    
    status = tonger.oneKeyIPO()
    print(status)
