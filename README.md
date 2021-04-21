# Welcome to etonger !

This is a repo for the [`etonger`](https://github.com/robinshare/etonger) trading engine under the Mac OSX system.

## Author
[`etonger`](https://github.com/robinshare/etonger) ©[RobinShare](https://github.com/robinshare), Released under the [GPL-3.0](./LICENSE) License.

## What's etonger support for?
[e海通财PC端Mac版](https://download.htsec.com/ChannelHome/4051009/4051213/index_2.shtml).

Details:

```
1、e海通财PC端Mac3.08版，支持Mac10.12以上版本。

2、支持科创板交易和新股申购业务。

3、支持普通交易、融资融券、贵金属三种交易类型。

5、支持多个基金品种交易，如场内基金、分级基金、ETF申赎、场外开放基金等业务功能。

6、支持新股一键申购，打新从此更方便。

7、增加沪深全景图，创业板注册制，全面支持IPv6。

8、支持在线客户服务，24小时在线为您解答。

```


## Repo structure
```
etonger/
    ├── LICENSE
    ├── pyproject.toml
    ├── README.md
    ├── setup.py  
    ├── src/
    │   └── etonger/
    │        ├── __init__.py
    │        ├── ascmd.py
    │        ├── ehelper.py             
    │        └── etonger.py
    └── tests/

tree ~/.config/etonger
    ~/.config/etonger
    └── config.xml
```

## Installation guide
1. Requirements
    - python >= 3.9.4

2. Dependencies

    ```bash
    brew install cliclick
    cliclick -V             # cliclick 4.0.1, 2018-04-10
    which cliclick          # /usr/local/bin/cliclick

    pip install pandas==1.2.4
    ```

3. Installation
   - Building `etonger` from pip
   
       ```bash
       pip install etonger
       ```

   - Building `etonger` from source
   
       ```bash
       git clone git@github.com:robinshare/etonger.git ~/etonger; cd ~/etonger; python setup.py install; rm -rf ~/etonger
       ```

4. Configuration

    ```bash
    mkdir -p ~/.config/etonger

    echo """
    <etonger>
        <trading>
            <userid>77777777777</userid>
            <password>123456</password>
            <broker_code>PAZQ</broker_code>
            <broker_account>66666666</broker_account>
            <broker_password>123456</broker_password>
            <bank_name>华夏银行</bank_name>
            <bank_account>666666666666666666</bank_account>
            <bank_password>123456</bank_password>
        </trading>
        <mail>
            <mail_host>smtp.163.com</mail_host>
            <mail_sender>mailAddress@163.com</mail_sender>
            <mail_license>SNRRQOKFKEUNNSFT</mail_license>
            <mail_receivers>mailAddress@163.com</mail_receivers>
        </mail>
    </etonger>
    """ > ~/.config/etonger/config.xml
    ```

## For more information
- Hint:
    - If you want to use the email notification module, you need to open a 163 email account.
    - Be Careful【手动要求】：
       - 客户端手动提前设置：双向委托[F6]---->>>>委托(R),勾选☑️可撤委托,同时向右拖动该窗口，让委托信息中全部列名可见。【注意：版式切换不要变更，使用原来的版式<上>】
