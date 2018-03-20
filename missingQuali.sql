SELECT R.raceId, count(qualifyId)  FROM F1.races R

LEFT JOIN qualifying Q ON R.raceId = Q.raceId

GROUP BY R.raceId

ORDER BY count(qualifyId) 