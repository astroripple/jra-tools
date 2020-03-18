SELECT ymd FROM kaisai
WHERE kaisaikey IN (
    SELECT kaisaikey FROM bangumi
    WHERE racekey IN (
        SELECT racekey FROM bangumi
        EXCEPT
        SELECT racekey FROM returninfo
    )
    GROUP BY kaisaikey
)
GROUP BY ymd
;