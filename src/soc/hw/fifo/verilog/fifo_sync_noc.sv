// synchronous FWFT FIFO with NoC naming (nothing else changed)
module fifo_sync_noc #(
   parameter WIDTH = 34,
   parameter DEPTH = 16
)(
   input clk,
   input rst,
   
   // FIFO input side
   input  [WIDTH-1:0] in_flit,   // input
   input  in_valid,                   // write_enable
   output in_ready,                   // accepting new data

   // FIFO output side
   output [WIDTH-1:0] out_flit,   // data_out
   output out_valid,                   // data available
   input  out_ready                   // read request
);
   
   
   wire [(WIDTH-1):0]   din;
   wire                 wr_en;
   wire                full;
   
   wire [(WIDTH-1):0]  dout;
   wire                 rd_en;
   wire                empty;
   
   // Synchronous FWFT FIFO
   fifo_sync_fwft 
      #(
         .WIDTH(WIDTH), 
         .DEPTH(DEPTH)
      )
      u_fifo (
         .clk(clk),
         .rst(rst),
         
         .din(din),
         .wr_en(wr_en),
         .full(full),
         .prog_full(), // unused
         
         .dout(dout),
         .rd_en(rd_en),
         .empty(empty)
      );

   // map wire names from NoC naming to normal FIFO naming
   assign din = in_flit;
   assign wr_en = in_valid;
   assign in_ready = ~full;

   assign out_flit = dout;
   assign out_valid = ~empty;
   assign rd_en = out_ready;
   
endmodule
