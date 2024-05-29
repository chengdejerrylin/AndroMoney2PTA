import argparse
import csv
import os

def parseInput(inputFile:str, ignore_row:int):
    '''
    inputFile: str, file path
    ignore_row: int, ignore first n rows
    '''
    extension = os.path.splitext(inputFile)[1]
    
    if extension == '.csv':
        with open(inputFile, 'r') as file:
            reader = csv.reader(file)
            for _ in range(ignore_row):
                next(reader)
            yield from reader

    elif extension == '.xls' or extension == '.xlsx':
        raise NotImplementedError('Excel files are not supported yet')
    else:
        raise ValueError(f'File:{inputFile} extension ({extension}) not supported')
    
class AndroMoneyReader:
    def __init__(self, reader):
        self.reader = reader

    def __iter__(self):
        return self

    def __next__(self):
        row = next(self.reader)
        return {
            'id': row[0],
            'currency': row[1],
            'amount': row[2],
            'category': row[3],
            'sub_category': row[4],
            'date': row[5],
            'expense': row[6],
            'income': row[7],
            'remark': row[8],
            'periodic': row[9],
            'project': row[10],
            'payee': row[11],
            'uid': row[12],
            'time': row[13],
            'status': row[14],
        }
    
class LedgerWriter:
    def __init__(self, writer):
        '''
        writer: file
        '''
        self.writer = writer

    def write(self, transaction_date, payee, effective_date=None, changed_account=[], remark='', tags={}):
        '''
        transaction_date: datetime
        payee: string
        (optional) effective_date: datetime
        changed_account: [{
            account: str, 
            (optional) amount: str, 
            (optional) currency: str, 
            (optional) effective_dates: [dates, ...],
        }, ...]
        (optional) remark: string
        (optional) tags: {tag: value, ...}
        '''
        self.file.write(f'{transaction_date[0:4]}-{transaction_date[4:6]}-{transaction_date[6:8]} * {payee}\n')

        self.file.write(f'\n')
        
    
def generateLedger(reader, outputFile:str, init_date:str):
    '''
    reader: AndroMoneyReader
    outputFile: str
    init_date: str
    '''
    with open(outputFile, 'w') as file:
        for row in reader:
            assert row['status'] == '1', f'{row} has status 1'

            # if row[3] == 'SYSTEM': # Initial amount
            #     assert row[4] == 'INIT_AMOUNT', f'{row} has SYSTEM but not INIT_AMOUNT'
            #     file.write(f'{init_date[0:4]}-{init_date[4:6]}-{init_date[6:8]} * {row[4]}\n')
            # else:
            #     file.write(f'{row[5][0:4]}-{row[5][4:6]}-{row[5][6:8]} * {row[11]}\n')
            #     if row[3] == 'Transfer': # Transfer
            #         pass
            #     elif row[3] == 'Income': # Income
            #         pass
            #     else: # Expense
            #         pass

                # init_date = row[5]
            
            # file.write(f'\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse AndroMoney CSV export')
    parser.add_argument('input', type=str, help='AndroMoney file')
    parser.add_argument('--output', type=str, help='Output CSV file')
    parser.add_argument('--ignore_row', type=int, help='Ignore first n rows', default=2)
    parser.add_argument('--init_date', type=str, help='Ignore first n rows', default='20160824')
    args = parser.parse_args()

    if args.output is None:
        args.output = os.path.splitext(args.input)[0] + '.ledger'
    reader = parseInput(inputFile=args.input, ignore_row=args.ignore_row)
    reader = AndroMoneyReader(reader)
    generateLedger(reader, outputFile=args.output, init_date=args.init_date)