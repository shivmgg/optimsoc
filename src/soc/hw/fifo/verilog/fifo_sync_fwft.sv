// synchronous FWFT FIFO
module fifo_sync_fwft #(
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

   reg                   fifo_valid, middle_valid, dout_valid;
   reg [(WIDTH-1):0]     middle_dout;

   wire [(WIDTH-1):0]    fifo_dout;
   wire                  fifo_empty, fifo_rd_en;
   wire                  will_update_middle, will_update_dout;

   // non-FWFT synchronous FIFO
   fifo_sync 
      u_fifo (
         .rst(rst),       
         .clk(clk),
         .rd_en(fifo_rd_en),
         .dout(fifo_dout),
         .empty(fifo_empty),
         .wr_en(wr_en),
         .din(din),
         .full(full),
         .prog_full(prog_full)
      );

   // create FWFT FIFO out of non-FWFT FIFO
   // public domain code from Eli Billauer
   // see http://www.billauer.co.il/reg_fifo.html
   assign will_update_middle = fifo_valid && (middle_valid == will_update_dout);
   assign will_update_dout = (middle_valid || fifo_valid) && (rd_en || !dout_valid);
   assign fifo_rd_en = (!fifo_empty) && !(middle_valid && dout_valid && fifo_valid);
   assign empty = !dout_valid;

   always_ff @(posedge clk) begin
      if (rst) begin
         fifo_valid <= 0;
         middle_valid <= 0;
         dout_valid <= 0;
         dout <= 0;
         middle_dout <= 0;
      end else begin
         if (will_update_middle)
            middle_dout <= fifo_dout;
            
         if (will_update_dout)
            dout <= middle_valid ? middle_dout : fifo_dout;
            
         if (fifo_rd_en)
            fifo_valid <= 1;
         else if (will_update_middle || will_update_dout)
            fifo_valid <= 0;
            
         if (will_update_middle)
            middle_valid <= 1;
         else if (will_update_dout)
            middle_valid <= 0;
            
         if (will_update_dout)
            dout_valid <= 1;
         else if (rd_en)
            dout_valid <= 0;
      end 
   end
 
endmodule
