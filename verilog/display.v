module display(
        input i_clk_sys,
        input i_rst_n,
        input i_uart_rx,
        output reg [15:0] o_data_col,
        output reg [3:0] o_curr_col,
        output o_ld_parity
    );
    localparam DATA_WIDTH = 8;
    localparam BAUD_RATE = 115200;
    localparam PARITY_ON = 1;
    localparam PARITY_TYPE = 1;

    wire w_rx_done;
    wire ld_parity;
    wire rst_n;
    wire [DATA_WIDTH-1 : 0] w_data;
    reg [DATA_WIDTH-1:0] w_data_matrix [0:256/DATA_WIDTH-1];
    assign o_ld_parity = ld_parity;

    // 2Khz分频模块
    reg clk_2K = 1'b0;
    reg [15:0] clk_2K_count = 16'd0;
    always @(negedge i_clk_sys) begin
        if (clk_2K_count<16'd12500)
            clk_2K_count <= clk_2K_count+1;
        else begin
            clk_2K_count <= 16'b0;
            clk_2K <= ~clk_2K;
        end
    end

    debouncing u_debouncing(
                   .clk_sys(i_clk_sys),
                   .key_b(i_uart_rx),
                   .key(rst_n)
               );

    uart_rx #(
                .CLK_FRE     	(50),
                .DATA_WIDTH  	(DATA_WIDTH),
                .PARITY_ON   	(PARITY_ON),
                .PARITY_TYPE 	(PARITY_TYPE),
                .BAUD_RATE   	(BAUD_RATE)
            ) u_uart_rx(
                .i_clk_sys   	(i_clk_sys),
                .i_rst_n     	(rst_n),
                .i_uart_rx   	(i_uart_rx),
                .o_uart_data 	(w_data),
                .o_ld_parity 	(ld_parity),
                .o_rx_done   	(w_rx_done)
            );

    reg [4:0] write_ptr = 0;
    integer i;
    always @(posedge i_clk_sys or negedge i_rst_n) begin
        if (!i_rst_n) begin
            write_ptr <= 0;
            for (i = 0; i < 32; i = i + 1)
                w_data_matrix[i] <= 8'b0;
        end
        else if (w_rx_done) begin
            w_data_matrix[write_ptr] <= w_data;
            if (write_ptr < 31)
                write_ptr <= write_ptr + 1;
            else
                write_ptr <= 0;
        end
    end

    always @(negedge clk_2K) begin
        if (o_curr_col < 4'b1111)
            o_curr_col <= o_curr_col + 1;
        else
            o_curr_col <= 0;
    end

    always @(*) begin
        o_data_col = {w_data_matrix[o_curr_col * 2], w_data_matrix[o_curr_col*2+1]};
    end

endmodule
