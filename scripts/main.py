from clean_ksei import clean_file, detect_dates
from load_database import get_connection, register_new_stocks, load_ownership_data, get_changes
from pathlib import Path

def run_pipeline(filepath, conn):
    previous_date, latest_date = detect_dates(filepath)

    print(f"Detected dates: {previous_date}, {latest_date}")

    df = clean_file(filepath)

    register_new_stocks(df, conn)

    load_ownership_data(
        df,
        conn,
        previous_date,
        latest_date
    )
    
    print()

def main():
    conn = get_connection()
    folder = Path("../data")

    #track succesful and failed processed files 
    loaded = []
    failed = []

    try:
        #find all the 5% changes excel files with the specified pattern
        for f in sorted(folder.glob("peng-????-??-??*.xlsx")):
            try:
                run_pipeline(f, conn)
                loaded.append(f.name)
            except Exception as e:
                conn.rollback()
                failed.append((f.name, str(e)))

        print(f"\nLoaded: {len(loaded)} | Failed: {len(failed)}")
        for name, reason in failed:
            print(f"  FAILED {name}: {reason}")

        # changes = get_changes(conn)
        # print(f"\n{len(changes)} ownership changes detected:")
        # print(changes.to_string())
    finally:
        conn.close()



if __name__ == "__main__":
    main()