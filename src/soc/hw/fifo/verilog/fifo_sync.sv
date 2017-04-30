// synchronous non-FWFT FIFO
// optimized for Xilinx Vivado Synthesis, following "RAM HDL Coding Guidelines" 
// in UG901
module fifo_sync #(
   parameter WIDTH = 8,
   parameter DEPTH = 32,
   parameter PROG_FULL = DEPTH / 2
)(
   input                 clk,
   input                 rst,

   input [(WIDTH-1):0]   din,
   input                 wr_en,
   output                full,
   output                prog_full,

   output reg [(WIDTH-1):0]  dout,  
   input                 rd_en,
   output                empty
   // XXX: add output prog_empty   
);
   
   localparam AW = $clog2(DEPTH); //rd_count width
   
   reg [AW-1:0]        wr_addr;
   reg [AW-1:0]        rd_addr;
   wire         fifo_read;
   wire         fifo_write;
   reg [AW-1:0] rd_count;
      
   // generate control signals
   assign empty       = (rd_count[AW-1:0] == 0);   
   assign prog_full   = (rd_count[AW-1:0] >= PROG_FULL);   
   assign full        = (rd_count[AW-1:0] == (DEPTH-1));
   assign fifo_read   = rd_en & ~empty;
   assign fifo_write  = wr_en & ~full;

   // address logic
   always_ff @(posedge clk) begin 
      if (rst) begin      
         wr_addr[AW-1:0]   <= 'd0;
         rd_addr[AW-1:0]   <= 'b0;
         rd_count[AW-1:0]  <= 'b0;
      end else begin 
         if (fifo_write & fifo_read) begin
            wr_addr[AW-1:0] <= wr_addr[AW-1:0] + 'd1;
            rd_addr[AW-1:0] <= rd_addr[AW-1:0] + 'd1;        
         end else if (fifo_write) begin
            wr_addr[AW-1:0] <= wr_addr[AW-1:0]  + 'd1;
            rd_count[AW-1:0]<= rd_count[AW-1:0] + 'd1; 
         end else if (fifo_read) begin         
            rd_addr[AW-1:0] <= rd_addr[AW-1:0]  + 'd1;
            rd_count[AW-1:0]<= rd_count[AW-1:0] - 'd1;
         end
      end
   end
   
   // generic dual-port, single clock memory
   reg [WIDTH-1:0] ram [DEPTH-1:0];

   // write
   always_ff @(posedge clk) begin 
      if (fifo_write) begin
         ram[wr_addr] <= din;
      end
   end
   
   // read
   always_ff @(posedge clk) begin 
      if (fifo_read) begin
         dout <= ram[rd_addr];
      end
   end   
endmodule
