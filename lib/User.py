# All logic related to direct interaction with the user
# Like asking the user for a password or voting on a proposal
# Import our own libraries
from lib import State, Contract


### Main logic for user handling


"""
@brief Print all user choices
"""
def printOptions(options):
    print("\nPlease choose an option:")
    for option in options:
        print(option)
    print()

"""
@brief Asks the user to give us a number
@return -1 on failure, else an integer
"""
def getInputAsInt():
    choice = input("Enter a number: ")
    
    try:
        choice = int(choice)
    except ValueError:
        print("Invalid input. Please enter a valid number.\n")
        choice = -1
    return choice

"""
@brief Asks the user for keystore passwords or choose from an option menu
"""
def handleUserInput():
    # Else continue to menu
    while True:
        options = [
            "1. Treasury proposals"
        ]
        if not State.LOCK_INTERACTIVE:
            options.append("0. Start siphoning. Press `CTRL + z`or `CTRL + \\` if you want to switch back to interactive mode")
        printOptions(options)
        choice = getInputAsInt()

        if choice == 0 and not State.LOCK_INTERACTIVE:
            print("Siphoning... 💸")
            State.require_user_input = False
            break
        else:
            if choice == 1:
                handleTreasury()
            else:
                print("UNIMPL: chose {0}".format(choice))
    

### Treasury proposals


"""
@brief Handler for voting on a proposal
"""
def handleVote(idx, proposalId):
    while True:
        print("{0} wants to vote".format(State.orchestrators[idx].source_address))
        options = ["3. Vote for the proposal", "2. Vote against the proposal", "1. Abstain", "0. Back to wallet selection"]
        printOptions(options)
        voteChoice = getInputAsInt()
        if voteChoice == 0:
            return
        else:
            if voteChoice < 4:
                reason = input("Type in a reason or leave empty to vote without reason: ")
                # Lastly ask them to confirm
                reasonString = State.orchestrators[idx].source_address + " is about to "
                if voteChoice == 1:
                    reasonString += "vote ABSTAIN this proposal "
                if voteChoice == 2:
                    reasonString += "vote AGAINST this proposal"
                if voteChoice == 3:
                    reasonString += "vote For this proposal"
                if reason == "":
                    reasonString += " without a reason"
                else:
                    reasonString += " with reason: '" + reason + "'"
                print(reasonString)
                # And cast the vote
                voteVal = -1 #< 0 = Against, 1 = For, 2 = Abstain
                if voteChoice == 3:
                    voteVal = 1
                if voteChoice == 2:
                    voteVal = 0
                if voteChoice == 1:
                    voteVal = 2
                if reason == "":
                    Contract.doCastVote(idx, proposalId, voteVal)
                else:
                    Contract.doCastVoteWithReason(idx, proposalId, voteVal, reason)
                return
            else:
                print("UNIMPL: chose {0}".format(voteChoice))

"""
@brief Handler for choosing a wallet to vote with
"""
def handleProposal(proposals, idx):
    proposal = proposals[idx]
    while True:
        # Refresh votes
        currentVotes = Contract.getVotes(proposal["proposalId"])
        sumVotes = currentVotes[0] + currentVotes[1] + currentVotes[2]
        amountAgainst = currentVotes[0]
        amountFor = currentVotes[1]
        amountAbstained = currentVotes[2]
        print("Currently {0:.0f} LPT ({1:.0f}%) is in favour, {2:.0f} LPT ({3:.0f}%) is in against, {4:.0f} LPT ({5:.0f}%) has abstained".format(
            amountFor, amountFor/sumVotes * 100, amountAgainst, amountAgainst/sumVotes * 100, amountAbstained, amountAbstained/sumVotes * 100
        ))
        # First build a list of eligible orchs
        canVoteIdx = []
        options = []
        for idx in range(len(State.orchestrators)):
            hasVoted = Contract.hasVoted(proposal["proposalId"], State.orchestrators[idx].source_checksum_address)
            if hasVoted:
                print("{0} has already voted on this proposal")
            else:
                print("{0} can vote on this proposal".format(State.orchestrators[idx].source_address))
                canVoteIdx.append(idx)
                options.append("{0}. Vote with {1}".format(idx + 1, State.orchestrators[idx].source_address))
        options.append("0. Back to proposals")
        # Ask which wallet to vote with
        printOptions(options)
        choice = getInputAsInt()
        if choice == 0:
            return
        else:
            if choice < len(canVoteIdx) + 1:
                handleVote(canVoteIdx[choice - 1], proposal["proposalId"])
            else:
                print("UNIMPL: chose {0}".format(choice))

"""
@brief Handler for choosing a treasury proposal
"""
def handleTreasury():
    proposals = Contract.getProposals()

    while True:
        options = []
        for idx, proposal in enumerate(proposals):
            options.append("{0}. {1}".format(idx + 1, proposal["title"]))
        options.append("0. Back to menu")
        printOptions(options)
        choice = getInputAsInt()

        if choice == 0:
            break
        else:
            if choice < len(proposals) + 1:
                handleProposal(proposals, choice - 1)
            else:
                print("UNIMPL: chose {0}".format(choice))


### Governance proposals


# TODO: get proposals
# TODO: get proposal status (open/closed, for/against/abstained)
# TODO: menu to select proposal
# TODO: menu to vote on proposal
# TODO: vote on proposal
# NOTE: tricky, seems to have a dedicated contract per proposal:
# https://arbiscan.io/tx/0x20a966e668ba6a2ec0ff74c1adb736484e506cc94f8279042e6d027218a26017
# https://arbiscan.io/tx/0x7f1b21412b01364b221090fea3d4d0b228aa0cd4a3d7745f2f53d59b4ed16f62
# https://arbiscan.io/tx/0x1f33cd73ee9b32b3c3423863c13166c4d69e2852117a9700d63624bdc02a1073

