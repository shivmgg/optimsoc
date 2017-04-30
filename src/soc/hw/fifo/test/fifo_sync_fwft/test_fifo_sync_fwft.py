"""
Test for single port SRAM (sram_sp)
"""
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly, Join, ClockCycles
from cocotb.result import TestFailure

TEST_MAX_RD_DELAY = 2
TEST_MAX_WR_DELAY = 2
TEST_ENTRIES_COUNT = 50

FIFO_TYPE = 'fwft'

# Mirroring expected contents of the FIFO
fifo_data = []

@cocotb.coroutine
def write_fifo(dut):
    fifo_wrcnt = 0
    while True:
        # insert random wait before the next write
        wr_delay = random.randint(0, TEST_MAX_WR_DELAY)
        dut._log.info("WRITE: Wait for %d clock cycles" % (wr_delay))
        for _ in range(wr_delay):
            yield RisingEdge(dut.clk)

        if dut.full.value:
            dut._log.info("WRITE: FIFO full, not writing")
        else:
            # generate and write random data, keep track of it for checking
            data = random.getrandbits(dut.WIDTH.value.integer)
            dut.din <= data
            fifo_data.append(data)
            
            dut.wr_en <= 1
            yield RisingEdge(dut.clk)
            dut.wr_en <= 0

            fifo_wrcnt += 1
            dut._log.info("WRITE: Wrote word %d to FIFO, value 0x%x" % (fifo_wrcnt, data))
            
        if fifo_wrcnt >= TEST_ENTRIES_COUNT:
            return

@cocotb.coroutine
def read_fifo(dut):
    fifo_rdcnt = 0
    while True:
        # insert random wait before the next read
        rd_delay = random.randint(0, TEST_MAX_RD_DELAY)
        dut._log.info("READ: Wait for %d clock cycles" % (rd_delay))
        for _ in range(rd_delay):
            yield RisingEdge(dut.clk)

        if dut.empty.value:
            dut._log.info("READ: FIFO empty, not reading")
        else:
            # send read request
            dut.rd_en <= 1
            fifo_rdcnt += 1

            yield RisingEdge(dut.clk)
            
            if FIFO_TYPE != 'fwft':

                # output is delayed by one cycle
                # lower read request signal
                dut.rd_en <= 0
                yield RisingEdge(dut.clk)
            else:
                yield ReadOnly()

            data_read = dut.dout.value.integer
            dut._log.info("READ: Got 0x%x in read %d" % (data_read, fifo_rdcnt))

            data_expected = fifo_data.pop(0)
            if data_read != data_expected:
                raise TestFailure("READ: Expected 0x%x, got 0x%x at read %d" %
                                  (data_expected, data_read, fifo_rdcnt))

            if FIFO_TYPE == 'fwft':
                # output is delayed by one cycle
                # lower read request signal
                dut.rd_en <= 0


        # done
        if fifo_rdcnt >= TEST_ENTRIES_COUNT:
            return



@cocotb.test()
def test_fifo_sync_fwft(dut):
    """
    Test the module fifo_sync_fwft, a synchronous first-word-fall-through FIFO
    """

    # Read the parameters back from the DUT to set up our model
    width = dut.WIDTH.value.integer  # [bit]
    depth = dut.DEPTH.value.integer  # [entries]
    dut._log.info("%d bit wide FIFO with %d entries." % (width, depth))

    cocotb.fork(Clock(dut.clk, 3200).start())

    # reset for two cycles
    dut._log.info("Resetting DUT")
    dut.rst <= 1

    dut.din <= 0
    dut.wr_en <= 0
    dut.rd_en <= 0

    yield ClockCycles(dut.clk, 2)
    dut.rst <= 0

    
    # start read and write processes
    write_thread = cocotb.fork(write_fifo(dut))
    read_thread = cocotb.fork(read_fifo(dut))

    # wait for all reads and writes to finish
    yield read_thread.join()

    yield(Timer(200))

    dut._log.info("All tests done")
