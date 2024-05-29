import argparse
import csv
import datetime
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
            'id': int(row[0]),
            'currency': row[1],
            'amount': row[2],
            'category': row[3],
            'sub_category': row[4],
            'date': datetime.datetime.strptime(row[5], '%Y%m%d'),
            'expense_account': row[6],
            'income_account': row[7],
            'remark': row[8],
            'periodic': row[9],
            'project': row[10],
            'payee': row[11],
            'uid': row[12],
            'time': datetime.datetime.strptime(row[13].zfill(4), '%H%M'),
            'status': int(row[14]) if row[14] != '' else None,
        }
    
class LedgerWriter:
    def __init__(self, writer, indent:int=4):
        '''
        writer: file
        '''
        self.writer = writer
        self.indent = indent

    def write(self, transaction_date, payee, effective_date=None, changed_account=[], remark='', tags={}):
        '''
        transaction_date: datetime
        payee: string
        (optional) effective_date: datetime
        changed_account: [{
            account: str, 
            (optional) amount: (number: str, currency: str), 
            (optional) effective_dates: [dates, ...],
        }, ...]
        (optional) remark: string
        (optional) tags: {tag: value, ...}
        '''
        # title
        self.writer.write(f'{transaction_date.strftime("%Y-%m-%d")}')
        if effective_date is not None:
            self.file.write(f'={effective_date.strftime("%Y-%m-%d")}')
        self.writer.write(f' * {payee}\n')

        # changed account
        for account in changed_account:
            if 'effective_dates' in account:
                raise NotImplementedError('Effective dates inside account are not supported yet')
            else:
                self.write_single_account(account['account'], account.get('amount', None))

        self.writer.write(f'\n')

    def write_single_account(self, account, amount=None, effective_date=None):
        '''
        account: str
        amount: (number: str, currency: str)
        (optional) effective_date: datetime
        '''
        self.writer.write(f'{" " * self.indent}{account}')
        if amount is not None:
            self.writer.write(f'  {amount[0]} {amount[1]}')
        if effective_date is not None:
            raise NotImplementedError('Effective dates inside account are not supported yet')
        self.writer.write(f'\n')
        
    
def generateLedger(reader, outputFile:str, init_date:str):
    '''
    reader: AndroMoneyReader
    outputFile: str
    init_date: str
    '''
    curr_date = init_date
    with open(outputFile, 'w') as file:
        writer = LedgerWriter(writer=file)
        for row in reader:
            assert row['status'] is None, f'{row} has status {row["status"]}'

            if row['category'] == 'SYSTEM': # Initial amount
                assert row['sub_category'] == 'INIT_AMOUNT', f'{row} has SYSTEM but not INIT_AMOUNT'
                transaction_date = curr_date
                payee = row['sub_category']

                if int(row['amount']) == 0:
                    continue

                changed_account = [{
                    'account': f"Asset:{row['income_account']}",
                    'amount': (row['amount'], row['currency']),
                }, {
                    'account': f"Equity:Opening Balances",
                }]
            else:
                changed_account = []
                transaction_date = row['date']
                if row['category'] == 'Transfer': # Transfer
                    payee = row['sub_category']
                elif row['category'] == 'Income': # Income
                    payee = row['payee']
                else: # Expense
                    payee = row['payee']

                curr_date = row['date']

            # write to ledger
            writer.write(transaction_date=transaction_date, payee=payee, changed_account=changed_account, remark=row['remark'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse AndroMoney CSV export')
    parser.add_argument('input', type=str, help='AndroMoney file')
    parser.add_argument('--output', type=str, help='Output CSV file')
    parser.add_argument('--ignore_row', type=int, help='Ignore first n rows', default=2)
    parser.add_argument('--init_date', type=lambda s: datetime.datetime.strptime(s, '%Y%m%d'), help='Ignore first n rows', default='20160824')
    args = parser.parse_args()

    if args.output is None:
        args.output = os.path.splitext(args.input)[0] + '.ledger'
    reader = parseInput(inputFile=args.input, ignore_row=args.ignore_row)
    reader = AndroMoneyReader(reader)
    generateLedger(reader, outputFile=args.output, init_date=args.init_date)