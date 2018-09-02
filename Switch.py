# Project 2 for OMS6250
#
# This defines a Switch that can can send and receive spanning tree
# messages to converge on a final loop free forwarding topology.  This
# class is a child class (specialization) of the StpSwitch class.  To
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm -
# a non-distributed algorithm will not receive credit.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015


from Message import *
from StpSwitch import *

class Switch(StpSwitch):

    def __init__(self, idNum, topolink, neighbors):
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)

        #TODO: Define a data structure to keep track of which links are part of / not part of the spanning tree.
        self.switchID = idNum
        self.root = idNum
        self.distance = 0
        self.activeLinks = []
        self.switchThrough = idNum
        self.neighbors = neighbors
        # Store links
        # Store root
        # Store distance from root

    def doPrinting(self):
        # if self.switchID == 7:
            print("[Switch] SwitchID: %s Root: %s Distance: %s ActiveLinks: %s SwitchThrough: %s Neighbors: %s" %(self.switchID, self.root, self.distance, self.activeLinks, self.switchThrough, self.neighbors))

    def send_initial_messages(self):
        #TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
	#      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)
        for neighborID in self.neighbors:
            message = Message(self.root, self.distance, self.switchID, neighborID, False)
            Message.doPrinting(message)
            self.send_message(message)
        return

    def process_message(self, message):
        #TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.
        Message.doPrinting(message)
        Switch.doPrinting(self)
        if message.pathThrough == True:
            print("Got message pathThrough=True, adding to activeLinks")
            self.activeLinks.append(message.origin)
            Switch.doPrinting(self)
        elif message.pathThrough == False:
            if message.origin in self.activeLinks:
                print("Got message pathThrough=False, removing from activeLinks")
                self.activeLinks.remove(message.origin)
                if self.switchThrough == message.origin:
                    self.switchThrough = None
                # You can't just set it to none because it might not be the existing switchThrough. It might be a downstream node that no longer wants to be connected. In which case you just remove it from your active links.

                # self.switchThrough = None
                # if you're removing a link from the node you have to assign it another switchThrough but it's not
                # how do you do this
                # can you resend messages from all the other active links?

                Switch.doPrinting(self)
                # send message to the old link node
                message = Message(self.root, self.distance, self.switchID, message.origin, False)
                self.send_message(message)
            else:
                print("Need to do comparisons")
                if message.root < self.root:
                    print("Message root is less than my root")
                    # Message.doPrinting(message)
                    # Switch.doPrinting(self)
                    self.root = message.root
                    self.distance = message.distance + 1
                    self.activeLinks.append(message.origin)
                    self.switchThrough = message.origin
                    # Switch.doPrinting(self)
                    for neighborID in self.neighbors:
                        pathThrough = neighborID == self.switchThrough
                        message = Message(self.root, self.distance, self.switchID, neighborID, pathThrough)
                        self.send_message(message)
                elif message.root > self.root:
                    print("Message root is not less than my root")
                    # Message.doPrinting(message)
                    # Switch.doPrinting(self)
                else:
                    if message.distance + 1 < self.distance:
                        print("Message distance is less than my distance")
                        Message.doPrinting(message)
                        # Switch.doPrinting(self)
                        self.distance = message.distance + 1
                        self.activeLinks.append(message.origin)
                        self.switchThrough = message.origin
                        # Switch.doPrinting(self)
                        for neighborID in self.activeLinks:
                            pathThrough = neighborID == self.switchThrough
                            message = Message(self.root, self.distance, self.switchID, neighborID, pathThrough)
                            # Message.doPrinting(message)
                            self.send_message(message)
                    elif message.distance + 1 > self.distance:
                        print("Message distance is greater than my distance")
                    else:
                        if self.switchThrough is None:
                            print("SwitchThrough is None")
                            self.switchThrough = message.origin
                            self.activeLinks.append(self.switchThrough)
                            Switch.doPrinting(self)
                            message = Message(self.root, self.distance, self.switchID, self.switchThrough, True)
                            Message.doPrinting(message)
                            self.send_message(message)
                        elif message.origin < self.switchThrough:
                            print("Message origin is less than my switchThrough")
                            self.activeLinks.remove(self.switchThrough)
                            oldSwitchThrough = self.switchThrough
                            self.switchThrough = message.origin
                            self.activeLinks.append(self.switchThrough)
                            Switch.doPrinting(self)
                            messageToOldSwitchThrough = Message(self.root, self.distance, self.switchID, oldSwitchThrough, False)
                            messageToNewSwitchThrough = Message(self.root, self.distance, self.switchID, self.switchThrough, True)
                            Message.doPrinting(messageToOldSwitchThrough)
                            Message.doPrinting(messageToNewSwitchThrough)
                            self.send_message(messageToOldSwitchThrough)
                            self.send_message(messageToNewSwitchThrough)
                        elif message.origin > self.switchThrough:
                            print("Message origin is more than my switchThrough")
        return

    def generate_logstring(self):
        #TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked
        #      only after the simulaton is complete.  Output the links included in the
        #      spanning tree by increasing destination switch ID on a single line.
        #      Print links as '(source switch id) - (destination switch id)', separating links
        #      with a comma - ','.
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project skeleton.

        strings = []
        self.activeLinks.sort()
        for activeLink in self.activeLinks:
            strings.append("%s - %s" % (self.switchID, activeLink))
        return ", ".join(strings)
