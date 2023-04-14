from ATM import ATM
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: %s self_port partner1_port partner2_port ...' % sys.argv[0])
        sys.exit(-1)

    port = int(sys.argv[1])
    partners = ['localhost:%d' % int(p) for p in sys.argv[2:]]
    o = ATM('localhost:%d' % port, partners)
    n = 0
    old_value = -1
    while True:
        output = -3
        if o._getLeader() is not None:
            print('Leader node - ', o._getLeader())
            print('Press 1 to Add New Account')
            print('Press 2 for Withdrawal')
            print('Press 3 for Deposit')
            print('Press 4 for Balance Enquiry')
            print('Press 5 for Money Transfer')
            print('Press 6 for exit.')

            inp = input('Enter your choice: ')
            inp = int(inp)

            if inp == 1:
                inp = input('Enter Account ID: ')
                output = o.add(inp)
            if inp == 2:
                inp = input('Enter Account ID: ')
                inp2 = input('Enter Amount: ')
                output = o.withdraw(inp, int(inp2))
            
            elif inp == 3:
                inp = input('Enter Account ID: ')
                inp2 = input('Enter Amount: ')
                output = o.deposit(inp, int(inp2))
            
            elif inp == 4:
                inp = input('Enter Account ID: ')
                output = o.balance(inp)
                if output > -1:
                    print("The balance is ", output, '\n')
            
            elif inp == 5:
                inp = input('Enter Sender Account ID: ')
                inp2 = input('Enter Receiver Account ID: ')
                inp3 = input('Enter Amount: ')
                output = o.transfer(inp, inp2, int(inp3))
            
            elif inp == 6: 
                exit()
            else: 
                print('Please enter valid number.\n\n')
        
            if output == 1:
                print("Success\n")
            elif output == -1:
                print("ID Not Valid\n")
            elif output == -2:
                print("Funds not available\n")
            
            
        



        

