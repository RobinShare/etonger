# -*- coding: utf-8 -*-
# file: eTonger.py

import abc, os, sys, json, time
import pandas
from . import ascmd
from . import ehelper
import locale
# 解决编码问题
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')


class Lock(object):
    """ Lock: lock maintainer
    """
    def __init__(self):
        self._lockFilePath = os.path.join('/tmp/', 'lock.json')
        self.unlock()


    def lock(self):
        try:
            info = {"lock": 1}
            s = json.dumps(info, ensure_ascii=False, sort_keys=True, indent = 4)                
            with open(self._lockFilePath, 'w+') as fh:
                fh.write(s)
            return True
        except Exception:
            return False


    def unlock(self):
        try:
            info = {"lock": 0}
            s = json.dumps(info, ensure_ascii=False, sort_keys=True, indent = 4)                
            with open(self._lockFilePath, 'w+') as fh:
                fh.write(s)
            return True
        except Exception:
            return False


    def requestLock(self):
        def islocked():
            islock = 0
            with open(self._lockFilePath, 'r', encoding='utf8') as fp:
                islock = json.load(fp).get("lock")
            return islock

        islock = islocked()
        tolerance = 15    # 15 sec
        elapsedTime = 0
        delta = 0.05
        while islock and elapsedTime < tolerance:
            time.sleep(delta)
            elapsedTime += delta
            islock = islocked()
        if islock:
            return False
        self.lock()
        return True


class Service(object):
    """ THS service. up and down daemons, login client, logout client, is client logged in, reLoginClient, getEntrustInfo, lockClient, unlockClient
    """
    def __init__(self):
        self._config = ehelper.Config()
        self.__logging = ehelper.Logging(logType='service')
        self.__lock = Lock()


    def isClientLoggedIn(self):
        """ is client logged in: 选择不加锁, 加不加锁都会产生影响
        Args:
        Returns:
            True/False
        Raises:
        """
        status = False
        cmd = ascmd.isClientLoggedIn
        res = os.popen(cmd).read().strip()
        if res == "true":
            status = True
        return status


    def loginClient(self):
        """ login client
        Args:
        Returns:
            True/False
        Raises:
        """
        status = False
        res = 'failed'

        whetherClientLoggedIn  = self.isClientLoggedIn()

        if whetherClientLoggedIn:
            res = "successed"
        else:
            userid = self._config.userid #账号
            Tpwd = self._config.broker_password #交易密码
            Cpwd = self._config.password #通讯密码

            cmd = ascmd.eTongLoginCmd + ' ' + userid + ' ' + Tpwd + ' ' + Cpwd
            res = os.popen(cmd).read().strip()

        if res == "successed":
            self.__logging.info("login client: " + res)
            status = True
            self.__lock.unlock()
        else:
            self.__logging.error("login client: " + res)
        return status


    def logoutClient(self):
        """ logout client
        Args:
        Returns:
            True/False
        Raises:
        """
        cmd = ascmd.eTongLogoutCmd
        res = os.popen(cmd).read().strip()

        status = False
        if "button 确定" in res:
            self.__logging.info("logout client: " + res)
            status = True
            self.__lock.lock()
        else:
            self.__logging.error("logout client: " + res)
        return status


    def reLoginClient(self):
        """ relogin client
        Args:
        Returns:
            True/False
        Raises:
        """
        self.logoutClient()
        time.sleep(1)
        return self.loginClient()


    def getEntrustInfo(self):
        '''
        ------------------------------------------------------
        功能：查看委托
        参数描述：返回数据格式(bool, dataframe)[status, entrustDf]
        status                  --响应状态：请求是否响应成功
        entrustDf               --委托下单信息表
        -------------------------
        entrustDf的列命名：[选, 委托日期, 委托时间, 证券代码, 证券名称, 操作, 委托状态, 委托数量, 成交数量, 委托价格, 委托子业务, 成交价格, 成交金额, 委托编号, 已撤数量, 股东代码, 交易市场, 客户代码, 资金账号, 错误信息, 特定流水号]

        entrustDf例如：
           选,   委托日期,     委托时间,   证券代码, 证券名称,   操作, 委托状态, 委托数量, 成交数量, 委托价格, 委托子业务, 成交价格, 成交金额, 委托编号, 已撤数量, 股东代码,   交易市场, 客户代码,      资金账号,   错误信息, 特定流水号
        0  '1', '20210420', '21:37:07', '600336', '澳柯玛', '卖', '场外撤单', 100.0,   0.0,     7.09,  '正常委托',   0.0,    0.0,    '3186',  100.0, 'A760989792', '沪A', '3370045659', '3370045659', '20', '21'
        '''
        def isFloat(x):  # 判断字符串或字符x能否强制转换为float数据类型
            try:
                float(x)
                if str(x) in ['inf', 'infinity', 'INF', 'INFINITY', 'True', 'NAN', 'nan', 'False', '-inf', '-INF', '-INFINITY', '-infinity', 'NaN', 'Nan']:
                    return False
                else:
                    return True
            except:
                return False

        status = False
        entrustDf = pandas.DataFrame()
        if not self.__lock.requestLock():
            return status, entrustDf

        try:
            result = os.popen(ascmd.getEntrustMentInfo).read().strip()
            resultList = result.split(",")

            res = resultList.pop(0)
            if res == "successed":
                status = True
                self.__logging.info("get entrustment Info successed")
            else:
                status = False
                self.__logging.error("get entrustment Info failed")

            newList = []
            for iterm in resultList:#数据清洗处理
                endIndex = iterm.find(
                    "of group 1 of group 1 of group 3 of splitter group 1 of splitter group 1 of group 1 of splitter group 1 of window")
                iterm = iterm[:endIndex]
                iterm = iterm.replace("column", "")
                iterm = iterm.replace("group", "")
                iterm = iterm.replace(" ", "")
                newList.append(iterm)

            columnName = []
            num = 21  # 定义每组包含的元素个数
            
            for i in range(0, len(newList), num):
                if i == 0:
                    columnName = newList[i:i + num]
                    # 创建空的newDataFrame以存放持仓rowList信息
                    entrustDf = pandas.DataFrame(columns=columnName)
                else:
                    rowList = newList[i:i + num]
                    for i in range(len(rowList)):
                        if (i > 6 and i < 10) or (i > 10 and i < 13) or i == 14:
                            if isFloat(rowList[i]):
                                rowList[i] = float(rowList[i])
                    # 往entrustDf中插入一行数据
                    entrustDf.loc[len(entrustDf)] = rowList

        except Exception as e:
            self.__logging.error("get entrustment Info failed")

        self.__lock.unlock()
        return status, entrustDf
        

    def lockClient(self):
        '''lockClient
            加锁e海通财
        '''
        status = False
        res = 'failed'

        res = os.popen(ascmd.eTongLockCmd).read().strip()
        
        if res == "successed":
            self.__logging.info("lock client: " + res)
            status = True
            self.__lock.lock()
        else:
            self.__logging.error("lock client: " + res)
        return status


    def unlockClient(self):
        '''unlockClient
            解锁e海通财
        '''
        status = False
        res = 'failed'

        userid = self._config.userid #账号
        unlockePwd = self._config.password #解锁密码

        cmd = ascmd.eTongUnLockCmd + ' ' + userid + ' ' + unlockePwd
        res = os.popen(cmd).read().strip()

        if res == "successed":
            self.__logging.info("unlock client: " + res)
            status = True
            self.__lock.lock()
        else:
            self.__logging.error("unlock client: " + res)
        return status


class Base(metaclass = abc.ABCMeta):
    def __init__(self):
        self._config = ehelper.Config()
        
    @abc.abstractmethod
    def isBrokerLoggedIn(self):
        pass

    @abc.abstractmethod
    def loginBroker(self):
        pass

    @abc.abstractmethod
    def logoutBroker(self):
        pass

    @abc.abstractmethod
    def getAccountInfo(self):
        pass

    @abc.abstractmethod
    def buyAllStocks(self):
        pass

    @abc.abstractmethod
    def sellAllStocks(self):
        pass

    @abc.abstractmethod
    def oneKeyIPO(self):
        pass


class Etonger(Base):
    """ eTonger: trading engine
    """
    def __init__(self):
        super(Etonger, self).__init__()
        self.__logging = ehelper.Logging(logType = 'env_prod')
        self.__service = Service()
        self.__keepInformed = False                             # mail me
        self.__lock = Lock()

    @property
    def keepInformed(self):
        return self.__keepInformed

    @keepInformed.setter
    def keepInformed(self, val = True):
        self.__keepInformed = val


    def isBrokerLoggedIn(self):
        """ is broker logged in
        Args:
        Returns:
            True/False
        Raises:
        """
        status = False
        if not self.__lock.requestLock():
            return status

        status = self.__service.isClientLoggedIn()
        self.__lock.unlock()
        return status


    def loginBroker(self):
        """ loggin broker
        Args:
        Returns:
            True/False
        Raises:
        """
        status = False
        if not self.__lock.requestLock():
            return status

        isOning = self.__service.loginClient()

        if isOning:
            self.__logging.info("login broker: " + "successed")
            status = True
        else:
            self.__logging.error("login broker: " + "failed")
        self.__lock.unlock()
        return status
        

    def logoutBroker(self):
        """ logout broker
        Args:
        Returns:
            True/False
        Raises:
        """
        status = False
        if not self.__lock.requestLock():
            return status

        res = self.__service.logoutClient()

        if res == "successed":
            self.__logging.info("logout broker: " + res)
            status = True
        else:
            self.__logging.error("login broker: " + res)
        self.__lock.unlock()
        return status


    def getAccountInfo(self):
        """
        Args:
        Returns:
            ------------------------------------------------------
            功能：查看账户资金分配
            参数描述：返回字典dict数据格式
            -------------------------
            dict的key命名：
            status                  --响应状态：请求是否响应成功
            dataAssetInStock        --总市值
            dataAssetCanBeUsed      --可用
            dataTodayProfitAndLoss  --当日盈亏
            dataAssetBalance        --资金余额
            dataSHNewIPOAmount      --沪新股额度
            dataKCNewIPOAmouut      --科创新股额度
            dataAssetAll            --参考总资产
            dataAssetTurnBank       --可取
            dataAssetProfitAndLoss  --浮动盈亏
            dataAssetOnWay          --在途
            dataSZNewIPOAmount      --深新股额度
            dataStockBalance        --股质余额
            dict例如：
            {"status": True
            'dataAssetInStock': 197298.0,
            'dataAssetCanBeUsed': 460.29,
            'dataTodayProfitAndLoss': -3997.71,
            'dataAssetBalance': 0.0,
            'dataSHNewIPOAmount': 17000.0,
            'dataKCNewIPOAmouut': 17500.0,
            'dataAssetAll': 197758.29,
            'dataAssetTurnBank': 0.0,
            'dataAssetProfitAndLoss': -38331.22,
            'dataAssetOnWay': -460.29,
            'dataSZNewIPOAmount': 1500.0,
            'dataStockBalance': 0.0}
        Raises:
        """
        status = False
        accountInfo = {}
        if not self.__lock.requestLock():
            return accountInfo

        try:
            result = os.popen(ascmd.getAssetInfoCmd).read().strip()
            resultList = result.split(",")
            
            res = resultList.pop(0)
            if res == "successed":
                status = True
                self.__logging.info("get account info successed")
            else:
                status = False
                self.__logging.error("get account info failed")

            newList = []
            for iterm in resultList:#数据清洗处理
                startIndex = iterm.find("text")
                endIndex = iterm.find(
                    "of group 1 of group 1 of splitter group 1 of window")
                iterm = iterm[startIndex:endIndex]
                iterm = iterm.replace("column", "")
                iterm = iterm.replace("group", "")
                iterm = iterm.replace("text", "")
                iterm = iterm.replace(" ", "")
                newList.append(iterm)

            accountInfo["status"] = status
            accountInfo['dataAssetInStock'] = float(newList[11])
            accountInfo['dataAssetCanBeUsed'] = float(newList[14])
            accountInfo['dataTodayProfitAndLoss'] = float(newList[12])
            accountInfo['dataAssetBalance'] = float(newList[0])
            accountInfo['dataSHNewIPOAmount'] = float(newList[6])
            accountInfo['dataKCNewIPOAmouut'] = float(newList[23])
            accountInfo['dataAssetAll'] = float(newList[15])
            accountInfo['dataAssetTurnBank'] = float(newList[17])
            accountInfo['dataAssetProfitAndLoss'] = float(newList[2])
            accountInfo['dataAssetOnWay'] = float(newList[4])
            accountInfo['dataSZNewIPOAmount'] = float(newList[5])
            accountInfo['dataStockBalance'] = float(newList[22])
        except Exception as e:
            self.__logging.error("get account info faile："+str(e))
        self.__lock.unlock()
        return accountInfo
        

    def getEntrustMentInfo(self):
        '''
        ------------------------------------------------------
        功能：查看委托
        参数描述：返回数据格式(bool, dataframe)[status, entrustDf]
        status                  --响应状态：请求是否响应成功
        entrustDf               --委托下单信息表
        -------------------------
        entrustDf的列命名：[选, 委托日期, 委托时间, 证券代码, 证券名称, 操作, 委托状态, 委托数量, 成交数量, 委托价格, 委托子业务, 成交价格, 成交金额, 委托编号, 已撤数量, 股东代码, 交易市场, 客户代码, 资金账号, 错误信息, 特定流水号]

        entrustDf例如：
           选,   委托日期,     委托时间,   证券代码, 证券名称,   操作, 委托状态, 委托数量, 成交数量, 委托价格, 委托子业务, 成交价格, 成交金额, 委托编号, 已撤数量, 股东代码,   交易市场, 客户代码,      资金账号,   错误信息, 特定流水号
        0  '1', '20210420', '21:37:07', '600336', '澳柯玛', '卖', '场外撤单', 100.0,   0.0,     7.09,  '正常委托',   0.0,    0.0,    '3186',  100.0, 'A760989792', '沪A', '3370045659', '3370045659', '20', '21'
        '''
        status = False
        entrustDf = pandas.DataFrame()
        status, entrustDf = self.__service.getEntrustInfo()
       
        return status, entrustDf


    def sellAllStocks(self, stock_codeList=[], priceList=[], amountList=[], mode=2):
        """
        Args:
            ------------------------------------------------------
            功能：下多只股票的卖单
            备注：stock_codeList、priceList、amountList三者的值必须一一对应，mode=0时，priceList不能为空。
            参数描述：
            -------------------------
            名称            类型          描述
            stock_codeList  list         股票代码列表：交易所的代码，不带任何如：.SH .SZ等前后置，正确的如：['601990','000681']
            priceList       list         卖出价格列表：仅限价委托须要[15.4, 14.8]
            amountList      list         卖出数量列表：必须以手为基数填写，如：[200, 300]
            mode            int          委托类型：沪户：mode=0--限价委托【默认】;mode=1--最优五档成交剩余撤销;mode=2--最优五档成交剩余转限价
                                                深户：mode=0--限价委托【默认】;mode=1--对方最优价格;mode=2--本方最优价格;
                                                     mode=3--即时成交剩撤;mode=4--最优五档成交剩余撤销;mode=5--全成交或撤销
        Returns:
            (statusList, entrustNoDict) 
            statusList                  --响应状态列表：请求是否响应成功         
            entrustNoDict               --字典格式 {'委托编号': '证券代码', '3290': '600336'}  
        Raises:
        """
        statusList = []
        entrustNoDict = {}
        if mode == 0:
            for index, stock_code in enumerate(stock_codeList):
                status, entrustNo = self.sellAStock(
                    stock_code=stock_code, price=priceList[index], amount=amountList[index], mode=mode)
                entrustNoDict[entrustNo] = stock_code
                statusList.append(status)


        elif mode == 1 or mode == 2 or mode == 3 or mode == 4 or mode ==5:
            for index, stock_code in enumerate(stock_codeList):
                status, entrustNo = self.sellAStock(stock_code=stock_code,
                                amount=amountList[index], mode=mode)
                entrustNoDict[entrustNo] = stock_code
                statusList.append(status)

        return statusList, entrustNoDict


    def sellAStock(self, stock_code='', price=None, amount=100, mode=0):
        """
        Args:
            ------------------------------------------------------
            功能：下指定某只股票的卖单
            参数描述：
            -------------------------
            名称            类型              描述
            stock_code      str             股票代码：交易所的代码，不带任何如：.SH .SZ等前后置，正确的如：'601990'
            price           float           卖出价格：仅限价委托须要
            amount          int             卖出数量：必须以手为基数填写，如：100、200、300股
            mode            int             委托类型：沪户：mode=0--限价委托【默认】;mode=1--最优五档成交剩余撤销;mode=2--最优五档成交剩余转限价
                                                    深户：mode=0--限价委托【默认】;mode=1--对方最优价格;mode=2--本方最优价格;
                                                    mode=3--即时成交剩撤;mode=4--最优五档成交剩余撤销;mode=5--全成交或撤销
        Returns:
            (status, entrustNo)
        Raises:
        """
        def mailMe(action = 'sell', assetsName = '', assetsCode = '', price = '', amount = '', status = '', comments = ''):
            try:
                if self.__keepInformed:
                    action = 'entrust ' + action
                    priceLogged = 'best price' if price is None else price
                    tlog = ehelper.Tlog(action = action, assetsName = assetsName, assetsCode = assetsCode, price = priceLogged, amount = amount, status = status, comments = '')
                    ehelper.Mail(tlog)
            except Exception as e:
                self.__logging.error("mailing failed with error: " + str(e))
            return

        status = False
        res = "failed"
        entrustNo = ''
        entrustNoListBefore = []
        entrustNoListAfter = []
        #交易前委托状态
        if status == False:
            statusGetEntrustInfo, entrustDf = self.__service.getEntrustInfo()
            entrustNoListBefore = entrustDf['委托编号'].values.tolist()

        if not self.__lock.requestLock():
            return status, contractNo

        try:
            # result = os.popen(cmd % (stock_code, price, amount, mode)).read()
            command = ascmd.sellAStockCmd + ' ' + stock_code + ' ' + \
                str(price) + ' ' + str(amount) + ' ' + str(mode)
            res = os.popen(command).read().strip()

            if res == "failed":
                status = False

                self.__logging.error("issuing entrust failed: " + 'sell' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount) + '. Err: ' + 'unknow!')
                mailMe(action = 'sell', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "failed")
            else:
                status = True

        except Exception as e:
            self.__logging.error("issuing entrust failed: " + 'sell' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount) + '. Err: ' + str(e))
            mailMe(action = 'sell', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "failed")

        self.__lock.unlock()

        #交易后委托状态
        if status == True:
            statusGetEntrustInfo, entrustDf = self.__service.getEntrustInfo()
            entrustNoListAfter = entrustDf['委托编号'].values.tolist()

        if entrustNoListBefore and entrustNoListAfter:
            #list作差集运算（entrustNoListAfter - entrustNoListBefore）
            #entrustNo = list(set(entrustNoListAfter).difference(set(entrustNoListBefore)))[-1]
            entrustNoList = list(set(entrustNoListAfter).difference(set(entrustNoListBefore)))
            if entrustNoList:
                entrustNo = entrustNoList[-1]

        if res == "successed" and entrustNo:
            status = True

            self.__logging.info("issuing entrust successed: " + 'sell' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount))
            mailMe(action = 'sell', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "successed")
        else:
            status = False
            
            self.__logging.error("issuing entrust failed: " + 'sell' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount) + '. Err: ' + 'unknow!')
            mailMe(action = 'sell', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "failed")

        return status, entrustNo


    def buyAllStocks(self, stock_codeList=[], priceList=[], amountList=[], mode=2):
        """
        Args:
            ------------------------------------------------------
            功能：下多只股票的买单
            备注：stock_codeList、priceList、amountList三者的值必须一一对应，mode=0时，priceList不能为空。
            参数描述：
            -------------------------
            名称            类型          描述
            stock_codeList  list         股票代码列表：交易所的代码，不带任何如：.SH .SZ等前后置，正确的如：['601990','000681']
            priceList       list         买入价格列表：仅限价委托须要[15.4, 14.8]
            amountList      list         买入数量列表：必须以手为基数填写，如：[200, 300]
            mode            int          委托类型：沪户：mode=0--限价委托【默认】;mode=1--最优五档成交剩余撤销;mode=2--最优五档成交剩余转限价
                                                 深户：mode=0--限价委托【默认】;mode=1--对方最优价格;mode=2--本方最优价格;
                                                      mode=3--即时成交剩撤;mode=4--最优五档成交剩余撤销;mode=5--全成交或撤销
        Returns:
            (statusList, entrustNoDict) 
            statusList                  --响应状态列表：请求是否响应成功         
            entrustNoDict               --字典格式 {'委托编号': '证券代码', '3290': '600336'}  
        Raises:
        """
        statusList = []
        entrustNoDict = {}
        if mode == 0:
            for index, stock_code in enumerate(stock_codeList):
                status, entrustNo = self.buyAStock(
                    stock_code=stock_code, price=priceList[index], amount=amountList[index], mode=mode)
                entrustNoDict[entrustNo] = stock_code
                statusList.append(status)

        elif mode == 1 or mode == 2 or mode == 3 or mode == 4 or mode ==5:
            for index, stock_code in enumerate(stock_codeList):
                status, entrustNo = self.buyAStock(stock_code=stock_code, amount=amountList[index], mode=mode)
                entrustNoDict[entrustNo] = stock_code
                statusList.append(status)

        return statusList, entrustNoDict

  
    def buyAStock(self, stock_code='', price=0, amount=100, mode=0):
        """
        Args:
            ------------------------------------------------------
            功能：下指定某只股票的买单
            参数描述：
            -------------------------
            名称            类型              描述
            stock_code      str             股票代码：交易所的代码，不带任何如：.SH .SZ等前后置，正确的如：'601990'
            price           float           买入价格：仅限价委托须要
            amount          int             买入数量：必须以手为基数填写，如：100、200、300股
            mode            int             委托类型：沪户：mode=0--限价委托【默认】;mode=1--最优五档成交剩余撤销;mode=2--最优五档成交剩余转限价
                                                    深户：mode=0--限价委托【默认】;mode=1--对方最优价格;mode=2--本方最优价格;
                                                    mode=3--即时成交剩撤;mode=4--最优五档成交剩余撤销;mode=5--全成交或撤销
        Returns:
            (status, entrustNo)
        Raises:
        """
        def mailMe(action = 'buy', assetsName = '', assetsCode = '', price = '', amount = '', status = '', comments = ''):
            try:
                if self.__keepInformed:
                    action = 'entrust ' + action
                    priceLogged = 'best price' if price is None else price
                    tlog = ehelper.Tlog(action = action, assetsName = assetsName, assetsCode = assetsCode, price = priceLogged, amount = amount, status = status, comments = '')
                    ehelper.Mail(tlog)
            except Exception as e:
                self.__logging.error("mailing failed with error: " + str(e))
            return

        status = False
        res = "failed"
        entrustNo = ''
        entrustNoListBefore = []
        entrustNoListAfter = []
        #交易前委托状态
        if status == False:
            statusGetEntrustInfo, entrustDf = self.__service.getEntrustInfo()
            entrustNoListBefore = entrustDf['委托编号'].values.tolist()

        if not self.__lock.requestLock():
            return status, contractNo

        try:
            # result = os.popen(cmd % (stock_code, price, amount, mode)).read()
            command = ascmd.buyAStockCmd + ' ' + stock_code + ' ' + \
                str(price) + ' ' + str(amount) + ' ' + str(mode)
            res = os.popen(command).read().strip()

            if res == "failed":
                status = False

                self.__logging.error("issuing entrust failed: " + 'buy' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount) + '. Err: ' + 'unknow!')
                mailMe(action = 'buy', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "failed")
            else:
                status = True

        except Exception as e:
            self.__logging.error("issuing entrust failed: " + 'buy' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount) + '. Err: ' + str(e))
            mailMe(action = 'buy', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "failed")

        self.__lock.unlock()

        #交易后委托状态
        if status == True:
            statusGetEntrustInfo, entrustDf = self.__service.getEntrustInfo()
            entrustNoListAfter = entrustDf['委托编号'].values.tolist()

        if entrustNoListBefore and entrustNoListAfter:
            #list作差集运算（entrustNoListAfter - entrustNoListBefore）
            entrustNoList = list(set(entrustNoListAfter).difference(set(entrustNoListBefore)))
            if entrustNoList:
                entrustNo = entrustNoList[-1]

        if res == "successed" and entrustNo:
            status = True

            self.__logging.info("issuing entrust successed: " + 'buy' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount))
            mailMe(action = 'buy', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "successed")
        else:
            status = False

            self.__logging.error("issuing entrust failed: " + 'buy' + ' ' + 'stock' + ' ' + stock_code + ' ' + str(price) + ' ' + str(amount) + '. Err: ' + 'unknow!')
            mailMe(action = 'buy', assetsName = 'stock', assetsCode = stock_code, price = price, amount = amount, status = "failed")

        return status, entrustNo


    def getKeepPositionOnBuyF1(self):
        """
        Args:
            ------------------------------------------------------
            功能：'双向委托F6'模块的股票持有仓位
            参数描述：返回dataframe数据格式
            -------------------------
            dataframe的列命名：['序号', 证券名称', '证券代码', '证券余额', '证券可用', '冻结数量', '最新价', '成本价', '成本(价港币)', '市值', '浮动盈亏', '当日参考盈亏', '当日盈亏比例', '盈亏比例%', '交易市场', '股东账号']

            dataframe例如：
               序号 证券名称, 证券代码, 证券余额, 证券可用, 冻结数量, 最新价, 成本价, 成本(价港币), 市值, 浮动盈亏, 当日参考盈亏, 当日盈亏比例, 盈亏比例%, 交易市场, 股东账号
            0   1 '南京证券', '601990', 5800.0, 5800.0, 0.0,     14.46, 14.632, 14.632,   83868.0, -996.92,   '--',        0.0,      -1.18,   '沪A', 'A760989792'
        Returns:
            positionDataFrame
        Raises:
        """
        def isFloat(x):  # 判断字符串或字符x能否强制转换为float数据类型
            try:
                float(x)
                if str(x) in ['inf', 'infinity', 'INF', 'INFINITY', 'True', 'NAN', 'nan', 'False', '-inf', '-INF', '-INFINITY', '-infinity', 'NaN', 'Nan']:
                    return False
                else:
                    return True
            except:
                return False

        status = False
        positionDataFrame = pandas.DataFrame()
        if not self.__lock.requestLock():
            return positionDataFrame

        try:
            result = os.popen(ascmd.getKeepPositionOnBuyF1Cmd).read().strip()
            resultList = result.split(",")
            
            res = resultList.pop(0)
            if res == "successed":
                status = True
                self.__logging.info("get BuyF1 position info successed")
            else:
                status = False
                self.__logging.error("get BuyF1 position info failed")

            newList = []
            for iterm in resultList: #数据清洗处理
                endIndex = iterm.find(
                    "of group 1 of group 1 of splitter group 1 of group 1 of splitter group 1 of window")
                iterm = iterm[:endIndex]
                iterm = iterm.replace("column", "")
                iterm = iterm.replace("group", "")
                iterm = iterm.replace(" ", "")
                newList.append(iterm)

            columnName = []
            num = 16  # 定义每组包含的元素个数
            for i in range(0, len(newList), num):
                if i == 0:
                    columnName = newList[i:i + num]
                    # 创建空的positionDataFrame以存放持仓rowList信息
                    positionDataFrame = pandas.DataFrame(columns=columnName)
                else:
                    rowList = newList[i:i + num]
                    for i in range(len(rowList)):
                        if i > 2 and i < 14:
                            if isFloat(rowList[i]):
                                rowList[i] = float(rowList[i])
                    # 往positionDataFrame中插入一行数据
                    positionDataFrame.loc[len(positionDataFrame)] = rowList

            #DataFrame删除列“市值”为0.000的行
            positionDataFrame = positionDataFrame.drop(positionDataFrame[positionDataFrame["市值"]==0.000].index)

        except Exception as e:
            self.__logging.error("get BuyF1 position info faile："+str(e))
        self.__lock.unlock()
        return positionDataFrame


    def getKeepPositionOnAssetModel(self):
        """
        Args:
            ------------------------------------------------------
            功能：'查询F4'->'资金股份'模块的股票持有仓位
            参数描述：返回dataframe数据格式
            -------------------------
            dataframe的列命名：['序号', 证券名称', '证券代码', '证券余额', '证券可用', '冻结数量', '最新价', '成本价', '成本(价港币)', '市值', '浮动盈亏', '当日参考盈亏', '当日盈亏比例', '盈亏比例%', '交易市场', '股东账号']

            dataframe例如：
               序号 证券名称, 证券代码, 证券余额, 证券可用, 冻结数量, 最新价, 成本价, 成本(价港币), 市值, 浮动盈亏, 当日参考盈亏, 当日盈亏比例, 盈亏比例%, 交易市场, 股东账号
            0   1 '南京证券', '601990', 5800.0, 5800.0, 0.0,     14.46, 14.632, 14.632,   83868.0, -996.92,   '--',        0.0,      -1.18,   '沪A', 'A760989792'
        Returns:
            positionDataFrame
        Raises:
        """
        def isFloat(x):  # 判断字符串或字符x能否强制转换为float数据类型
            try:
                float(x)
                if str(x) in ['inf', 'infinity', 'INF', 'INFINITY', 'True', 'NAN', 'nan', 'False', '-inf', '-INF', '-INFINITY', '-infinity', 'NaN', 'Nan']:
                    return False
                else:
                    return True
            except:
                return False

        status = False
        positionDataFrame = pandas.DataFrame()# 创建空的newDataFrame以存放持仓rowList信息
        if not self.__lock.requestLock():
            return positionDataFrame

        try:
            result = os.popen(ascmd.getKeepPositionOnAssetModelCmd).read().strip()
            resultList = result.split(",")

            res = resultList.pop(0)
            if res == "successed":
                status = True
                self.__logging.info("get AssetModel F4 position info successed")
            else:
                status = False
                self.__logging.error("get AssetModel F4 position info failed")

            newList = []
            for iterm in resultList:  #数据清洗处理
                endIndex = iterm.find(
                    "of group 3 of group 1 of splitter group 1 of window")
                iterm = iterm[:endIndex]
                iterm = iterm.replace("column", "")
                iterm = iterm.replace("group", "")
                iterm = iterm.replace(" ", "")
                newList.append(iterm)

            columnName = []
            num = 16  # 定义每组包含的元素个数  
            for i in range(0, len(newList), num):
                if i == 0:
                    columnName = newList[i:i + num]
                    positionDataFrame = pandas.DataFrame(
                        columns=columnName)  # 添加newDataFrame列的命名
                else:
                    rowList = newList[i:i + num]
                    for i in range(len(rowList)):
                        if i > 2 and i < 14:
                            if isFloat(rowList[i]):
                                rowList[i] = float(rowList[i])
                    # 往positionDataFrame中插入一行数据
                    positionDataFrame.loc[len(positionDataFrame)] = rowList

            #DataFrame删除列“市值”为0.000的行
            positionDataFrame = positionDataFrame.drop(positionDataFrame[positionDataFrame["市值"]==0.000].index)

        except Exception as e:
            self.__logging.error("get AssetModel F4 position info faile："+str(e))
        self.__lock.unlock()
        return positionDataFrame


    def checkPosition(self):
        """
        Args:
            ------------------------------------------------------
            功能：查看持有仓位
            参数描述：返回dataframe数据格式
            -------------------------
            dataframe的列命名：['序号', 证券名称', '证券代码', '证券余额', '证券可用', '冻结数量', '最新价', '成本价', '成本(价港币)', '市值', '浮动盈亏', '当日参考盈亏', '当日盈亏比例', '盈亏比例%', '交易市场', '股东账号']

            dataframe例如：
               序号 证券名称, 证券代码, 证券余额, 证券可用, 冻结数量, 最新价, 成本价, 成本(价港币), 市值, 浮动盈亏, 当日参考盈亏, 当日盈亏比例, 盈亏比例%, 交易市场, 股东账号
            0   1 '南京证券', '601990', 5800.0, 5800.0, 0.0,     14.46, 14.632, 14.632,   83868.0, -996.92,   '--',        0.0,      -1.18,   '沪A', 'A760989792'
        Returns:
            positionDataFrame
        Raises:
        """
        # 首先考虑在'双向委托F6'模块获取持仓信息
        positionDataFrame = self.getKeepPositionOnBuyF1()
        if positionDataFrame.empty:
            # 如果positionDf为空，再考虑从'查询F4'->'资金股份'模块获取持仓信息
            positionDataFrame = self.getKeepPositionOnAssetModel()
        return positionDataFrame


    def cancelAllSellStocks(self):
        """
        Args:
            -------------------------
            功能：撤委托的所有卖单
            -------------------------
        Returns:
            status
        Raises:
        """
        status = False
        if not self.__lock.requestLock():
            return status

        try:
            res = os.popen(ascmd.cancelAllSellStocksCmd).read().strip()

            if res == "successed":
                status = True
                self.__logging.info("cacel All Sell Stocks successed!" )
            else:
                status = False
                self.__logging.error("cacel All Sell Stocks faile："+"error unknow!")

        except Exception as e:
            self.__logging.error("cacel All Sell Stocks faile："+str(e))
        self.__lock.unlock()
        return status
        
   
    def cancelAllStocks(self):
        """
        Args:
            -------------------------
            功能：撤委托的所有单
            -------------------------
        Returns:
            status
        Raises:
        """
        status = False
        if not self.__lock.requestLock():
            return status

        try:
            res = os.popen(ascmd.cancelAllStocksCmd).read().strip()

            if res == "successed":
                status = True
                self.__logging.info("cacel All Stocks successed!" )
            else:
                status = False
                self.__logging.error("cacel All Stocks faile："+"error unknow!")

        except Exception as e:
            self.__logging.error("cacel All Stocks faile："+str(e))
        self.__lock.unlock()
        return status
        

    def cancelAllBuyStocks(self):
        """
        Args:
            -------------------------
            功能：撤委托的所有买单
            -------------------------
        Returns:
            status
        Raises:
        """
        status = False
        if not self.__lock.requestLock():
            return status

        try:
            res = os.popen(ascmd.cancelAllBuyStocksCmd).read().strip()

            if res == "successed":
                status = True
                self.__logging.info("cacel All Buy Stocks successed!" )
            else:
                status = False
                self.__logging.error("cacel All Buy Stocks faile："+"error unknow!")

        except Exception as e:
            self.__logging.error("cacel All Buy Stocks faile："+str(e))
        self.__lock.unlock()
        return status
        

    def oneKeyIPO(self):
        """
        Args:
            -------------------------
            功能：当日一键打新，新股申购
            -------------------------
        Returns:
            status
        Raises:
        """
        status = False
        if not self.__lock.requestLock():
            return status

        try:
            res = os.popen(ascmd.oneKeyIPOCmd).read().strip()

            if res == "successed":
                status = True
                self.__logging.info("one key IPO successed!" )
            else:
                status = False
                self.__logging.error("one key IPO faile："+"error unknow!")

        except Exception as e:
            self.__logging.error("one key IPO faile："+str(e))
        self.__lock.unlock()
        return status

        


if __name__ == "__main__":
    pass
    # --- Service
    # -----------------------------------------
    # service = Service()

    # status = service.isClientLoggedIn()
    # print(status)
    # time.sleep(1)

    # status = service.loginClient()
    # print(status)
    # time.sleep(1)

    # status = service.isClientLoggedIn()
    # print(status)
    # time.sleep(1)

    # status = service.logoutClient()
    # print(status)
    # time.sleep(1)

    # status = service.isClientLoggedIn()
    # print(status)
    # time.sleep(1)

    # status = service.reLoginClient()
    # print(status)
    # time.sleep(1)

    # status, entrustDf = service.getEntrustInfo()
    # print("status:", status, "entrustDf:", entrustDf)

    # time.sleep(5)
    # status = service.lockClient()
    # print("status:",status)
    

    #---暂时不知道锁屏后怎么解锁操作，待定
    # service.unlockClient()



    # --- Etonger
    # -----------------------------------------
    # tonger = Etonger()
    # tonger.keepInformed = True

    # status = tonger.isBrokerLoggedIn()
    # print(status)

    # status = tonger.loginBroker()
    # print(status)

    # status = tonger.isBrokerLoggedIn()
    # print(status)
    
    # accountInfo = tonger.getAccountInfo()
    # print("accountInfo:",accountInfo)

    # status, entrustDf = tonger.getEntrustMentInfo()
    # print("status:",status, "entrustDf:", entrustDf)

    # status, entrustNo = tonger.sellAStock(stock_code='600336', price=7.45, amount=100, mode=0)
    # print("status:", status, "entrustNo:", entrustNo)

    # status, entrustNo = tonger.sellAStock(stock_code='300059', price=32.29, amount=100, mode=5)
    # print("status:", status, "entrustNo:", entrustNo)

    # statusList, entrustNoDict = tonger.sellAllStocks(stock_codeList=['600336','300059'], priceList=[7.28, 32.88], amountList=[100,500], mode=0)
    # print("statusList:", statusList, "entrustNoDict:", entrustNoDict)

    # status, entrustNo = tonger.buyAStock(stock_code='300059', price=29.29, amount=100, mode=0)
    # print("status:", status, "entrustNo:", entrustNo)

    # status, entrustNo = tonger.buyAStock(stock_code='600336', price=7.29, amount=100, mode=2)
    # print("status:", status, "entrustNo:", entrustNo)

    # statusList, entrustNoDict = tonger.buyAllStocks(stock_codeList=['600336','300059'], priceList=[6.59, 28.29], amountList=[100,100], mode=0)
    # print("statusList:", statusList, "entrustNoDict:", entrustNoDict)

    # positionDataFrame = tonger.checkPosition()
    # print("positionDataFrame:", positionDataFrame)
    
    # time.sleep(15.0)
    # status = tonger.cancelAllSellStocks()
    # print(status)

    # status = tonger.cancelAllStocks()
    # print(status)

    # status = tonger.cancelAllBuyStocks()
    # print(status)
    
    # status = tonger.oneKeyIPO()
    # print(status)

    
