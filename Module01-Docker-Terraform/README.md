# Homework

## Question 1 & 2 & 7 Answered in MCQ
## Quetions 3 - 6 Answered in MCQ and Below is the SQL Queries and homework.ipynb in Pipelines Folder.

```SQL
--QUESTION 3 in homework
SELECT COUNT(trip_distance) 
FROM public."greenData_NOV25" 
WHERE lpep_pickup_datetime >= '2025-11-01' AND lpep_pickup_datetime < '2025-12-01' AND trip_distance <= 1.00;
--answer = 8007

--QUESTION 4 in homework
SELECT lpep_pickup_datetime, trip_distance 
FROM public."greenData_NOV25" 
WHERE trip_distance < 100
ORDER BY trip_distance DESC;
--answer = 2025-11-14

--QUESTION 5 in homework
SELECT l."Zone", SUM(g."total_amount") AS total_amounts
FROM public."greenData_NOV25" AS g
INNER JOIN public."lookupData" AS l ON g."PULocationID" = l."LocationID"
WHERE g."lpep_pickup_datetime" >= '2025-11-18' AND g."lpep_pickup_datetime" < '2025-11-19'
GROUP BY l."Zone"
ORDER BY SUM(g."total_amount") DESC;
--answer = East Harlem North

--QUESTION 6 in homework
SELECT lu."Zone", MAX(gt."tip_amount") AS Largest_Tip
FROM (SELECT g."PULocationID", g."DOLocationID", g."tip_amount"
FROM public."greenData_NOV25" AS g INNER JOIN public."lookupData" AS l ON
g."PULocationID" = l."LocationID" AND l."Zone" = 'East Harlem North') AS gt
INNER JOIN public."lookupData" AS lu ON gt."DOLocationID" = lu."LocationID" 
GROUP BY lu."Zone"
ORDER BY MAX(gt."tip_amount") DESC;
--answer = Yorkville West
```

