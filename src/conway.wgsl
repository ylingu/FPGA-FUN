@group(0) @binding(0) var<storage, read> currentCells: array<f32>;
@group(0) @binding(1) var<storage, read_write> nextCells: array<f32>;
@group(0) @binding(2) var<uniform> dims: vec2<u32>;

fn getCellValue(x: i32, y: i32) -> f32 {
    let width = i32(dims.x);
    let height = i32(dims.y);
    let col = (x + width) % width;
    let row = (y + height) % height;
    return currentCells[u32(col * height + row)];
}

@compute @workgroup_size(16, 16)
fn main(@builtin(global_invocation_id) id : vec3<u32>) {
    let x = i32(id.x);
    let y = i32(id.y);
    let width = i32(dims.x);
    let height = i32(dims.y);
    if (x >= width || y >= height) {
    return;
    }

    // 计算周围邻居
    var sum = 0.0;
    for (var i = -1; i <= 1; i = i + 1) {
    for (var j = -1; j <= 1; j = j + 1) {
        sum = sum + getCellValue(x + i, y + j);
    }
    }
    sum = sum - getCellValue(x, y);

    let currentState = getCellValue(x, y);
    var newState = 0.0;

    if (currentState == 1.0) {
    if (sum < 2.0 || sum > 3.0) {
        newState = 0.0;
    } else {
        newState = 1.0;
    }
    } else {
    if (sum == 3.0) {
        newState = 1.0;
    }
    }
    let index = x * height + y;
    nextCells[u32(index)] = newState;
}