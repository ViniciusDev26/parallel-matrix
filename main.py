import socket
import multiprocessing
import threading
import sys

# ======================= Matrix File Reader ==========================
def load_and_validate_matrices(filename='matrix.txt'):
    with open(filename, 'r') as f:
        content = f.read().strip()

    parts = content.split('\n\n')

    if len(parts) != 2:
        raise ValueError("Matrix file must contain two matrices separated by two blank lines.")

    matrix1 = [[int(num) for num in line.split()] for line in parts[0].strip().split('\n')]
    matrix2 = [[int(num) for num in line.split()] for line in parts[1].strip().split('\n')]

    valid1, msg1 = validate_matrix(matrix1)
    if not valid1:
        raise ValueError(f"First matrix invalid: {msg1}")

    valid2, msg2 = validate_matrix(matrix2)
    if not valid2:
        raise ValueError(f"Second matrix invalid: {msg2}")

    return matrix1, matrix2

# ======================= Socket Server ==========================
def multiplication_server(host='localhost', port=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}...")
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(4096).decode() # Buffer size 4096 bytes (4MB)
                if not data:
                    continue
                # Data format: "Row;Column"
                # Example: "1,2,3;7,8,9"
                line_str, col_str = data.split(';')
                line = list(map(int, line_str.split(',')))
                col = list(map(int, col_str.split(',')))

                # Calculate dot product
                result = sum(l * c for l, c in zip(line, col))

                print(f"[Server {port}] Processing dot product: {line} · {col} = {result}")

                conn.sendall(str(result).encode())

# ======================= Socket Client ==========================
def send_operation(line, col, host='localhost', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        message = ','.join(map(str, line)) + ';' + ','.join(map(str, col))
        s.sendall(message.encode())
        result = s.recv(1024).decode()
    return int(result)

# ======================= Multiprocessing Worker ==========================
def compute_element(i, j, matrix1, matrix2, servers, result):
    line = matrix1[i]
    col = [matrix2[k][j] for k in range(len(matrix2))]
    server = servers[(i + j) % len(servers)]
    res = send_operation(line, col, *server)
    print(f"Computed element [{i}][{j}] = {res} by server {server}")
    result[i][j] = res

# ======================= Matrix Multiplication ==========================
def multiply_matrices(matrix1, matrix2, servers):
    rows = len(matrix1)
    cols = len(matrix2[0])
    manager = multiprocessing.Manager()
    result = manager.list([manager.list([0 for _ in range(cols)]) for _ in range(rows)])

    processes = []

    for i in range(rows):
        for j in range(cols):
            p = multiprocessing.Process(
                target=compute_element,
                args=(i, j, matrix1, matrix2, servers, result)
            )
            processes.append(p)
            p.start()

    for p in processes:
        p.join()

    return [list(row) for row in result]

# ======================= Export Result ==========================
def export_result_pretty(matrix, filename='result.txt'):
    # Discovery the largest number to define the column width
    max_num = max(max(row) for row in matrix)
    width = len(str(max_num)) + 2  # extra space for margin
    
    with open(filename, 'w') as f:
        for row in matrix:
            line = ''.join(f"{num:>{width}}" for num in row)
            f.write(line + '\n')

# ======================= Matrix Validation ==========================
def validate_matrix(matrix):
    if not matrix:
        return False, "Matrix is empty."

    row_length = len(matrix[0])

    for row in matrix:
        if len(row) != row_length:
            return False, "All rows must have the same number of columns."
        for elem in row:
            if not isinstance(elem, int):
                return False, f"Invalid element '{elem}', must be integer."

    return True, "Matrix is valid."



# ======================= Main Execution ==========================
if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == 'server':
        # Example: python main.py server 8000
        port = int(sys.argv[2]) if len(sys.argv) >= 3 else 8000
        multiplication_server(port=port)

    else:
        # Client mode: matrix multiplication
        matrix1, matrix2 = load_and_validate_matrices('matrix-1.txt')

        # List of servers: (host, port)
        servers = [('localhost', 8000), ('localhost', 8001), ('localhost', 8002)]

        # Parallel multiplication using servers
        result_parallel = multiply_matrices(matrix1, matrix2, servers)
        export_result_pretty(result_parallel, 'result_parallel.txt')
        print("Parallel result exported to result_parallel.txt")

