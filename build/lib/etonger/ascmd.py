# -*- coding: utf-8 -*-
# file: eTongAsCmd.py


# 是否已登录海通e海通财客户端
isClientLoggedIn = """/usr/bin/osascript -e '
on isClientLoggedIn()
    tell application "System Events"
        tell application "System Events" to set isRunning to exists (processes where name is "e海通财")
        if isRunning then
            tell process "e海通财" to activate
            delay 4
            tell front window of process "e海通财"
                try
                    delay 0.25
                    set val to get value of attribute "AXTitle" of button "通讯设置" of window "e海通财" of application process "e海通财" of application "System Events"
                    if val contains "通讯设置" then
                        return false
                    end if
                    return true
                on error
                    return true
                end try
            end tell
        end if
    end tell
end isClientLoggedIn

isClientLoggedIn()
'"""


# 自动登录
eTongLoginCmd = """/usr/bin/osascript -e '
on loginClientHelp(userid, Tpwd, Cpwd)
    tell application "System Events"
        tell process "e海通财"
            --选中证券代码的输入框
            set StaticText to text field 1 of pop up button 2 of window "e海通财" of application process "e海通财" of application "System Events"
            set {x, y} to position of StaticText
            do shell script "/usr/local/bin/cliclick c:" & x+4 & "," & y+2

            keystroke userid --资金账号
            delay 1

            set value of text field 2 of window "e海通财" of application process "e海通财" of application "System Events" to Tpwd --交易密码
            delay 1

            set value of text field 1 of window "e海通财" of application process "e海通财" of application "System Events" to Cpwd --通讯密码
            delay 1
            
            click button "登录" of window "e海通财" of application process "e海通财" of application "System Events"

            delay 6 --Wait for the application to login and load data, can not remove
        
            try 
                --遇到登录成功后客户端弹窗的应急处理
                click button 1 of window 1
                delay 3

                --让e海通财的窗口足够大，便于程序后续自动下单
                tell front window
                    set {position, size} to {{0, 28}, {1920, 898}}
                end tell

                click button "刷新[F5]" of splitter group 1 of window 1
                set res to "successed"
            on error
                set res to "failed"
            end try
    
        end tell
    end tell
end loginClientHelp


on loginClient(userid, Tpwd, Cpwd)
    --启动交易系统
    set isOning to false
    repeat 3 times
        tell application "System Events" to set isOning to exists (processes where name is "海通e海通财")
        if not isOning then
            
            try
                tell application "海通e海通财" to quit
                delay 1
            end try

            tell application "海通e海通财" to activate
            delay 8 -- wait process start up, can not remove
            
            tell application "System Events"
                tell process "海通e海通财" --开启登陆界面
                    click button "   委托   " of window 1
                    delay 3
                end tell
            end tell
            tell application "System Events" to set isOning to exists (processes where name is "海通e海通财")
        end if

        if isOning then
            exit repeat
        end if
    end repeat

    --登录交易系统
    set isRunning to false
    repeat 3 times
        try
            tell application "System Events"
                tell process "海通e海通财" --开启登陆界面
                    click button "   委托   " of window 1
                    delay 3
                end tell
            end tell

            loginClientHelp(userid, Tpwd, Cpwd)
            tell application "System Events" to set isRunning to exists (processes where name is "e海通财")
        end try

        tell application "System Events" to set isRunning to exists (processes where name is "e海通财")
        if not isRunning then
            loginClientHelp(userid, Tpwd, Cpwd)
            tell application "System Events" to set isRunning to exists (processes where name is "e海通财")
        end if
        
        if isRunning then
            exit repeat
        end if
    end repeat
    
    -- return status
    if isRunning then
        return "successed"
    else
        return "failed"
    end if
end loginClient


on run {userid, Tpwd, Cpwd}
    --set userid to "XXXXXXX"
    --set Tpwd to "XXXXXX"
    --set Cpwd to "XXXXXX"
    loginClient(userid, Tpwd, Cpwd)
end run
'"""


# 退出
eTongLogoutCmd = """/usr/bin/osascript -e '
try    
    tell application "System Events"
    tell process "e海通财"
        click button "退出" of splitter group 1 of window 1
        delay 1
        click button "确定" of group 1 of window 1
    end tell
    end tell
on error
    tell application "海通e海通财" to quit
    delay 1
    set res to "button 确定"
end try'"""


# 锁屏
eTongLockCmd = """/usr/bin/osascript -e 'tell application "System Events"
    tell process "e海通财"
        tell process "e海通财" to activate
        try
            click button "锁屏" of splitter group 1 of window 1
            set res to "successed"
        on error
            set res to "failed"
        end try
    end tell
    end tell'"""


# 解锁----暂时不知道锁屏后怎么解锁操作，待定
eTongUnLockCmd = """/usr/bin/osascript -e '
on windowName() --获取窗口名称
    tell application "System Events"
        set frontAppProcess to process "e海通财"
        --set frontAppProcess to first application process whose frontmost is true
    end tell
    
    tell frontAppProcess
        if (count of windows) > 0 then
            set window_name to name of every window
        end if
    end tell
end windowName


on unLockeTong(name, unlockePwd)
    tell application "System Events"
        tell process "e海通财"
            tell process "e海通财" to activate
            delay 1
            keystroke unlockePwd  --输入解锁密码
       
            click button "确定" of window name --of application process "e海通财" of application "System Events"
        end tell
    end tell
end unLockeTong


on run {userid, unlockePwd}
    try
        set parm to windowName() as string
        unLockeTong(parm, unlockePwd)
        set res to "successed"
    on error
        set res to "failed"
    end try
end run
'"""


# 获取资金信息
getAssetInfoCmd = """/usr/bin/osascript -e 'tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 118 --查询[F4]->资金股份

            delay 1.5

            key code 96 --刷新[F5]网络数据更新

            delay 1.5

            tell group 1 of group 1 of splitter group 1 of window 1
                set accountInfo to entire contents -- 获取所有 UI 元素
                return {"successed", accountInfo}
            end tell
        on error
            return {"failed", "unknown err"}
        end try
    end tell
    end tell'"""


#获取下单委托信息
getEntrustMentInfo ="""/usr/bin/osascript -e '
tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 97 --双向委托[F6]
            delay 1

            key code 96 --刷新[F5]网络数据更新
            delay 1

            tell group 1 of group 1 of group 3 of splitter group 1 of splitter group 1 of group 1 of splitter group 1 of window 1
                set entrustInfo to entire contents -- 获取所有 UI 元素
                return {"successed", entrustInfo}
            end tell
        on error
            return {"failed", "unknown err"}
        end try
    end tell
end tell'"""


# 卖出证券
sellAStockCmd = """/usr/bin/osascript -e 'on run {stockcode, price, amount, mode}
    tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 97 --双向委托[F6]
            delay 1

            key code 120 --卖出证券[F2]
            delay 1

            --取消买卖代码联动
            set theCheckbox1 to checkbox "买卖代码联动" of splitter group 1 of group 1 of splitter group 1 of window 1
            tell theCheckbox1
                set checkboxStatus to value of theCheckbox1 as boolean
                if checkboxStatus is true then click theCheckbox1
            end tell

            --取消委托后不清空
            set theCheckbox2 to checkbox "委托后不清空" of splitter group 1 of group 1 of splitter group 1 of window 1
            tell theCheckbox2
                set checkboxStatus to value of theCheckbox2 as boolean
                if checkboxStatus is true then click theCheckbox2
            end tell

            key code 96 --刷新[F5]网络数据更新
            delay 1

            --重置清空输入框内容
            click button "重置" of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1

            --传入的参数格式转换
            set price to price as number
            set amount to amount as number
            set mode to mode as number

            --选中证券代码的输入框
            set StaticText to text field "卖出证券[F2]" of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
            set {x, y} to position of StaticText
            do shell script "/usr/local/bin/cliclick c:" & x & "," & y

            keystroke stockcode --输入证券代码
            delay 0.5

            --判断下单方式mode，以决定委托类型
            if mode = 1 then --最优五档成交剩余撤销【沪户】/对方最优价格【深户】

                click pop up button "限价委托" of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode1Select to static text 2 of list 1 of window 1
                set {x, y} to position of Mode1Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                --选中卖出数量的输入框
                set StaticText to incrementor 1 of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入卖出数量

            else if mode = 2 then --最优五档成交剩余转限价【沪户】/本方最优价格【深户】

                click pop up button "限价委托" of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode2Select to static text 3 of list 1 of window 1
                
                set {x, y} to position of Mode2Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中卖出数量的输入框
                set StaticText to incrementor 1 of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入卖出数量

            else if mode = 3 then --即时成交剩撤【深户】

                click pop up button "限价委托" of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode3Select to static text 4 of list 1 of window 1
                
                set {x, y} to position of Mode3Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中卖出数量的输入框
                set StaticText to incrementor 1 of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入卖出数量

            else if mode = 4 then --最优五档成交剩余撤销【深户】

                click pop up button "限价委托" of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode4Select to static text 5 of list 1 of window 1
                
                set {x, y} to position of Mode4Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中卖出数量的输入框
                set StaticText to incrementor 1 of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入卖出数量

            else if mode = 5 then --全成交或撤销【深户】

                click pop up button "限价委托" of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode5Select to static text 6 of list 1 of window 1
                
                set {x, y} to position of Mode5Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中卖出数量的输入框
                set StaticText to incrementor 1 of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入卖出数量

            else  --限价委托

                --选中卖价输入框
                set StaticText to incrementor 1 of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke price --输入卖价
                delay 0.5

                 --选中卖出数量的输入框
                set StaticText to incrementor 2 of group "卖出证券[F2]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入卖出数量

            end if

            --点击卖出[S]
            key code 1 --卖出(S)
            delay 0.5

            --确认卖出并委托下单
            click button "确认" of window "卖出交易确认"
            delay 1

            --进一步确认委托单号
            click button "确定" of group 1 of window 1
            delay 1

            return "successed"
        on error
            return "failed"
        end try

    end tell
    end tell
    end run'"""


# 买入证券
buyAStockCmd = """/usr/bin/osascript -e 'on run {stockcode, price, amount, mode}
    tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 97 --双向委托[F6]
            delay 1

            key code 122 --买入证券[F1] 
            delay 1

            --取消买卖代码联动
            set theCheckbox1 to checkbox "买卖代码联动" of splitter group 1 of group 1 of splitter group 1 of window 1
            tell theCheckbox1
                set checkboxStatus to value of theCheckbox1 as boolean
                if checkboxStatus is true then click theCheckbox1
            end tell

            --取消委托后不清空
            set theCheckbox2 to checkbox "委托后不清空" of splitter group 1 of group 1 of splitter group 1 of window 1
            tell theCheckbox2
                set checkboxStatus to value of theCheckbox2 as boolean
                if checkboxStatus is true then click theCheckbox2
            end tell

            key code 96 --刷新[F5]网络数据更新
            delay 1

            --重置清空输入框内容
            click button "重置" of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1

            --传入的参数格式转换
            set price to price as number
            set amount to amount as number
            set mode to mode as number

            --选中证券代码的输入框
            set StaticText to text field "买入证券[F1]" of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
            set {x, y} to position of StaticText
            do shell script "/usr/local/bin/cliclick c:" & x & "," & y

            keystroke stockcode --输入证券代码
            delay 0.5

            --判断下单方式mode，以决定委托类型
            if mode = 1 then --最优五档成交剩余撤销【沪户】/对方最优价格【深户】

                click pop up button "限价委托" of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode1Select to static text 2 of list 1 of window 1

                set {x, y} to position of Mode1Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                --选中买入数量的输入框
                set StaticText to incrementor 1 of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入买入数量

            else if mode = 2 then --最优五档成交剩余转限价【沪户】/本方最优价格【深户】

                click pop up button "限价委托" of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode2Select to static text 3 of list 1 of window 1

                set {x, y} to position of Mode2Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中买入数量的输入框
                set StaticText to incrementor 1 of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入买入数量

            else if mode = 3 then --即时成交剩撤【深户】

                click pop up button "限价委托" of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode3Select to static text 4 of list 1 of window 1

                set {x, y} to position of Mode3Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中买入数量的输入框
                set StaticText to incrementor 1 of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入买入数量

            else if mode = 4 then --最优五档成交剩余撤销【深户】

                click pop up button "限价委托" of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode4Select to static text 5 of list 1 of window 1

                set {x, y} to position of Mode4Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中买入数量的输入框
                set StaticText to incrementor 1 of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入买入数量

            else if mode = 5 then --全成交或撤销【深户】

                click pop up button "限价委托" of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1

                delay 0.5

                set Mode5Select to static text 6 of list 1 of window 1

                set {x, y} to position of Mode5Select
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                delay 0.5

                --选中买入数量的输入框
                set StaticText to incrementor 1 of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入买入数量                       

            else  --限价委托

                --选中买价输入框
                set StaticText to incrementor 1 of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke price --输入买价
                delay 0.5

                --选中买入数量的输入框
                set StaticText to incrementor 2 of group "买入证券[F1]" of splitter group 1 of group 1 of splitter group 1 of window 1
                set {x, y} to position of StaticText
                do shell script "/usr/local/bin/cliclick c:" & x & "," & y

                keystroke amount --输入买入数量

            end if

            --点击买入按钮
            key code 11 --买入[B]
            delay 0.5

            --确认买入并委托下单
            click button "确认" of window "买入交易确认"
            delay 1

            --进一步确认委托单号
            click button "确定" of group 1 of window 1

            return "successed"
        on error
            return "failed"
        end try
    end tell
    end tell
    end run'"""


# 获取'买入[F1]'持仓信息
getKeepPositionOnBuyF1Cmd = """/usr/bin/osascript -e 'tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 122 --买入[F1]
            delay 1

            key code 13 --持仓(W)
            delay 1

            key code 96 --刷新[F5]网络数据更新
            delay 1

            tell group 1 of group 1 of splitter group 1 of group 1 of splitter group 1 of window 1
                set positionInfo to entire contents -- 获取所有 UI 元素
                return {"successed", positionInfo}
            end tell
        on error
            return {"failed", "unknown err"}
        end try

    end tell
    end tell
    '"""


# 获取'查询F4'->'资金股份'模块的持仓信息
getKeepPositionOnAssetModelCmd = """/usr/bin/osascript -e 'tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 118 --查询[F4]->资金股份
            delay 1

            key code 96 --刷新[F5]网络数据更新
            delay 1

            tell group 3 of group 1 of splitter group 1 of window 1
                set positionInfo to entire contents -- 获取所有 UI 元素
                return {"successed", positionInfo}
            end tell
        on error
            return {"failed", "unknown err"}
        end try

    end tell
    end tell'"""


# 把所有未成交的委托卖单撤掉--撤卖(C)
cancelAllSellStocksCmd = """/usr/bin/osascript -e 'tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 99 --撤单[F3]
            delay 1

            key code 8 --撤卖(C)
            delay 1

            --确认撤单
            click button "确定" of group 1 of window 1
            delay 1

            --确认撤单完毕
            click button "确定" of window "提示"
            return "successed"
        on error
            return "failed"
        end try
    end tell
    end tell'"""


# 把所有未成交的委托单撤掉--全撤(Z)
cancelAllStocksCmd = """/usr/bin/osascript -e 'tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 99 --撤单[F3]
            delay 1

            key code 6 --全撤(Z)
            delay 1

            --确认撤单
            click button "确定" of group 1 of window 1
            delay 1

            --确认撤单完毕
            click button "确定" of window "提示"

            return "successed"
        on error
            return "failed"
        end try
    end tell
    end tell'"""


# 把所有未成交的委托买单撤掉--撤买(X)
cancelAllBuyStocksCmd = """/usr/bin/osascript -e 'tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            key code 99 --撤单[F3]
            delay 1

            key code 6 --撤买(X)
            delay 1

            --确认撤单
            click button "确定" of group 1 of window 1
            delay 1

            --确认撤单完毕
            click button "确定" of window "提示"

            return "successed"
        on error
            return "failed"
        end try
    end tell
    end tell'"""


# 一键新股申购
oneKeyIPOCmd = """/usr/bin/osascript -e 'tell application "System Events"
    --进程"e海通财"进行激活
    set frontmost of process "e海通财" to true
    tell process "e海通财"
        try
            --展开侧边栏的"一键打新"
            set NameGroup to group "一键打新" of group 1 of group 2 of splitter group 1 of window 1
            set {x, y} to position of NameGroup
            do shell script "/usr/local/bin/cliclick c:" & x & "," & y
            delay 3

            --展开侧边栏的"新股申购"
            set NameGroup to group "新股申购" of group 1 of group 2 of splitter group 1 of window 1
            set {x, y} to position of NameGroup
            do shell script "/usr/local/bin/cliclick c:" & x & "," & y
            delay 3

            --展开侧边栏的"今日申购"
            set NameGroup to group "今日申购" of group 1 of group 2 of splitter group 1 of window 1
            set {x, y} to position of NameGroup
            do shell script "/usr/local/bin/cliclick c:" & x & "," & y
            delay 3

            --应急处理弹窗提示
            try
                click button "确定" of group 1 of window 1
                delay 1
            end try

            --点击“一键打新”按钮
            try
                click button "批量申购" of group 1 of splitter group 1 of window 1
                delay 2
            end try

            --确认打新完毕
            click button "确定" of group 1 of window 1
            delay 2

            --提示确认
            click button "确定" of window "提示"
            delay 2

            --折叠侧边栏的"新股申购"下的"今日申购"
            set NameGroup to group "新股申购" of group 1 of group 2 of splitter group 1 of window 1
            set {x, y} to position of NameGroup
            do shell script "/usr/local/bin/cliclick c:" & x & "," & y
            delay 2

            --展开侧边栏的"一键打新"下的"新股申购"
            set NameGroup to group "一键打新" of group 1 of group 2 of splitter group 1 of window 1
            set {x, y} to position of NameGroup
            do shell script "/usr/local/bin/cliclick c:" & x & "," & y
            delay 2

            return "successed"
        on error
            return "failed"
        end try
    end tell
    end tell'"""

