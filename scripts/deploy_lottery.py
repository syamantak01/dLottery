from brownie import Lottery, network, config
from scripts.helpful_scripts import get_account, get_contract, fund_LINK
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(
        "----------------------------------------------------------------------------------------------"
    )
    print("Lottery is deployed!")
    print(
        "----------------------------------------------------------------------------------------------"
    )
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    # wait for the last transaction to actually go through
    starting_tx.wait(1)
    print(
        "----------------------------------------------------------------------------------------------"
    )
    print("Lottery begins...")
    print(
        "----------------------------------------------------------------------------------------------"
    )


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = (
        lottery.getEntranceFee() + 100000000
    )  # 100000000 is some marginal wei added for threshold purpose
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print(
        "----------------------------------------------------------------------------------------------"
    )
    print("Welcome to the lottery!")
    print(
        "----------------------------------------------------------------------------------------------"
    )


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # in the endLottery function of Lottery.sol, we call requestRandomness() which will in turn require some LINK tokens
    # so we need to fund the contract with some LINK tokens
    tx = fund_LINK(lottery.address)
    tx.wait(1)
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)

    # requestRandomness() function of endLottery solidity function will make a request to a chainlink node and the
    # chainlink node will respond with the fulfillRandomness function so we have to wait for chainlink node to finish.
    # Typically, its within a few blocks, so we wait.
    time.sleep(180)
    print(f"Congratulations! {lottery.recentWinner()} is the winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
