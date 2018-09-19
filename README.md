# cash-rip
Implementation of cash rip for Bitcoin cash using multi signature addresses and the electroncash wallet.

Conceptually, this mimics a real-world interaction where the buyer rips a cash note in half and gives the merchant one half.
The two halves are useless, on their own, for both parties. After the buyer receives his item and he is happy, he can give his half to the 
merchant who then sticky-tapes the two halves together and can spend the money. A similar interaction is achieved via 
multi-signature addresses and Bitcoin Cash payments.

# Installation

Drag and drop cashRip.zip into Tools->Installed_Plugins manager in electron-cash version 3.3.1 and above.

# Usage

Short version: The buyer does Invite -> CheckAddress -> Send Funds -> Release in that order.

The merchant does AcceptInvite -> Send Goods -> RequestRelease in that order.

Long verson:

1. The buyer clicks **Invite**, which creates a contract in his app and gives him an **x_pubkey** which he shares with the merchant. He can now set a label to the contract to associate it with the merchant he is dealing with.
2. The merchant runs **AcceptInvite**, with the **x_pubkey** from the buyer as input. This generates his own contract and a bitcoincash multisig **address**. He shares this address plus his generated contract's x_pubkey with the buyer. He can also now set a label to the contract to associate it with the buyer he is dealing with.
3. The buyer then runs **CheckAddress**, giving as inputs three things: the **address** and **x_pubkey** sent to him by the merchant, as well as selecting his original **contract** that he created to invite the merchant. If this results in success, he can be sure that both he and the merchant generated the same multisig address that they both partially control. He can now **send the BCH** to the address, splitting control over the funds between him and the merchant.
4. When the merchant sees the funds have arrived (in a few seconds), he sends out the goods he is selling to the buyer. He now runs **RequestRelease** which requires two inputs: selecting the **contract** containing the funds in question, and entering a BCH **address** to which he would like the funds released into his control. He shares the resulting **hex code** with the buyer.

5. When the buyer receives the ordered item from the merchant and he is happy with it, he runs **Release**, which requires two inputs: the **hex code** he got from the merchant, and selecting the **contract** containing the funds in question.

