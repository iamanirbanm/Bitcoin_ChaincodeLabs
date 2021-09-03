def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2

def setup_network(self):
        """This is the setting up of the network of nodes"""
        self.setup_nodes()
        #Note that no block has been generated yet. This one is only creating the network of nodes.
        self.connect_nodes(0, 1)
        self.sync_all(self.nodes[0:2])   
def run_test(self):
        """Main test logic"""

        # Create P2P connections will wait for a verack to make sure the connection is fully up
        peer_messaging = self.nodes[0].add_p2p_connection(BaseNode())

        # Generating a block on one of the nodes will get us out of IBD[mining of the initial block,genesis block]
        blocks = [int(self.nodes[0].generate(nblocks=1)[0], 16)]
        self.sync_all(self.nodes[0:2]) #The information has been synced with both the nodes

        self.log.info("Starting test!")
        #Beginning of mining of New block
        self.log.info("Create some blocks")
        self.tip = int(self.nodes[0].getbestblockhash(), 16)
        self.block_time = self.nodes[0].getblock(self.nodes[0].getbestblockhash())['time'] + 1

        height = self.nodes[0].getblockcount()
        #The following will mine a new block in node 1
        block = create_block(self.tip, create_coinbase(height+1), self.block_time)
        block.solve()
        block_message = msg_block(block)
        # Send message is used to send a P2P message to the node over our P2PInterface
        peer_messaging.send_message(block_message)
        self.tip = block.sha256
        blocks.append(self.tip)
        self.block_time += 1
        height += 1
        
        #The info that block has been mined at node 1 is sent to node 2
        self.log.info("Wait for node1 to reach current tip (height 2) using RPC")
        self.nodes[1].waitforblockheight(2)

        self.log.info("Connect node2 and node1")
        self.connect_nodes(1, 2)

        self.log.info("Wait for node2 to receive all the blocks from node1")
        self.sync_all()

        self.log.info("Add P2P connection to node2")
        self.nodes[0].disconnect_p2ps()

        

        peer_receiving = self.nodes[2].add_p2p_connection(BaseNode())

        self.log.info("Test that node2 propagates all the blocks to us")

        #checking that the node 2 has received the Mined block
        getdata_request = msg_getdata()
        for block in blocks:
            getdata_request.inv.append(CInv(MSG_BLOCK, block))
        peer_receiving.send_message(getdata_request)

        # wait_until() will loop until a predicate condition is met. Use it to test properties of the
        # P2PInterface objects.
        peer_receiving.wait_until(lambda: sorted(blocks) == sorted(list(peer_receiving.block_receive_map.keys())), timeout=5)
