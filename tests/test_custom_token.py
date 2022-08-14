from brownie import OZToken, CustomToken, config, network, web3, exceptions
from scripts.helpful_scripts import get_account
from scripts.deploy import deploy_contracts
import pytest
import time

mint_price = 0.01e18


def test_can_mint():
    oz_token, c_token, acc = deploy_contracts()
    mint_quantity = 10
    c_token.mint(mint_quantity, {"from": acc, "value": mint_quantity * mint_price})
    assert c_token.totalSupply() == 10
    assert c_token.balanceOf(acc) == 10
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.mint(
            mint_quantity, {"from": acc, "value": (mint_quantity - 1) * mint_price}
        )
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.mint(
            mint_quantity, {"from": acc, "value": (mint_quantity + 1) * mint_price}
        )


def test_can_burn():
    oz_token, c_token, acc = deploy_contracts()
    acc2 = get_account(index=1)
    mint_quantity = 10
    c_token.mint(mint_quantity, {"from": acc, "value": mint_quantity * mint_price})
    c_token.mint(mint_quantity, {"from": acc2, "value": mint_quantity * mint_price})
    # cannot burn token that is not yours
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.burn(15, {"from": acc})
    # cannot burn token that doesn't exist
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.burn(50, {"from": acc})
    c_token.burn(5, {"from": acc})
    assert c_token.totalSupply() == 19
    assert c_token.balanceOf(acc) == 9
    # cannot burn token that is already burnt
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.burn(5, {"from": acc})


def test_can_approve():
    oz_token, c_token, acc = deploy_contracts()
    acc2 = get_account(index=1)
    acc3 = get_account(index=2)
    mint_quantity = 10
    token_id = 3
    c_token.mint(mint_quantity, {"from": acc, "value": mint_quantity * mint_price})
    # cannot approve token that is not yours
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.approve(acc2, token_id, {"from": acc3})
    c_token.approve(acc2, token_id, {"from": acc})
    assert c_token.getApproved(token_id) == acc2
    c_token.setApprovalForAll(acc3, True, {"from": acc})
    assert c_token.isApprovedForAll(acc, acc3) == True


def test_approver_transfer():
    oz_token, c_token, acc = deploy_contracts()
    acc2 = get_account(index=1)
    acc3 = get_account(index=2)
    mint_quantity = 10
    token_id = 3
    c_token.mint(mint_quantity, {"from": acc, "value": mint_quantity * mint_price})
    c_token.approve(acc2, token_id, {"from": acc})
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.transferFrom(acc, acc2, token_id + 1, {"from": acc2})
    c_token.transferFrom(acc, acc2, token_id, {"from": acc2})
    assert c_token.balanceOf(acc) == 9
    assert c_token.balanceOf(acc2) == 1
    assert c_token.ownerOf(token_id) == acc2
    assert c_token.getApproved(token_id) != acc2

    c_token.setApprovalForAll(acc3, True, {"from": acc})
    assert c_token.isApprovedForAll(acc, acc3) == True
    c_token.transferFrom(acc, acc3, token_id + 1, {"from": acc3})
    c_token.transferFrom(acc, acc3, token_id - 1, {"from": acc3})
    assert c_token.balanceOf(acc) == 7
    assert c_token.balanceOf(acc3) == 2
    assert c_token.ownerOf(token_id + 1) == acc3
    assert c_token.ownerOf(token_id - 1) == acc3


def test_can_transfer():
    oz_token, c_token, acc = deploy_contracts()
    acc2 = get_account(index=1)
    mint_quantity = 10
    token_id = 3
    c_token.mint(mint_quantity, {"from": acc, "value": mint_quantity * mint_price})
    # non owner / approver cannot transfer
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.transferFrom(acc, acc2, token_id, {"from": acc2})

    c_token.burn(token_id, {"from": acc})
    # burnt token cannot be transferred
    with pytest.raises(exceptions.VirtualMachineError):
        c_token.transferFrom(acc, acc2, token_id, {"from": acc})

    c_token.transferFrom(acc, acc2, token_id + 1, {"from": acc})
    assert c_token.balanceOf(acc) == 8
    assert c_token.balanceOf(acc2) == 1
    assert c_token.ownerOf(token_id + 1) == acc2
