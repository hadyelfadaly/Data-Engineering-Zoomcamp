# Homework

## Questions 1 & 2 & 6 Answered in MCQ

## Questions 3 - 5 Answered in MCQ and Below is the SQL Queries

```SQL
-- Question 3
SELECT COUNT(*) FROM `production.monthly_revenue_per_locations`;
-- Answer: 12184

-- Question 4
SELECT pickup_zone
FROM `production.monthly_revenue_per_locations`
WHERE service_type = 'Green'AND EXTRACT(YEAR FROM revenue_month) = 2020
ORDER BY revenue_monthly_total_amount DESC;
-- Answer = East HArlem North

-- Question 5
SELECT SUM(total_monthly_trips)
FROM `production.monthly_revenue_per_locations`
WHERE service_type = 'Green'AND EXTRACT(YEAR FROM revenue_month) = 2019 AND EXTRACT(MONTH FROM revenue_month) = 10;
-- Answer = 384624

```