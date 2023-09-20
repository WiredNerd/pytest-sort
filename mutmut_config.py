from datetime import datetime

def pre_mutation(context):
    print(f"\t{datetime.now()}\t{context.filename}:{context.current_line_index}")