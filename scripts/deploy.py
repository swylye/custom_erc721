from brownie import OZToken, CustomToken, config, network, web3
from scripts.helpful_scripts import get_account
import time

mint_price = 0.01e18


def main():
    oz_token, c_token, account = deploy_contracts()


def deploy_contracts():
    account = get_account()
    oz_token = OZToken.deploy(
        mint_price,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    c_token = CustomToken.deploy(
        mint_price,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    return oz_token, c_token, account
