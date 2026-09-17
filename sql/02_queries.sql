-- 5% Shareholder changes analyzer

-- Sum of stock held by each holder name, on 2 snapshot dates
WITH holder_sum AS(
	SELECT ticker, holder_name, snapshot_date, SUM(shares_held) AS total_share_held
	FROM ownership_snapshots	
	GROUP BY ticker, holder_name, snapshot_date
	ORDER BY ticker, snapshot_date
),

-- Lag of holder_sum to compare between 2 snapshot dates
holder_lag AS(
	SELECT
	    ticker, holder_name, snapshot_date, total_share_held,
		LAG(total_share_held) OVER(
			PARTITION BY ticker, holder_name ORDER BY snapshot_date) AS previous_day_share_held
	FROM holder_sum
)

-- Contains changes of share held by holder between the 2 dates
SELECT ticker, 
	holder_name, 
	snapshot_date, 
	total_share_held,
	previous_day_share_held,
	total_share_held - previous_day_share_held AS share_change
FROM holder_lag
WHERE total_share_held != previous_day_share_held 
AND share
ORDER BY share_change DESC
