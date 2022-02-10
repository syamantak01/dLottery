// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    //list of all players
    address payable[] public players;
    address payable public recentWinner;
    uint256 public randomness;
    uint256 public usdEntryFee;

    AggregatorV3Interface internal ethUsdPriceFeed;

    // enumerables are useful to model choice and keep track of state.
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    bytes32 internal keyHash; //we need keyhash to uniquely identify the chainlink VRF node
    uint256 internal fee; //fee is associated with the link token needed to pay for the request to chainlinkVRF

    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        //declaring entry fee as 50$ and 10**18 because we want to keep the units in wei
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        //We can only enter if somebody started the lottery
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Sorry the lottery isn't open yet!"
        );
        //minimum $50 to enter the lottery
        require(
            msg.value >= getEntranceFee(),
            "Sorry! Cannot enter lottery due to insufficient ETH."
        );
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        //convert int256 to uint256
        //Also ETH/USD conversion will have 8 decimals
        //To make it 18 decimals we multiply by 10**10
        uint256 adjustedPrice = uint256(price) * (10**10);
        //Since there is no support for decimals in Solidity, we need to make it in the powers of (10**18) to avoid decimals.
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    //only the Owner can start the lottery
    //using openzepplin Ownable-onlyOwner modifier
    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "There is an ongoing lottery already!"
        );
        //start the lottery
        lottery_state = LOTTERY_STATE.OPEN;
    }

    //only the owner can end the lottery
    function endLottery() public onlyOwner {
        /*naive way to generate random number
        uint256(
            keccak256(
                abi.encodePacked(
                    nonce,
                    msg.sender,
                    block.difficulty,
                    block.timestamp
                )
            )
        )%players.length;
        */
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;

        /*
        The chainlink random number generator is based on request-response mechanism
        requestRandomness initiates a request for VRF output given _seed
        The fulfillRandomness method receives the output, once it is provided by the Oracle, and verified by the vrfCoordinator 
        */

        //Request Random Number
        bytes32 requestId = requestRandomness(keyHash, fee);
        //emit the RequestRandomness event
        emit RequestedRandomness(requestId);
    }

    //fulfillRandomness handles the VRF response
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        //need to check the state of the lottery
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Not there yet"
        );
        require(_randomness > 0, "Random not found");

        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);

        //Reset the lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        //so that we can keep tract of random numbers
        randomness = _randomness;
    }
}
