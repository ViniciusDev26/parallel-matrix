def multiply_matrices_serial(matrix1, matrix2):
    if not matrix1 or not matrix2:
        return None
        
    rows1 = len(matrix1)
    cols1 = len(matrix1[0])
    rows2 = len(matrix2) 
    cols2 = len(matrix2[0])


    # Initialize result matrix with zeros
    result = [[0 for _ in range(cols2)] for _ in range(rows1)]

    # Multiply matrices
    for i in range(rows1):
        for j in range(cols2):
            for k in range(cols1):
                result[i][j] += matrix1[i][k] * matrix2[k][j]

    return result

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

def export_result_pretty(matrix, filename='result.txt'):
    # Discovery the largest number to define the column width
    max_num = max(max(row) for row in matrix)
    width = len(str(max_num)) + 2  # extra space for margin
    
    with open(filename, 'w') as f:
        for row in matrix:
            line = ''.join(f"{num:>{width}}" for num in row)
            f.write(line + '\n')

if __name__ == "__main__":
    matrix1, matrix2 = load_and_validate_matrices('matrix-1.txt')

    # Serial multiplication (single process)
    result_serial = multiply_matrices_serial(matrix1, matrix2)
    export_result_pretty(result_serial, 'result_serial.txt') 
    print("\nSerial result exported to result_serial.txt")
  