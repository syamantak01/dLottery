# DLottery

This is a decentralized lottery application in which anyone can enter and random winner is selected. This is full scale application based on smart contract development with solidity and brownie. A special feature of this lottery application is that only the owner/admin has exclusive permission to start and end the lottery

## Installation

1. Please install or have installed the following:
   - [nodejs and npm](https://nodejs.org/en/download/)
   - [python](https://www.python.org/downloads/)
2. [Install web3py]([Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html))
3. [Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html)
4. [Install ganache-cli](https://www.npmjs.com/package/ganache-cli)

## Setup

In the project folder run `brownie init` to setup the project. But by this method we have to manually add all the mocks and install dependencies and modify our config file accordingly and is quite some work.

Another way would be to use **chainlink-mix** and we will get all the dependencies preinstalled which provides with a boilerplate starting point for working on a project.

``` bash
brownie bake chainlink-mix
```

## Testnet Development

If you want to be able to deploy to testnets, do the following.

### With environment variables

Set the `WEB3_INFURA_PROJECT_ID`, and `PRIVATE_KEY` environment variables.

We can get a `WEB3_INFURA_PROJECT_ID` by getting a free trial of [Infura](https://infura.io/). At the moment, it does need to be infura with brownie.  You can find your `PRIVATE_KEY` from your Ethereum wallet like [metamask](https://metamask.io/).

We'll also need testnet rinkeby ETH and LINK. You can get LINK and ETH into your wallet by using the [rinkeby faucets located here](https://docs.chain.link/docs/link-token-contracts#rinkeby).

You can add your environment variables to the `.env` file:

```
export WEB3_INFURA_PROJECT_ID=<PROJECT_ID>
export PRIVATE_KEY=<PRIVATE_KEY>
```

AND THEN RUN `source .env` TO ACTIVATE THE ENV VARIABLES (You'll need to do this everytime you open a new terminal, or [learn how to set them easier](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html))

### Without environment variables

Add your account by doing the following:

```
brownie accounts new <some_name_you_decide>
```

We'll be prompted to add your private key, and a password. Then, in your code, you'll want to use `load` instead of add when getting an account.

```
account = accounts.load("some_name_you_decide")
```

Then we'll want to add your RPC_URL to the network of choice. For example:

```
brownie networks modify rinkeby host=https://your_url_here
```

Otherwise, we can build, test, and deploy on your local environment.

## Local Development

All the scripts are designed to work locally or on a testnet. We can add a development network ``` mainnet-fork ``` like this.

```
brownie networks add development mainnet-fork cmd=ganache-cli host=http://127.0.0.1 fork=<YOUR_ALCHEMY_PROJECT_KEY_HTTPS> accounts=10 mnemonic=brownie port=8545
```

## Project Outline

1) Users can enter the lottery with ETH based on a USD fee.
2) An admin will choose when the lottery is over. (This somewhat creates centralization but for the sake of project we can work with it)
3) The lottery will select a random winner.

## How I went on with the project

1) [**Lottery.sol**]() contract:
   - Add functions for **entering the lottery**, ***getting entrance fees***, ***starting the lottery***, ***finishing the lottery***.
   - Remember to add dependencies and compiler tag in ***brownie-config.yaml*** to use chainlink datafeeds in local environment.
   - Only the owner will be able to start and end the lottery and for that we used OpenZepplins's onlyOwner modifier.
   - We decided that the winner will be decided randomly. But generating random number in solidity is not that easy. Solidity contracts are deterministic. Anyone who figures out how your contract produces randomness can anticipate its results and use this information to exploit your application. [Read More](https://betterprogramming.pub/how-to-generate-truly-random-numbers-in-solidity-and-blockchain-9ced6472dbdf). So we used ***Chainlink VRF***.
   - After the winner is chosen, we reset the lottery.
2) [**helpful_scripts.py**]();
   - contains helpful functions variable needed for testing and development.
   - based on the network(local ganache or local forked or testnet), ***get_account()*** function fetches the appropriate account.
   - ***get_contract()*** function will grab the contract addresses from the brownie config if defined, otherwise, it will deploy a mock version of that contract, and return the mock contract.
   - We deploy 3 mocks: [MockAggregatorV3](https://github.com/smartcontractkit/chainlink-mix/blob/master/contracts/test/MockV3Aggregator.sol), [LinkToken mock](https://github.com/smartcontractkit/chainlink-mix/blob/master/contracts/test/LinkToken.sol), [VRF coordinator mock](https://github.com/smartcontractkit/chainlink-mix/blob/master/contracts/test/VRFCoordinatorMock.sol).
   - ***fund_LINK()*** will take *contract_address*, *account*, *link_token*, and *amount* as parameters and then fund the contract with the specified LINK.
3) [**deploy_lottery.py**]():
   - We start with deploying the lottery.
   - Then start the lottery
   - Then entering the lottery: We need to pass the *value* through the function which will give us the entrance fee.
   - Then we end the lottery: We need to fund the lottery with LINK which will be needed by chainlink-randomness function.  
   - And we declare the winner.
4) [**test_lottery_unit.py**]():
   - Design a ***unit test*** for testing in the *local development network*.
   - check if the **entrance fee** is correct.
   - make sure that **entry is denied** if the the **lottery is closed**.
   - make sure that player can **enter the lottery** once it is started.
   - make sure that the lottery can pick the correct winner. We use [Solidity Events](https://hackernoon.com/how-to-use-events-in-solidity-pe1735t5) for this particular function. (Modify the smart contract accordingly)

5. [**test_lottery_integration.py**]():
   - so unlike *unit testing* where we had to create a dummy of VRF coordinator and pretend to be a chainlink node in order to call callBackWithRandomness() function, *Integration testing* is done for a contract deployed on testnet, which is an actual network and not a mock network. So we are just going to wait for the chainlink node to respond.

## Final Conclusion

After testing on local development network and on a testnet like rinkeby. We can finally run scripts/deploy_lottery.py on a rinkeby testnet. Before doing that, make sure the metamask account linked has some LINK tokens and ETH. And after deploying it on a rinkeby testnet, its a good practice to observe and explore the *Transactions*, *Contract Information*, *Events* on the **Etherscan**.
