from brownie import network
import pytest
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_LINK,
)
from scripts.deploy_lottery import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_LINK(lottery)
    lottery.endLottery({"from": account})

    # so unlike unittest where we had to create a dummy of VRF coordinator and pretend to be a chainlink node in order to call callBackWithRandomness() function
    # integration testing is done for a contract deployed on testnet, which is an actual network and not a mock network. So we are just going
    # to wait for the chainlink node to respond
 
    time.sleep(180)

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
