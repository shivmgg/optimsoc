"""
Test for single port SRAM (sram_sp)
"""
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure, ReturnValue

@cocotb.coroutine
def write_ram(dut, address, value):
    """
    Write data to the RAM
    """

    yield RisingEdge(dut.clk)
    dut.addr = address
    dut.din = value
    dut.we = 1
    yield RisingEdge(dut.clk)
    dut.we = 0

@cocotb.coroutine
def read_ram(dut, address):
    """
    Read data from the RAM and return its value
    """
    yield RisingEdge(dut.clk)

    dut.addr = address
    dut.oe = 1

    yield RisingEdge(dut.clk)
    yield RisingEdge(dut.clk)
    dut.oe = 0
    #yield ReadOnly()
    raise ReturnValue(int(dut.dout.value))


@cocotb.test()
def test_ram(dut):
    """
    Write random values into the RAM, read back its valus and check the output
    """
    RAM = {}

    # Read the parameters back from the DUT to set up our model
    data_width = dut.DW.value.integer # [bit]
    address_width = dut.AW.value.integer # [bit]
    mem_size = dut.MEM_SIZE.value.integer # [bytes]
    mem_size_words = dut.MEM_SIZE.value.integer / (data_width / 8) # [words]
    dut._log.info("Found RAM with %d words (%d bytes). Word width: %d bit" %
                  (mem_size_words, mem_size, data_width))

    cocotb.fork(Clock(dut.clk, 3200).start())

    # select chip enable
    dut.ce = 1

    # select all bytes
    dut.sel = 2**(data_width/8) - 1;

    # reset for two cycles
    dut._log.info("Resetting DUT")
    dut.rst = 1

    dut.we = 0
    dut.oe = 0
    for _ in xrange(2):
        yield RisingEdge(dut.clk)
    dut.rst = 0

    dut._log.info("Writing in random values")
    for i in xrange(mem_size_words):
        RAM[i] = int(random.getrandbits(data_width))
        yield write_ram(dut, i, RAM[i])

    dut._log.info("Reading back values and checking")
    for i in xrange(mem_size_words):
        value = yield read_ram(dut, i)
        if value != RAM[i]:
            dut._log.error("RAM[%d] expected %d but got %d" % (i, RAM[i], dut.dout.value.value))
            raise TestFailure("RAM contents incorrect")

    dut._log.info("RAM contents OK")
