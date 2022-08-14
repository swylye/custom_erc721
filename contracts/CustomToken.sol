// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "./ERC721C.sol";

contract CustomToken is ERC721C {
    uint256 mintPrice;

    constructor(uint256 _mintPrice) ERC721C("Custom Token", "CT") {
        mintPrice = _mintPrice;
    }

    function safeMint(uint256 _amount) external payable {
        require(msg.value == _amount * mintPrice, "INCORRECT_FUND_AMOUNT");
        _safeMint(msg.sender, _amount);
    }

    function mint(uint256 _amount) external payable {
        require(msg.value == _amount * mintPrice, "INCORRECT_FUND_AMOUNT");
        _mint(msg.sender, _amount);
    }

    function burn(uint256 _tokenId) external {
        require(msg.sender == ownerOf(_tokenId));
        _burn(_tokenId);
    }

    function withdrawFunds() external onlyOwner {
        (bool sent, ) = msg.sender.call{value: address(this).balance}("");
        require(sent, "Failed to send Ether");
    }

    // Function to receive Ether. msg.data must be empty
    receive() external payable {}

    // Fallback function is called when msg.data is not empty
    fallback() external payable {}
}
