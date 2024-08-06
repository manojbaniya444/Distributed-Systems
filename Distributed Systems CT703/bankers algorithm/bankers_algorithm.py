def compute_need(need, maximum, allocated):
    """
    This computes the need matrix
    """
    # need = maximum - allocated
    for i in range(len(need)):
        for j in range(len(need[0])):
            need[i][j] = maximum[i][j] - allocated[i][j]
            
def is_system_safe(process, available, maximum, allocated):
    """
    This checks whether the system is in a safe state or not.
    
    parameters:
    process: vector array
    available: vector m
    max: n*m matrix
    allocated: n*m matrix
    """
    
    n = len(process)
    m = len(available)
    
    need = [[0] * m for _ in range(n)]
    finished = [False] * n
    safe_sequence = []
    
    compute_need(need, maximum, allocated)
    copy_available = available[:]
    
    count = 0
    
    while count < n:
        # run for the number of process time
        flag = False
        for i in range(n):
            if not finished[i]:
                newFlag = True
                
                for j in range(m):
                    if need[i][j] > copy_available[j]:
                        newFlag = False
                        break
                
                if(newFlag):
                    for k in range(m):
                        copy_available[k] += allocated[i][k]
                    safe_sequence.append(i)
                    
                    finished[i] = True
                    count += 1
                    flag = True
                    break
                
        if not flag:
            print("System is not in a safe state")
            return False
    
    print("System is in safe state.")
    print(safe_sequence)
    return True
        
if __name__ == "__main__":
    process = [0, 1, 2, 3, 4]
    
    maximum = [
        [7,5,3],
        [3,2,2],
        [9,0,2],
        [2,2,2],
        [4,3,3]
    ]
    
    allocated = [
        [0,1,0],
        [2,0,0],
        [3,0,2],
        [2,1,1],
        [0,0,2]
    ]
    
    available = [3,3,2]
    
    is_safe = is_system_safe(process, available, maximum, allocated)
    
   