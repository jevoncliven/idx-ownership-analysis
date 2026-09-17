from clean_ksei import clean_file, detect_dates
from load_database import get_connection, register_new_stocks, load_ownership_data


def run_pipeline(filepath):
    previous_date, latest_date = detect_dates(filepath)

    print(f"Detected dates: {previous_date}, {latest_date}")

    conn = get_connection()

    df = clean_file(filepath)

    register_new_stocks(df, conn)

    load_ownership_data(
        df,
        conn,
        previous_date,
        latest_date
    )


if __name__ == "__main__":
    run_pipeline("../data/idx_15sept.xlsx")