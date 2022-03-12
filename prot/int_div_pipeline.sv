/*
attempt to use pipeline for int_div
*/

parameter bitwidth = 32;

module int_div_pipeline(input clk, input rst, output reg ack, input [bitwidth - 1:0] a, input [bitwidth - 1:0] b, output reg [bitwidth - 1:0] quotient, output reg [bitwidth - 1:0] remainder);
    reg [bitwidth - 1:0] result1[bitwidth];
    reg [bitwidth - 1:0] result2[bitwidth];

    reg [bitwidth - 1: 0] a_;
    reg [2 * bitwidth - 1: 0] shiftedb;

    reg [5:0] pos;
    reg run;

    always @(posedge clk, posedge rst) begin
        if(rst) begin
            pos <= bitwidth - 1;
            quotient <= '0;
            a_ <= a;
            run <= 1;
            ack <= 0;
        end else if(run) begin
            if (shiftedb < a_) begin
                a_ <= a_ - shiftedb;
                quotient[pos] <= 1;
            end
            if (pos == 0) begin
                ack <= 1;
                run <= 0;
            end else begin
                pos <= pos - 1;
            end
        end else begin
            ack <= 0;
        end
    end

    assign shiftedb = b << pos;
    assign remainder = a_;
endmodule