# cash-rip
Implementation of cash rip for Bitcoin cash using multi signature addresses and the electroncash wallet.

Conceptually, this mimics a real-world interaction where the buyer rips a cash note in half and gives the merchant one half.
The two halves are useless, on their own, for both parties. After the buyer receives his item and he is happy, he can give his half to the 
merchant who then sticky-tapes the two halves together and can spend the money. A similar interaction is achieved via 
multi-signature addresses and Bitcoin Cash payments.

# Installation

Drag and drop cashRip.zip into Tools->Installed_Plugins manager in electron-cash version 3.3.1 and above.

# Usage

1. The buyer clicks Invite, which creates a contract in his app and gives him an x_pubkey which he shares with the merchant.
2. The merchant clicks AcceptInvite, with the x_pubkey from the buyer as argument. This generates his own contract and a bitcoincash multisig address. He shares this address plus his resulting x_pubkey with the buyer.
3. The buyer then clicks CheckAddress, using the address and x_pubkey from the merchant, as well as selecting his original contract that he created. If this results in success, he can now send the BCH to the address, splitting control over the funds between him and the merchant.
4. When the merchant sees the funds have arrived (a few seconds), he sends out the item he is selling to the buyer. He now clicks RequestRelease, selecting the relevant contract and also entering a BCH address to which he would like the funds released into his control. He shares the resulting hex code with the buyer.
5. When the buyer receives the ordered item from the merchant and he is happy with it, he clicks Release, giving as input the hex code he got from the merchant, as well as selecting the relevant contract.
