from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
from scripts.helpful_scripts import (
    get_contract,
    get_account,
    fund_LINK,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
import pytest


def test_get_entrance_fee():

    # do this test only when it is in local development network, otherwise skip it
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()

    # some maths to explain the values
    # 2000 eth/usd price feed in mock development network--> INITIAL_VALUE in MockV3Aggregator
    # usdEntryFee is $50
    # 2000/1 == 50/x; x = 0.025

    # Act
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()

    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # do this test only when it is in local development network, otherwise skip it
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter():
    # do this test only when it is in local development network, otherwise skip it
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # do this test only when it is in local development network, otherwise skip it
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange

    ### deploy lottery
    lottery = deploy_lottery()
    account = get_account()
    ### start lottery
    lottery.startLottery({"from": account})
    ### Enter lottery
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    ### End lottery
    fund_LINK(lottery)
    lottery.endLottery({"from": account})

    # assert
    assert lottery.lottery_state() == 2  # CALCULATING_WINNER


def test_can_pick_winner_correctly():
    # do this test only when it is in local development network, otherwise skip it
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange

    ### deploy lottery
    lottery = deploy_lottery()
    account = get_account()
    ### start lottery
    lottery.startLottery({"from": account})
    ### Enter lottery
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})  # player 1
    lottery.enter(
        {"from": get_account(index=1), "value": lottery.getEntranceFee()}
    )  # player 2
    lottery.enter(
        {"from": get_account(index=2), "value": lottery.getEntranceFee()}
    )  # player 3

    ### fund the lottery
    fund_LINK(lottery)

    ### some accounting
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()

    ### end the lottery
    transaction = lottery.endLottery({"from": account})

    # we grab the request id of RequestedRandomness even in smart contract
    request_id = transaction.events["RequestedRandomness"]["requestId"]

    # some static random number
    STATIC_RANDOM_NO = 9999

    # so now with the help of requestId, we can pretend to be a chainlink node and call the callBackWithRandomness function
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RANDOM_NO, lottery.address, {"from": account}
    )

    # assert
    ### 9999%3 == 0, so player 1 is the winner i.e., account
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
